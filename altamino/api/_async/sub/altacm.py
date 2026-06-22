from __future__ import annotations
from altamino.api.base import SyncBaseClass
from altamino.objects import args, resp


class AltACMModule(SyncBaseClass):
	comId: str | int | None
	

	async def create_community(self, name, aminoId, agentGlobalLink, lang) -> dict:

		data = {
			"name": name,
			"aminoId": aminoId,
			"agentGlobalLink": agentGlobalLink,
			"lang": lang
		}
		
		return await (await self.req.make_async_request("POST",  f"/altacm/s/community/create", data)).json()



	async def edit_community(self, name, aminoId, agentGlobalLink, lang) -> dict:

		data = {
			"name": name,
			"aminoId": aminoId,
			"agentGlobalLink": agentGlobalLink,
			"lang": lang
		}
		
		return await (await self.req.make_async_request("POST",  f"/altacm/s/community/x{self.comId}/edit", data)).json()

