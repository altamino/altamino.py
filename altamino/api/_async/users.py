
from __future__ import annotations
from altamino.api.base import AsyncBaseClass



class GlobalUsersModule(AsyncBaseClass):



	async def follow(self, userId: str):
		"""
		Follow an User.

		**Parameters**
		- userId : ID of the User.
		"""
		
		return await (await self.req.make_async_request("POST", f"/g/s/user-profile/{userId}/member")).json()

	async def unfollow(self, userId: str):
		"""
		Unfollow an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return await (await self.req.make_async_request("DELETE", f"/g/s/user-profile/{self.userId}/member/{userId}")).json()
