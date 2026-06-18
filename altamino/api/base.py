from __future__ import annotations

from altamino.utils.requester import Requester
from altamino.utils.generators import Generator
from altamino import respObject

from typing import IO
from _io import BufferedReader
from aiofiles.threadpool.binary import AsyncBufferedReader


class Base():
	req: Requester
	socket_enable: bool
	me: respObject.AuthData = respObject.AuthData({})

	@property
	def deviceId(self) -> str:
		return self.req.deviceId

	@property
	def userId(self) -> str | None:
		return self.req.userId

	@property
	def sid(self) -> str | None:
		return self.req.sid

	@property
	def user_agent(self) -> str:
		return self.req.user_agent

	@property
	def language(self) -> str:
		return self.req.language


	def set_device(self, deviceId: str) -> None:
		self.req.deviceId = deviceId

	def update_device(self) -> None:
		if self.req.deviceId: self.req.deviceId = Generator.update_deviceId(self.req.deviceId)

	def set_language(self, language: str) -> None:
		self.req.language = language

	def set_user_agent(self, user_agent: str) -> None:
		self.req.user_agent = user_agent

	def set_userId(self, userId: str | None) -> None:
		self.req.userId = userId

	def set_sid(self, sid: str | None) -> None:
		self.req.sid = sid



class AsyncBaseClass(Base):
	async def upload_media(self, file: IO | BufferedReader | AsyncBufferedReader, fileType: str | None = None) -> respObject.MediaObject: ...
	async def ws_disconnect() -> None: ...
	async def ws_connect() -> None: ...


class SyncBaseClass(Base):
	def upload_media(self, file: IO | BufferedReader, fileType: str | None = None) -> respObject.MediaObject: ...
	def ws_disconnect() -> None: ...
	def ws_connect() -> None: ...