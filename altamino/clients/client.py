from __future__ import annotations

from altamino.ws.socket import Socket
from altamino.utils.requester import Requester
from altamino.objects.args import ProxyConfig, ProxyPool
from altamino.utils.generators import Generator
from altamino.utils.state import ThreadSafeState
from altamino.utils import log
from altamino.clients.sub_client import SubClient
from altamino.utils import exceptions

from altamino import args, respObject

from altamino.api._sync import *


from typing import IO
from _io import BufferedReader
from mimetypes import guess_type

class Client(
	Socket,
	AuthModule,
	GlobalChatsModule,
	):

	state: ThreadSafeState

	@property
	def proxy(self) -> ProxyConfig | ProxyPool | None:
		return self.req.proxy


	def set_proxy(self, proxy: ProxyConfig | ProxyPool | None):
		self.req.proxy = proxy

	def __init__(self,
			  deviceId: str | None = None,
			  user_agent: str = "Apple iPhone16,1 iOS v15.0 Main/3.22.0",
			  accept_language: str = "en-us",
			  community_language: str = "en",
			  socket_enable: bool = True,
			  socket_error_trace: bool = False,
			  socket_daemon: bool = True,
			  proxy: ProxyConfig | ProxyPool | None = None
			  ):


		Socket.__init__(self, socket_error_trace, socket_daemon)
		self.socket_enable = socket_enable

		if deviceId is None:
			deviceId=Generator.gen_deviceId()
			log.warning(f"You didn't explicitly specify a device ID in the client.\nA new device ID was generated for you: {deviceId}.\nSave it for future use.")

		self.req = Requester(user_agent, deviceId, community_language, accept_language, proxy)
		self.state = ThreadSafeState()


	def get_community_client(self, comId: str | None = None, aminoId: str | None = None) -> SubClient:
		return SubClient(self, comId, aminoId)


	def get_from_id(self, objectId: str, objectType: int, comId: int | None = None) -> respObject.FromCode:
		"""
		Get the Object Information from the Object ID and Type.

		**Parameters**
		- objectID : ID of the Object. User ID, Blog ID, etc.
		- objectType : Type of the Object.
		- comId : ID of the Community. Use if the Object is in a Community.
		"""
		data = {
			"objectId": objectId,
			"targetCode": 1,
			"objectType": objectType,
		}

		return respObject.FromCode(self.req.make_request("POST", f"/g/{f's-x{comId}' if comId else 's'}/link-resolution", data).json())

	def get_from_link(self, link: str) -> respObject.FromCode:
		"""
		Get the Object Information from the Amino URL.

		**Parameters**
		- link : link from the Amino.
			- ``http://aminoapps.com/p/EXAMPLE``, the ``link`` is 'EXAMPLE'.
		"""
		return respObject.FromCode(self.req.make_request("GET", f"/g/s/link-resolution?q={link}").json())



	def upload_media(self, file: IO | BufferedReader, fileType: str | None = None) -> respObject.MediaObject:
		"""
        Upload file to the amino servers.

        **Parameters**
        - file : File to be uploaded.
		- fileType : image/jpg, image/png ... or None
		"""
		if fileType is None:
			fileType = guess_type(file.name)[0]
		if fileType not in args.UploadType.all: raise exceptions.SpecifyType(fileType)
		return respObject.MediaObject(self.req.make_request("POST", "/g/s/media/upload", file.read(), headers={"Content-Type":fileType}).json())
