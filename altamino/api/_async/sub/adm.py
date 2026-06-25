from __future__ import annotations
from altamino.api.base import AsyncBaseClass
from altamino.objects import args, resp
from altamino import exceptions
from altamino.utils.generators import Generator


class CommunityAdminModule(AsyncBaseClass):
	comId: str | int | None



	async def ban_user(self, userId: str) -> dict:
		return await (await self.req.make_async_request("POST",  f"/x{self.comId}/s/user-profile/{userId}/ban", {"timestamp": Generator.reqtime()})).json()


	async def unban_user(self, userId: str) -> dict:
		return await (await self.req.make_async_request("POST",  f"/x{self.comId}/s/user-profile/{userId}/unban", {"timestamp": Generator.reqtime()})).json()
	

	async def create_wiki_category(self, title: str, parentCategoryId: str, content: str | None = None, media: list | None = None, comId: str | int | None = None):
		"""
		Create wiki category.

		**Parameters**
		- title: category title
		- parentCategoryId: parent category id
		- content: text
		- media: media list
			- idk, looks like a trash. i will remake it.
		"""
		data = {
			"icon": None,
			"content": content,
			"label": title,
			"mediaList": media,
			"parentCategoryId": parentCategoryId,
		}
		return await (await self.req.make_async_request("POST", f"/x{comId or self.comId}/s/item-category", data)).json()
		
	async def create_shared_folder(self,title: str, comId: str | int | None = None):
		"""
		Create shared folder.

		**Parameters**
		- title: folder title
		"""
		data = { "title": title }
		return await (await self.req.make_async_request("POST", f"/x{comId or self.comId}/s/shared-folder/folders", data)).json()

	async def submit_to_wiki(self, wikiId: str, message: str, comId: str | int | None = None):
		"""
		Submit wiki to curator review.

		**Parameters**
		- wikiId: wiki id
		- message: text 
		"""
		
		data = {
			"message": message,
			"itemId": wikiId
		}
		return await (await self.req.make_async_request("POST", f"/x{comId or self.comId}/s/knowledge-base-request", data)).json()

	async def accept_wiki_request(self, requestId: str, destinationCategoryIdList: list, comId: str | int | None = None):
		"""
		Accept wiki.

		**Parameters**
		- requestId: request Id
		- destinationCategoryIdList: Category id List
		"""
		data = {
			"destinationCategoryIdList": destinationCategoryIdList,
			"actionType": "create"
		}

		return await (await self.req.make_async_request("POST", f"/x{comId or self.comId}/s/knowledge-base-request/{requestId}/approve", data)).json()

	async def reject_wiki_request(self, requestId: str, comId: str | int | None = None):
		"""
		Reject wiki.

		**Parameters**
		- requestId: request Id
		"""
		data = {}
		return await (await self.req.make_async_request("POST", f"/x{comId or self.comId}/s/knowledge-base-request/{requestId}/reject", data)).json()

	async def get_wiki_submissions(self, start: int = 0, size: int = 25, comId: str | int | None = None):
		"""
		Get wiki submissions to be approved.

		**Parameters**
		- start: int = 0
			- start pos
		- size: int = 25
			- how much you want to get
		"""
		return await (await self.req.make_async_request("GET", f"/x{comId or self.comId}/s/knowledge-base-request?type=all&start={start}&size={size}")).json()["knowledgeBaseRequestList"]



	async def moderation_history(self, userId: str | None = None, blogId: str | None = None, wikiId: str | None = None, quizId: str | None = None, fileId: str | None = None, size: int = 25, comId: str | int | None = None):
		"""
		Getting moderation history of object.

		**Parameters**
		- userId: user Id
		- blogId: blog Id
		- wikiId: wiki Id
		- quizId: quiz Id
		- fileId: file Id
			- can be only one field
			- if all fields are None, getting all latest operations in "shared" moderation history
		- size: int = 25
			- how much you want to get
		"""
		object_types = {
			'userId': {'id': userId, 'type': 0},
			'blogId': {'id': blogId, 'type': 1},
			'wikiId': {'id': wikiId, 'type': 2},
			'quizId': {'id': quizId, 'type': 1},
			'fileId': {'id': fileId, 'type': 109}
		}

		for key, value in object_types.items():
			if value['id']:
				url = f"/x{comId or self.comId}/s/admin/operation?objectId={value['id']}&objectType={value['type']}&pagingType=t&size={size}"
				break
		else:
			url = f"/x{comId or self.comId}/s/admin/operation?pagingType=t&size={size}"
		return await (await self.req.make_async_request("GET", url)).json()["adminLogList"]

	async def feature(self, days: int = args.FeatureDays.ONE_DAY, userId: str | None = None, chatId: str | None = None, blogId: str | None = None, wikiId: str | None = None, comId: str | int | None = None):
		"""
		Feature object.

		**Parameters**
		- days: feature days
		- userId: user Id
		- blogId: blog Id
		- wikiId: wiki Id
		- quizId: quiz Id
			- can be only one field
		"""
		times: dict = {
			"chatId": {
				1: 3600,
				2: 7200,
				3: 10800
			},
			"ect": {
				1: 86400,
				2: 172800,
				3: 259200,
			}
		}
		if days not in times[chatId].keys(): raise exceptions.WrongType(days)

		data = {
			"adminOpName": 114,
			"adminOpValue": {
				"featuredDuration": times["chatId" if chatId else "ect"][days]
			}
		}

		if userId:
			data["adminOpValue"] = {"featuredType": 4}
			url = f"/x{comId or self.comId}/s/user-profile/{userId}/admin"
		elif blogId:
			data["adminOpValue"] = {"featuredType": 1}
			url = f"/x{comId or self.comId}/s/blog/{blogId}/admin"
		elif wikiId:
			data["adminOpValue"] = {"featuredType": 1}
			url = f"/x{comId or self.comId}/s/item/{wikiId}/admin"
		elif chatId:
			data["adminOpValue"] = {"featuredType": 5}
			url = f"/x{comId or self.comId}/s/chat/thread/{chatId}/admin"
		else: raise exceptions.SpecifyType

		return await (await self.req.make_async_request("POST", url, data)).json()

	async def unfeature(self, userId: str | None = None, chatId: str | None = None, blogId: str | None = None, wikiId: str | None = None, comId: str | int | None = None):
		"""
		Unfeature object.

		**Parameters**
		- userId: user Id
		- blogId: blog Id
		- wikiId: wiki Id
		- quizId: quiz Id
			- can be only one field
		"""
		data = {
			"adminOpName": 114,
			"adminOpValue": {"featuredType": 0}
		}

		if userId:
			url = f"/x{comId or self.comId}/s/user-profile/{userId}/admin"
		elif blogId:
			url = f"/x{comId or self.comId}/s/blog/{blogId}/admin"
		elif wikiId:
			url = f"/x{comId or self.comId}/s/item/{wikiId}/admin"
		elif chatId:
			url = f"/x{comId or self.comId}/s/chat/thread/{chatId}/admin"
		else: raise exceptions.SpecifyType

		return await (await self.req.make_async_request("POST", url, data)).json()

	async def hide(self, userId: str | None = None, chatId: str | None = None, blogId: str | None = None, wikiId: str | None = None, quizId: str | None = None, fileId: str | None = None, reason: str | None = None, comId: str | int | None = None):
		"""
		Hide object.

		**Parameters**
		- userId: user Id
		- blogId: blog Id
		- wikiId: wiki Id
		- quizId: quiz Id
		- fileId: file Id
			- can be only one field
		- reason: hide reason
		"""
		
		data = {
			"adminOpName": 110,
			"adminOpNote": {
				"content": reason,
			}
		}
		if userId is None:
			data["adminOpValue"] = 9

		if userId:
			data["adminOpName"] = 18
			url = f"/x{comId or self.comId}/s/user-profile/{userId}/admin"
		elif blogId:
			url = f"/x{comId or self.comId}/s/blog/{blogId}/admin"
		elif quizId:
			url = f"/x{comId or self.comId}/s/blog/{quizId}/admin"
		elif wikiId:
			url = f"/x{comId or self.comId}/s/item/{wikiId}/admin"
		elif chatId:
			url = f"/x{comId or self.comId}/s/chat/thread/{chatId}/admin"
		elif fileId:
			url = f"/x{comId or self.comId}/s/shared-folder/files/{fileId}/admin"
		else: raise exceptions.SpecifyType

		return await (await self.req.make_async_request("POST", url, data)).json()

	async def unhide(self, userId: str | None = None, chatId: str | None = None, blogId: str | None = None, wikiId: str | None = None, quizId: str | None = None, fileId: str | None = None, reason: str | None = None, comId: str | int | None = None):
		"""
		unhide object.

		**Parameters**
		- userId: user Id
		- blogId: blog Id
		- wikiId: wiki Id
		- quizId: quiz Id
		- fileId: file Id
			- can be only one field
		- reason: unhide reason
		"""

		data = {
			"adminOpName": 110,
			"adminOpNote": {
				"content": reason
			}
		}
		if userId is None:
			data["adminOpValue"] = 0

		if userId:
			data["adminOpName"] = 19
			url = f"/x{comId or self.comId}/s/user-profile/{userId}/admin"
		elif blogId:
			url = f"/x{comId or self.comId}/s/blog/{blogId}/admin"
		elif quizId:
			url = f"/x{comId or self.comId}/s/blog/{quizId}/admin"
		elif wikiId:
			url = f"/x{comId or self.comId}/s/item/{wikiId}/admin"
		elif chatId:
			url = f"/x{comId or self.comId}/s/chat/thread/{chatId}/admin"
		elif fileId:
			url = f"/x{comId or self.comId}/s/shared-folder/files/{fileId}/admin"
		else: raise exceptions.SpecifyType

		return await (await self.req.make_async_request("POST", url, data)).json()

	async def edit_titles(self, userId: str, titles: list[dict], comId: str | int | None = None):
		"""
		Edit user's titles.

		**Parameters**
		- userId: user id
		- titles: list of titles

		- example: 
		[
			{"title": "#00FF00"},
			{"cute girl": "#FFC0CB"}
		]

		titles = [{"title name": "title color"}]
		"""

		tlt = list()
		for title  in titles:
			for title, color in title.items():
				tlt.append(
					{"title": title, "color": color}
				)
		data = {
			"adminOpName": 207,
			"adminOpValue": {
				"titles": tlt
			}
		}

		return await (await self.req.make_async_request("POST", f"/x{comId or self.comId}/s/user-profile/{userId}/admin", data)).json()

	
	async def warn(self, userId: str, reason: str | None = None, comId: str | int | None = None):
		"""
		Give a warn to user.

		**Parameters**
		- userId: user Id
		- reason: warn reason
		"""
		data = {
			"uid": userId,
			"title": "Custom",
			"content": reason,
			"attachedObject": {
				"objectId": userId,
				"objectType": 0
			},
			"penaltyType": 0,
			"adminOpNote": {},
			"noticeType": 7
		}

		return await (await self.req.make_async_request("POST", f"/x{comId or self.comId}/s/notice", data)).json()


	async def get_strike_templates(self, comId: str | int | None = None):
		"""
		get strike templates
		"""
		return await (await self.req.make_async_request("GET", f"/x{comId or self.comId}/s/notice/message-template/strike")).json()

	async def get_warn_templates(self, comId: str | int | None = None):
		"""
		get warn templates
		"""
		return await (await self.req.make_async_request("GET", f"/x{comId or self.comId}/s/notice/message-template/warning")).json()


	async def strike(self, userId: str, time: int = args.StrikeTime.ONE_HOUR, title: str | None = None, reason: str | None = None, comId: str | int | None = None):
		"""
		Give a strike (warn + read only mode) to user.

		**Parameters**
		- userId: str
		- title: strike title
		- reason: strike reason
		- time: 
			- time == 1 is 1 hour
			- time == 2 is 3 hours
			- time == 3 is 6 hours
			- time == 4 is 12 hours
			- time == 5 is 24 hours
				- use ``amino.arguments.StrikeTime``
		"""

		times = {
			1: 86400,
			2: 10800,
			3: 21600,
			4: 43200,
			5: 86400
		}
		if time not in times.keys():raise exceptions.WrongType(time)

		data = {
			"uid": userId,
			"title": title,
			"content": reason,
			"attachedObject": {
				"objectId": userId,
				"objectType": 0
			},
			"penaltyType": 1,
			"penaltyValue": times[time],
			"adminOpNote": {},
			"noticeType": 4
		}
		return await (await self.req.make_async_request("POST", f"/x{comId or self.comId}/s/notice", data)).json()
