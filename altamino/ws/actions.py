from __future__ import annotations
from altamino import exceptions

class SocketActions:

	def ws_send(self, req_t: int, **kwargs) -> None: ...
	def call(self, data: dict) -> None: ...

	def create_socket_event(self, data: dict) -> None:
		"""
		send data to event handler

		**parameters**
		- data : data to send
		"""
		return self.call(data)


	def online(self, comId: int) -> None:
		"""
			this request will show you in the list of online users
			
			**parameters**
			- comId : id of the community
		"""
		data = {
			"actions": ["Browsing"],
			"target":f"ndc://x{comId}/",
			"ndcId":comId
		}
		self.ws_send(req_t=304, body=data)


	def browsing_blogs(self, comId: int, blogId: str | None = None, quizId: str | None = None) -> None:
		"""
			this request will show you in the list of blog viewers
			
			**parameters**
			- comId : id of the community
			- blogId : id of the blog
			- quizId id of the quiz
		"""
		if blogId is None and quizId is None: raise exceptions.SpecifyType
		data = {
			"actions": ["Browsing"],
			"target": f"ndc://x{comId}/blog/{blogId or quizId}",
			"ndcId":comId,
			"params": {
				"blogType": 0 if blogId else 6,
				}
		}
		self.ws_send(req_t=304, body=data)


	def typing(self, chatId: str, comId: int | None = None) -> None:
		"""
			create the illusion of typing
			
			**parameters**
			- chatId : id of the chat
			- comId : id of the community
		"""

		data = {
			"actions": ["Typing"],
			"threadId": chatId,
			"target": f"ndc://x{comId}/chat-thread/{chatId}" if comId else f"ndc://x0/chat-thread/{chatId}",
			"params": {"threadType": 2}
		}
		if comId:data["ndcId"]=comId
		self.ws_send(req_t=304, body=data)

	def recording(self, chatId: str, comId: int | None = None) -> None:
		"""
			create the illusion of recording audio message
			
			**parameters**
			- chatId : id of the chat
			- comId : id of the community
		"""

		data = {
			"actions": ["Recording"],
			"threadId": chatId,
			"target": f"ndc://x{comId}/chat-thread/{chatId}" if comId else f"ndc://x0/chat-thread/{chatId}",
			"params": {"threadType": 2}
		}
		self.ws_send(req_t=304, body=data)


	def join_live_chat(self, chatId: str, comId: int | None = None, as_viewer: bool = False) -> None:
		"""
			join to live chat

			**parameters**
			- chatId : id of the chat
			- comId : id of the community
			- as_viewer : join as a viewer
		"""
		data = {
			"threadId": chatId,
			"joinRole": 2 if as_viewer else 1,
		}
		if comId:data["ndcId"]=int(comId)
		self.ws_send(req_t=112, body=data)


	def browsing_leader_boards(self, comId: int) -> None:
		"""
			send a request that will show you in the list of those viewing the leaderboard

			**parameters**
			- comId : id of the community
		"""
		data = {
			"o": {
				"actions": ["Browsing"],
				"target": f"ndc://x{comId}/leaderboards",
				"ndcId": int(comId),
				"params": {"duration": 859},
			}
		}
		self.ws_send(req_t=306, body=data)
