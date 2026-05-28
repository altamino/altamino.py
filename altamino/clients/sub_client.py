from typing import TYPE_CHECKING

from altamino.utils.requester import Requester

if TYPE_CHECKING:
	from altamino.clients.client import Client



class SubClient():
	comId: str | int | None = None

	def __init__(self, client: Client, comId: str | int | None = None, aminoId: str | None = None):
		self.req: Requester = client.req

		if comId: self.comId = comId
		elif aminoId:
			link = f"http://altamino.top/c/{aminoId}"
			self.comId = client.get_from_link(link).comId
		self.upload_media = client.upload_media
