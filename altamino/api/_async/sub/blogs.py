from __future__ import annotations
from altamino.api.base import AsyncBaseClass
from altamino.objects import args, resp



class CommunityBlogsModule(AsyncBaseClass):
	comId: str | int | None

	async def delete_blog(self, blogId: str):
		"""
		Deleting blog.

		**Parameters**:
		- blogId: str
		"""
		return await (await self.req.make_async_request("DELETE", f"/x{self.comId}/s/blog/{blogId}")).json()

	async def delete_wiki(self, wikiId: str):
		"""
		Deleting wiki.

		**Parameters**:
		- wikiId: str
		"""
		return await (await self.req.make_async_request("DELETE", f"/x{self.comId}/s/item/{wikiId}")).json()