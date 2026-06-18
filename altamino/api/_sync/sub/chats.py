from __future__ import annotations
from altamino.api.base import SyncBaseClass
from altamino.objects import args, resp


class CommunityChatsModule(SyncBaseClass):
	comId: str | int | None

	def send_message(self, chatId: str, message: str, replyId: str | None = None, mentionUserIds: list | None = None) -> resp.Message:
		
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

		return resp.Message(self.req.make_request("POST",  f"/x{self.comId}/s/chat/thread/{chatId}/message", data).json())


	def join_chat(self, chatId: str) -> resp.BaseObject:
		"""
		Join an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return resp.BaseObject(self.req.make_request("POST", f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.userId}", content_type="application/x-www-form-urlencoded").json())

	def leave_chat(self, chatId: str) -> resp.BaseObject:
		"""
		Leave an Chat.

		**Parameters**
		- chatId : ID of the Chat.
		"""
		return resp.BaseObject(self.req.make_request("DELETE", f"/x{self.comId}/s/chat/thread/{chatId}/member/{self.userId}", content_type="application/x-www-form-urlencoded").json())
