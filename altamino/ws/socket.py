from __future__ import annotations

import ssl
import websocket
from time import sleep
from orjson import loads, dumps

from threading import Thread

from altamino.utils.generators import Generator
from altamino.utils.constants import ws_url, ws_ping_time, ws_reconnect_time
from altamino.utils import log
from altamino.ws.handler import MessageHandler
from altamino.ws.actions import SocketActions


class Socket(MessageHandler, SocketActions):

	socket_enable: bool
	deviceId: str
	userId: str | None
	sid: str | None
	language: str

	def __init__(
		self,
		socket_trace: bool = False,
		socket_daemon: bool = True,
	):
		self.socket_trace=socket_trace
		self.socket_daemon=socket_daemon

		self.socket = None
		self.active = False
		self.headers = None
		self.socket_thread = None
		self.ping_thread = None
		self.ping_payload = dumps({"t": 116, "o": {"threadChannelUserInfoList": []}})
		self.reconnect_thread = None
		websocket.enableTrace(self.socket_trace)

		MessageHandler.__init__(self)

	def ws_connect(self):
		if not self.socket_enable:return

		if self.socket:
			log.debug("[WS] Socket already running")
			return

		self._run_altamino_socket()

		self.ping_thread = Thread(target=self.ping_handler, daemon=self.socket_daemon)
		self.ping_thread.start()


	def ping_handler(self):
		log.debug("[WS] Pinger started")
		while self.socket_enable and self.socket:
			sleep(ws_ping_time)
			self.ws_send(116, o={"threadChannelUserInfoList": []})

	def reconnect_handler(self):
		log.debug("[WS] Reconnect handler started")
		while self.socket_enable and self.socket and self.active:
			sleep(ws_reconnect_time)

			if self.active:
				self.ws_disconnect()
				log.debug("[WS] Reconnecting...")
				sleep(1)
				self.ws_connect()

	def ws_run_forever(self):
		self.socket.run_forever(
			sslopt={"cert_reqs": ssl.CERT_NONE},
			skip_utf8_validation=True,
			ping_interval=ws_ping_time,
			ping_payload=self.ping_payload,
		)

	def handle_message(self, ws, data):
		try:self.call(loads(data))
		except Exception as e:
			log.critical(f"[WS] Decode error: {e}")
	
	def ws_send(self, req_t: int, **kwargs) -> None:
		"""
			send data to altamino socket
		"""

		if not self.active or self.socket is None:
			log.debug("[WS] Socket no started")
			return
		data = dumps(dict(t=req_t, **kwargs))
		log.debug(f"[WS] Sending Data : {data}")
		try:return self.socket.send(data)
		except websocket._exceptions.WebSocketConnectionClosedException:
			log.debug(f"[WS] Socket not available : {data}")


	def handle_error(self, ws, err):
		log.critical(
			"[WS] Critical error in socket/lib/your code: {}".format(
				str(err).replace("\n", "")
			)
		)

	def handle_close(self, ws, close_code, close_msg):
		log.debug(
			"[WS] Socket closed: '{} = {}'!".format(
			 close_code, close_msg
			)
		)
		self.active = False
		self.socket = None

	def _run_altamino_socket(self):
		try:
			if self.sid is None:
				return

			final = f"{self.deviceId}|{Generator.reqtime()}"

			self.headers = {
				"Accept-Encoding": "gzip, deflate, br",
				"Connection": "Upgrade",
				"AUID": self.userId,
				"NDCAUTH": f"sid={self.sid}",
				"NDCLANG": self.language,
				"NDCDEVICEID": self.deviceId,
				"NDC-MSG-SIG": Generator.signature(final),
			}

			self.socket = websocket.WebSocketApp(
				f"{ws_url}/?signbody={final.replace('|', '%7C')}",
				on_message=self.handle_message,
				header=self.headers,
				on_error=self.handle_error,
				on_close=self.handle_close,
			)

			self.active = True
			self.socket_thread = Thread(target=self.ws_run_forever, daemon=self.socket_daemon)
			self.socket_thread.start()

			if self.reconnect_thread is None:
				self.reconnect_thread = Thread(target=self.reconnect_handler)
				self.reconnect_thread.start()

			log.debug(f"[WS] Connected to {ws_url}")
		except Exception as e:
			log.critical(f"[WS]: {e}")

	def ws_disconnect(self):

		try:
			self.socket.close()
		except Exception as closeError:
			log.debug(
				"Can't close connection: {}".format(
					str(closeError).replace("\n", " ")
				)
			)

		return