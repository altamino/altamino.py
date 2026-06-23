from __future__ import annotations
from altamino.api.base import SyncBaseClass
from altamino.objects import args, resp


class CommunityAdminModule(SyncBaseClass):
	comId: str | int | None



	async def ban_user(self, userId: str) -> dict:
		return await (await self.req.make_async_request("POST",  f"/x{self.comId}/s/user-profile/{userId}/ban")).json()


	async def unban_user(self, userId: str) -> dict:
		return await (await self.req.make_async_request("POST",  f"/x{self.comId}/s/user-profile/{userId}/unban")).json()