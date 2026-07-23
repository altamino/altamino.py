from __future__ import annotations
from altamino.api.base import AsyncBaseClass
from altamino.objects.resp import Community, BaseObject

class GlobalCommunitiesModule(AsyncBaseClass):

	async def get_joined_communities(self, start: int = 0, size: int = 25) -> list[Community]:
		"""
		List of Communities the account is in.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.
		"""
		result = await (await self.req.make_async_request("GET", f"/g/s/community/joined?v=1&start={start}&size={size}")).json()
		return [Community({"community": x}) for x in result.get("communityList", [])]


	async def get_community_info(self, comId: int) -> Community:
		"""
		Information of an Community.

		**Parameters**
		- comId : ID of the Community.
		"""
		return Community(await(await self.req.make_async_request("GET", f"/g/s-x{comId}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount")).json())



	async def join_community(self, comId: int, invitationId: str | None = None) -> BaseObject:
		"""
		Join a Community.

		**Parameters**
		- comId : ID of the Community.
		- invitationId : ID of the Invitation Code.
		"""
		
		data = {"uid": self.userId}
		if invitationId:data["invitationId"] = invitationId
		return BaseObject(await (await self.req.make_async_request("POST", f"/x{comId}/s/community/join", data)).json())

	async def request_join_community(self, comId: int, message: str = "") -> BaseObject:
		"""
		Request to join a Community.

		**Parameters**
		- comId : ID of the Community.
		- message : Message to be sent.
		"""
		return BaseObject(await (await self.req.make_async_request("POST", f"/x{comId}/s/community/membership-request", {"message": message, "uid": self.userId})).json())

	async def leave_community(self, comId: int) -> BaseObject:
		"""
		Leave a Community.

		**Parameters**
		- comId : ID of the Community.
		"""
		return BaseObject(await (await self.req.make_async_request("POST", f"/x{comId}/s/community/leave").json()))