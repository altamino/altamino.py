
from __future__ import annotations
from altamino.api.base import AsyncBaseClass
from altamino.objects import args, resp
from altamino import exceptions
from altamino.utils.generators import Generator

from uuid import uuid4


class CommunityUsersModule(AsyncBaseClass):
	comId: str | int | None

	async def follow(self, userId: str | list):
		"""
		Follow an User or Multiple Users.

		**Parameters**
		- userId : ID of the User or List of IDs of the Users.
		"""
		
		if isinstance(userId, str):
			return await (await self.req.make_async_request("POST", f"/x{self.comId}/s/user-profile/{userId}/member")).json()
		elif isinstance(userId, list):
			data = { "targetUidList": userId }
			return await (await self.req.make_async_request("POST", f"/x{self.comId}/s/user-profile/{self.userId}/joined", data)).json()
		else: raise exceptions.WrongType(f"userId: {type(userId)}")

	async def unfollow(self, userId: str):
		"""
		Unfollow an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return await (await self.req.make_async_request("DELETE", f"/x{self.comId}/s/user-profile/{self.userId}/member/{userId}")).json()

	async def block(self, userId: str):
		"""
		Block an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return await (await self.req.make_async_request("POST",  f"/x{self.comId}/s/block/{userId}")).json()

	async def unblock(self, userId: str):
		"""
		Unblock an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return await (await self.req.make_async_request("DELETE",  f"/x{self.comId}/s/block/{userId}")).json()


	async def get_all_users(self, type: str = args.UsersTypes.Recent, start: int = 0, size: int = 25) -> list[resp.UserProfile]:
		"""
		Get info about all members.

		**Parameters**
		- type: str
			- use ``amino.arguments.UsersTypes``
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		if type not in args.UsersTypes.all:raise exceptions.WrongType(f"type: {type} not in {args.UsersTypes.all}")
		result = await (await self.req.make_async_request("GET", f"/x{self.comId}/s/user-profile?type={type}&start={start}&size={size}")).json()["userProfileList"]
		return [resp.UserProfile(x) for x in result]


	async def get_user_info(self, userId: str) -> resp.UserProfile:
		"""
		Information of an User.

		**Parameters**
		- userId : ID of the User.
		"""
		return resp.UserProfile(await (await self.req.make_async_request("GET", f"/x{self.comId}/s/user-profile/{userId}")).json())

	async def search_users(self, nickname: str, start: int = 0, size: int = 25) -> list[resp.UserProfile]:
		"""
		Searching users by nickname.

		**Parameters**
		- nickname : user nickname
		- start : Where to start the list.
		- size : Size of the list.
		"""
		result = await (await self.req.make_async_request("GET", f"/x{self.comId}/s/user-profile?type=name&q={nickname}&start={start}&size={size}")).json()["userProfileList"]
		return [resp.UserProfile(x) for x in result]
