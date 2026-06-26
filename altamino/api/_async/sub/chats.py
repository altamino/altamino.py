from __future__ import annotations
from altamino.api.base import AsyncBaseClass
from altamino.objects import args, resp


class CommunityChatsModule(AsyncBaseClass):
	comId: str | int | None

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

		return resp.Message(await (await self.req.make_async_request("POST",  f"/x{self.comId}/s/chat/thread/{chatId}/message", data)).json())


	async def join_chat(self, chatId: str) -> resp.BaseObject:
		"""
		Join an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return resp.BaseObject(await (await self.req.make_async_request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.userId}", content_type="application/x-www-form-urlencoded")).json())

	async def leave_chat(self, chatId: str) -> resp.BaseObject:
		"""
		Leave an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return resp.BaseObject(await (await self.req.make_async_request("DELETE", f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.userId}", content_type="application/x-www-form-urlencoded")).json())



	async def add_co_hosts(self, chatId: str, coHosts: list, comId: str | int | None = None):
		"""
		Add assistants to chat

		**Parameters**
		- chatId : id of the chat
		- coHosts : user id's
		"""
		data = {
			"uidList": coHosts
		}
		return await (await self.req.make_async_request("POST", f"/x{comId or self.comId}/s/chat/thread/{chatId}/co-host", data)).json()

	async  def delete_co_host(self, chatId: str, userId: str, comId: str | int | None = None):
		"""
		Remove co-host from chat
		**Parameters**:
		- chatId: id of the chat 
		- userId: id of the user 
		"""
		return await (await self.req.make_async_request("DELETE", f"/x{comId or self.comId}/chat/thread/{chatId}/co-host/{userId}")).json()


	async def transfer_host(self, chatId: str, userIds: list[str], comId: str | int | None = None):
		"""
		transfer host from chat

		**Parameters**:
		- chatId: id of the chat 
		- userIds: id of the user's
		"""
		data = {"uidList": userIds }
		return await (await self.req.make_async_request("POST", f"/x{comId or self.comId}/s/chat/thread/{chatId}/transfer-organizer", data)).json()

	async def accept_host(self, chatId: str, requestId: str, comId: str | int | None = None):
		"""
		Accepting host in chat.

		**Parameters**:
		- chatId: id of the chat 
		- requestId: host transfer request ID
		"""
		return await (await self.req.make_async_request("POST", f"/x{comId or self.comId}/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept")).json()

	async def kick(self, userId: str, chatId: str, allowRejoin: bool = True, comId: str | int | None = None):
		return await (await self.req.make_async_request("DELETE", f"/x{comId or self.comId}/s/chat/thread/{chatId}/member/{userId}?allowRejoin={int(allowRejoin)}")).json()


	async def delete_chat(self, chatId: str):
		"""
		Delete a Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return await (await self.req.make_async_request("DELETE", f"/x{self.comId}/s/chat/thread/{chatId}")).json()