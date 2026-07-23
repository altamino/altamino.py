from altamino.utils import log
from altamino.objects.args import wsEvent, ws_message_methods, ws_chat_action_end, ws_chat_action_start, ws_message_types, notification_types
from altamino.objects.resp import Event

from altamino.ws import MiddlewareStopException
from altamino.ws._async.router import AsyncRouter


class MessageHandler(AsyncRouter):
	"""Dispatches incoming socket events to registered handlers"""

	def __init__(self):
		super().__init__()


	async def call(self, data: dict) -> None:
		"""
		call the event handler

		**parameters**
		- data : data from web socket
		"""
		if data.get("o") is None:return
		data_object = Event(data["o"], self)
		method = ws_message_methods.get(data["t"])
		if method in ("chat_action_start", "chat_action_end") :
			key = data['o'].get('actions', 0)
			ws_event = ws_chat_action_start.get(key) if method == "chat_action_start" else ws_chat_action_end.get(key)
		elif method == "chat_message":
			key = f"{data['o']['chatMessage']['type']}:{data['o']['chatMessage'].get('mediaType', 0)}"
			ws_event = ws_message_types.get(key)
		elif method == "notification":
			key = data["o"]["payload"]["notifType"]
			ws_event = notification_types.get(key)
		else:
			key = "unknown"
			ws_event="unknown"
		

		try:
			await self._run_middlewares(data_object, ws_event, key, method)
		except MiddlewareStopException:
			log.debug(f"[ws][middleware] Event {ws_event} stopped by middleware")
			return
		for key in (wsEvent.ANY, ws_event, key, method):
			if key not in self.handlers:
				continue
			for func in self.handlers[key]:
				try:
					await func(data_object)
				except Exception as e:
					log.error(f"[ws][event][{func}] Error: {e}")



	async def _run_middlewares(self, data, ws_event, key, method):
		middlewares_to_run = []

		for key in (wsEvent.ANY, ws_event, key, method):
			if key and key in self.middlewares:
				middlewares_to_run.extend(self.middlewares[key])

		for middleware in middlewares_to_run:
			try:
				result = await middleware(data)
				if result is False:
					raise MiddlewareStopException()
			except MiddlewareStopException:
				raise
			except Exception as e:
				log.error(f"[WS][middleware][{middleware}] Error: {e}")