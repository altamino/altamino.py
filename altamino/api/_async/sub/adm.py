from __future__ import annotations
from altamino.api.base import SyncBaseClass
from altamino.objects import args, resp
from altamino.utils.generators import Generator


class CommunityAdminModule(SyncBaseClass):
	comId: str | int | None



	async def ban_user(self, userId: str) -> dict:
		return await (await self.req.make_async_request("POST",  f"/x{self.comId}/s/user-profile/{userId}/ban", {"timestamp": Generator.reqtime()})).json()


	async def unban_user(self, userId: str) -> dict:
		return await (await self.req.make_async_request("POST",  f"/x{self.comId}/s/user-profile/{userId}/unban", {"timestamp": Generator.reqtime()})).json()