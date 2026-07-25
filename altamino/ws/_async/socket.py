from __future__ import annotations

from aiohttp import (
	ClientSession,
	WSMsgType,
	ClientWebSocketResponse,
	ClientConnectionError,
	WSServerHandshakeError,
	ClientTimeout,
)
from asyncio import create_task, CancelledError
from asyncio import sleep as asleep
from orjson import loads
import asyncio

from altamino.utils import log
from altamino.utils.generators import Generator, WSIdGenerator
from altamino.utils.constants import ws_url, ws_ping_time
from altamino.ws._async.handler import MessageHandler
from altamino.ws._async.actions import SocketActions
from altamino.objects.args import ProxyConfig, ProxyPool, ProxyType, ProxyUsage
from altamino.utils.requester import resolve_proxy


class Socket(MessageHandler, SocketActions):
	"""
	Module for working with the altamino socket in real time.
	Not used separately from the client.
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
		self.task_supervisor = None
		self.ws_client_session = None

		self._id_gen = WSIdGenerator()

		MessageHandler.__init__(self)

	# ------------------------------------------------------------------ #
	#  Public entry points
	# ------------------------------------------------------------------ #

	async def ws_connect(self):
		"""
		Start the socket. Idempotent: only spins up the supervisor once.
		The supervisor then owns the connection lifecycle and keeps it alive.
		"""
		if not self.socket_enable:
			log.debug("[WS] socket disabled, not connecting")
			return

		if not self.sid:
			log.debug("[WS] no sid, not connecting")
			return

		if self.task_supervisor and not self.task_supervisor.done():
			log.debug("[WS] supervisor already running")
			return

		self.task_supervisor = create_task(self._supervisor())

	async def ws_disconnect(self):
		"""Fully stop the socket and prevent the supervisor from reopening it."""
		log.debug("[WS] Closing socket...")
		self.socket_enable = False

		if self.task_supervisor:
			self.task_supervisor.cancel()
			self.task_supervisor = None

		await self._teardown_tasks()
		await self._teardown_connection()
		await self._teardown_session()

		log.debug("[WS] Socket closed")

	async def socket_wait(self):
		"""
		Keep the program alive while the socket runs in the background.

		Example:
			await client.socket_wait()
		"""
		try:
			while self.socket_enable:
				await asleep(3)
		except CancelledError:
			log.debug("[ws][socket_wait] Socket wait cancelled")
			await self.ws_disconnect()

	async def _supervisor(self):
		"""Owns the connection lifecycle. Reconnects forever with backoff."""
		backoff = 1
		max_backoff = 60

		log.debug("[WS] supervisor started")
		try:
			while self.socket_enable:
				if self.connection is not None:
					await asleep(2)
					continue

				try:
					await self._open_connection()
					backoff = 1
					log.debug("[WS] Socket started successfully")
				except CancelledError:
					raise
				except Exception as e:
					log.error(f"[WS] connect failed: {e}; retry in {backoff}s")
					await self._teardown_session()
					await asleep(backoff)
					backoff = min(backoff * 2, max_backoff)
					continue

				while self.socket_enable and self.connection is not None:
					await asleep(2)

				if self.socket_enable:
					log.debug("[WS] connection dropped, will reconnect")
		except CancelledError:
			log.debug("[WS] supervisor cancelled")
		finally:
			log.debug("[WS] supervisor stopped")

	async def _open_connection(self):
		"""Single attempt to establish the WS connection. Raises on failure."""
		await self._teardown_session()

		_proxy = resolve_proxy(self.proxy, ProxyUsage.WS)
		connector = None
		proxy_url = None

		if _proxy:
			if _proxy.proxy_type == ProxyType.HTTP:
				proxy_url = _proxy.for_aiohttp(True)
			else:
				connector = _proxy.for_aiohttp_connector()

		log.debug(
			f"[WS] connecting to {ws_url} "
			f"(proxy: {_proxy.url if _proxy else 'No proxy'})..."
		)

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

		self.ws_client_session = ClientSession(
			connector=connector,
			base_url=ws_url,
			headers=headers,
			timeout=ClientTimeout(total=20, connect=15, sock_connect=10, sock_read=15),
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

		if not self.task_receiver or self.task_receiver.done():
			self.task_receiver = create_task(self.ws_resolve())
		if not self.task_pinger or self.task_pinger.done():
			self.task_pinger = create_task(self.__pinger())

	async def ws_resolve(self):
		"""
		Read loop
		"""
		try:
			while True:
				if self.connection is None:
					return

				try:
					msg = await asyncio.wait_for(
						self.connection.receive(),
						timeout=35,
					)
				except asyncio.TimeoutError:
					log.debug("[WS][receive] Timeout, marking connection dead")
					self.connection = None
					return
				except CancelledError:
					log.debug("[WS][receive] Task cancelled")
					return
				except (WSServerHandshakeError, ClientConnectionError) as e:
					log.debug(f"[WS][receive] Connection error: {e}")
					self.connection = None
					return
				except Exception as e:
					log.error(f"[WS][receive] Unexpected error: {e}")
					self.connection = None
					return

				if msg.type == WSMsgType.TEXT:
					try:
						data = loads(msg.data)
					except Exception as e:
						log.debug(f"[WS][receive] Failed to parse message: {e}")
						continue

					log.debug(f"[WS][receive]: {data}")
					try:
						await self.call(data)
					except Exception as e:
						log.error(f"[WS][receive] handler error: {e}")
					continue

				if msg.type in (WSMsgType.CLOSED, WSMsgType.CLOSING, WSMsgType.ERROR):
					log.debug(f"[WS][receive] socket closed: {msg.type}")
					self.connection = None
					return

		except CancelledError:
			log.debug("[WS][receive] Task cancelled")
			return


	async def __pinger(self):
		log.debug("[WS] pinger started")
		try:
			while self.socket_enable and self.connection is not None:
				try:
					await self.ws_send(
						116,
						o={"threadChannelUserInfoList": [], "id": self._id_gen.next()},
					)
				except CancelledError:
					raise
				except Exception as e:
					log.debug(f"[WS] Ping error: {e}")
				await asleep(ws_ping_time)
		except CancelledError:
			log.debug("[WS] pinger cancelled")
			return
		log.debug("[WS] pinger stopped")


	async def ws_send(self, req_t: int, **kwargs):
		"""Send a message to the websocket. On failure marks the connection dead."""
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
			self.connection = None


	async def _teardown_tasks(self):
		for attr in ("task_receiver", "task_pinger"):
			task = getattr(self, attr, None)
			if task:
				task.cancel()
				setattr(self, attr, None)

	async def _teardown_connection(self):
		if self.connection:
			log.debug("[WS] Closing connection...")
			try:
				await asyncio.wait_for(self.connection.close(), timeout=3.0)
			except Exception as e:
				log.debug(f"[WS] Error closing connection: {e}")
			self.connection = None

	async def _teardown_session(self):
		if self.ws_client_session:
			log.debug("[WS] Closing session...")
			try:
				await asyncio.wait_for(self.ws_client_session.close(), timeout=5.0)
			except Exception as e:
				log.debug(f"[WS] Error closing session: {e}")
			self.ws_client_session = None


	async def reconnect(self):
		"""
		Force a reconnect: drop the current connection and let the supervisor
		bring it back. Safe to call from anywhere.
		"""
		log.debug("[WS] forced reconnect requested")
		await self._teardown_tasks()
		await self._teardown_connection()
		await self._teardown_session()

		if self.socket_enable and (not self.task_supervisor or self.task_supervisor.done()):
			self.task_supervisor = create_task(self._supervisor())