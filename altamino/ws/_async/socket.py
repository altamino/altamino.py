from __future__ import annotations

from aiohttp import ClientSession, WSMsgType, ClientWebSocketResponse, ClientConnectionError, WSServerHandshakeError, ClientTimeout
from asyncio import create_task, CancelledError
from asyncio import sleep as asleep
from orjson import loads
import asyncio

from altamino.utils import log
from altamino.utils.generators import Generator
from altamino.utils.constants import ws_url, ws_ping_time
from altamino.ws._async.handler import MessageHandler
from altamino.ws._async.actions import SocketActions
from altamino.objects.args import ProxyConfig, ProxyPool, ProxyType, ProxyUsage
from altamino.utils.requester import resolve_proxy

class Socket(MessageHandler, SocketActions):

	"""
	Module for working with kyodo socket in real time. Not used separately from the client.
	"""

	socket_enable: bool
	deviceId: str
	userId: str | None
	sid: str | None
	language: str

	proxy: ProxyConfig | ProxyPool

	connection: ClientWebSocketResponse = None

	def __init__(self):
		self.task_receiver = None
		self.task_pinger = None
		self.ws_client_session = None

		MessageHandler.__init__(self)
	

	async def ws_on_close(self, code: int, reason: str) -> None:
		log.debug("[WS] Closed with code %s and reason %s", code, reason)
		self.connection = None

		if self.task_receiver:
			self.task_receiver.cancel()
		if self.task_pinger:
			self.task_pinger.cancel()


	async def ws_resolve(self):
		retry_count = 0
		max_retries = 5
		
		while True:
			try:
				if self.connection is None:
					await asleep(1)
					continue
				
				retry_count = 0 
					
				try:
					msg = await asyncio.wait_for(
						self.connection.receive(), 
						timeout=35
					)
				except asyncio.TimeoutError:
					log.debug("[WS][receive] Timeout, attempting reconnect...")
					await self.reconnect()
					continue
				except CancelledError:
					log.debug("[WS][receive] Task cancelled")
					return
					
				if msg.type != WSMsgType.TEXT:
					continue
					
				try:
					data = loads(msg.data)
				except Exception as e:
					log.debug(f"[WS][receive] Failed to parse message: {e}")
					continue

				log.debug(f"[WS][receive]: {data}")
				await self.call(data)
				
			except (WSServerHandshakeError, ClientConnectionError) as e:
				log.debug(f"[WS][receive] Connection error: {e}")
				retry_count += 1
				if retry_count > max_retries:
					log.error("[ws][receive] Max retries exceeded")
					return
				await self.reconnect()
				continue
			except CancelledError:
				log.debug("[WS]][receive] Task cancelled")
				return
			except Exception as e:
				log.error(f"[WS][receive] Unexpected error: {e}")
				retry_count += 1
				if retry_count > max_retries:
					log.error("[WS][receive] Max retries exceeded")
					return
				await self.reconnect()
				continue

	async def ws_connect(self):
		"""Connect to web socket"""
		if self.connection:
			log.debug("[WS] Socket already running")
			return

		if not self.sid:
			return

		if self.ws_client_session:
			try:
				log.debug("[WS] Closing old session...")
				await asyncio.wait_for(self.ws_client_session.close(), timeout=5)
			except Exception:
				pass
			self.ws_client_session = None

		_proxy = resolve_proxy(self.proxy, ProxyUsage.WS)
		connector = None
		proxy_url = None

		if _proxy:
			if _proxy.proxy_type == ProxyType.HTTP:
				proxy_url = _proxy.for_aiohttp(True)
			else:
				connector = _proxy.for_aiohttp_connector()
		log.debug(f"[WS] connecting to {ws_url} (proxy: {_proxy.url if _proxy else 'No proxy'})...")

		final = f"{self.deviceId}|{Generator.reqtime()}"
		headers = {
			"Accept-Encoding": "gzip, deflate, br",
			"Connection": "Upgrade",
			"AUID": self.userId,
			"NDCAUTH": f"sid={self.sid}",
			"NDCLANG": self.language,
			"NDCDEVICEID": self.deviceId,
			"NDC-MSG-SIG": Generator.signature(final),
		}


		try:

			self.ws_client_session = ClientSession(
				connector=connector,
				base_url=ws_url,
				headers=headers,
				timeout=ClientTimeout(total=20, connect=15, sock_connect=10, sock_read=15)
			)
			self.connection = await asyncio.wait_for(
				self.ws_client_session.ws_connect(
					f"/?signbody={final.replace('|', '%7C')}",
					proxy=proxy_url,
					heartbeat=ws_ping_time,
					autoclose=True,
				),
				timeout=20,
			)
			if not self.task_receiver:
				self.task_receiver = create_task(self.ws_resolve())
			if not self.task_pinger:
				self.task_pinger = create_task(self.__pinger())
			log.debug("[WS] Socket started successfully")

		except (asyncio.TimeoutError, Exception) as e:
			self.connection = None
			if self.ws_client_session:
				try:
					await asyncio.wait_for(self.ws_client_session.close(), timeout=5)
				except Exception:
					pass
				self.ws_client_session = None
			if isinstance(e, asyncio.TimeoutError):
				log.error("[WS] WebSocket connection timeout")
			else:
				log.error(f"[WS] Error starting socket: {e}")


	async def ws_disconnect(self):
		"""Disconnect from websocket"""
		log.debug("[WS] Closing socket...")
		
		if self.connection:
			log.debug("[WS] Closing connection...")
			try:
				await asyncio.wait_for(self.connection.close(), timeout=3.0)
			except Exception as e:
				log.debug(f"[WS] Error closing connection: {e}")
			self.connection = None
		
		if self.ws_client_session:
			log.debug("[WS] Closing session...")
			try:
				await asyncio.wait_for(self.ws_client_session.close(), timeout=3.0)
			except Exception as e:
				log.debug(f"[WS] Error closing session: {e}")
			self.ws_client_session = None
		
		log.debug("[WS] Socket closed")


	async def reconnect(self):
		log.debug("[WS] Socket reconnecting...")
		await self.ws_disconnect()
		await asleep(2)
		try:
			await asyncio.wait_for(self.ws_connect(), timeout=25)
		except asyncio.TimeoutError:
			log.error("[WS] Reconnection timeout")
		except Exception as e:
			log.error(f"[WS] Reconnection failed: {e}")


	async def __pinger(self):
		log.debug(f"[WS] started.")
		while self.socket_enable and self.connection:
			try:
				if self.connection:
					await self.ws_send(116, o={"threadChannelUserInfoList": []})
					await asleep(ws_ping_time)
			except Exception as e:
				log.debug(f"[WS] Ping error: {e}")
				await asleep(2)


	async def ws_send(self, req_t: int, **kwargs):
		"""Send message to websocket"""
		if self.connection is None:
			log.debug("[WS] Socket not running")
			return
		
		try:
			data = dict(t=req_t, **kwargs)
			log.debug(f"[WS] Sending Data : {data}")
			await self.connection.send_json(data)
		except CancelledError:
			raise
		except Exception as e:
			log.debug(f"[ws][send] Error sending message: {e}")
			await self.reconnect()


	async def socket_wait(self):
		"""
		Starts a loop that continuously listens for new messages from the WebSocket connection.
		
		This method is used to keep the program running and process incoming messages in real-time. 
		It ensures that the WebSocket connection remains open, and the program doesn't exit unexpectedly while 
		awaiting messages. 

		The loop will run as long as `self.socket_enable` is True. The method sleeps for 3 seconds between 
		iterations to prevent unnecessary CPU usage while waiting for new data.

		Example:
			await client.socket_wait()
		"""
		try:
			while self.socket_enable:
				await asleep(3)
		except CancelledError:
			log.debug("[ws][socket_wait] Socket wait cancelled")
			await self.ws_disconnect()