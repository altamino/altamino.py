from __future__ import annotations
from altamino.api.base import AsyncBaseClass
from altamino.objects import args, resp

class GlobalChatsModule(AsyncBaseClass):

	async def get_my_chats(self, start: int = 0, size: int = 25) -> list[resp.Chat]:
		"""
		List of Chats the account is in.

		**Parameters**
		- start : Where to start the list.
		- size : Size of the list.

		"""
		result = await (await self.req.make_async_request("GET", f"/g/s/chat/thread?type=joined-me&start={start}&size={size}")).json()["threadList"]
		return [resp.Chat(x) for x in result]


	async def get_chat(self, chatId: str) -> resp.Chat:
		"""
		Get the Chat Object from an Chat ID.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return resp.Chat(await (await self.req.make_async_request("GET", f"/g/s/chat/thread/{chatId}")).json())

	async def get_chat_users(self, chatId: str, start: int = 0, size: int = 25) -> list[resp.UserProfile]:
		"""
		Getting users in chat. 

		**Parameters**:
		- chatId : ID of the Chat.
		- start : Where to start the list.
		- size : Size of the list.
		"""
		result = await (await self.req.make_async_request("GET", f"/g/s/chat/thread/{chatId}/member?cv=1.2&type=default&start={start}&size={size}")).json()["memberList"]
		return [resp.UserProfile(x) for x in result]


	async def join_chat(self, chatId: str) -> resp.BaseObject:
		"""
		Join an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return resp.BaseObject(await (await self.req.make_async_request("POST", f"/g/s/chat/thread/{chatId}/member/{self.userId}", content_type="application/x-www-form-urlencoded")).json())

	async def leave_chat(self, chatId: str) -> resp.BaseObject:
		"""
		Leave an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return resp.BaseObject(await (await self.req.make_async_request("DELETE", f"/g/s/chat/thread/{chatId}/member/{self.userId}", content_type="application/x-www-form-urlencoded")).json())
	


	async def send_message(self, chatId: str, message: str, replyId: str | None = None, mentionUserIds: list | None = None) -> resp.Message:
		
		message = message.replace("<@", "‎‏").replace("@>", "‬‭")

		data = {
		"type": args.MessageTypes.Text,
		"content": message,
		"attachedObject": None,
		"uid": self.userId
		}

		if replyId:data["replyMessageId"] = replyId
		if mentionUserIds:
			mentions = [{"uid": mention_uid} for mention_uid in mentionUserIds]
			data["extensions"] = {"mentionedArray": mentions}

		return resp.Message(await (await self.req.make_async_request("POST",  f"/g/s/chat/thread/{chatId}/message", data)).json())