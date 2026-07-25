from . import Message, UserProfile
from altamino.utils.state import AsyncSafeState, ThreadSafeState
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from altamino import AsyncClient, Client

class Event:
    """class with data about a new event"""

    def __init__(self, data: dict, client):
        self.client: AsyncClient | Client = client
        self.state = AsyncSafeState() if client.is_async else ThreadSafeState()

        self.data = data or {}
        params = data.get("params", {})

        # --- chat message (topic 1000) ---
        self.message: Message = Message(data.get("chatMessage", {}))
        self.alertOption = data.get("alertOption")
        self.membershipStatus = data.get("membershipStatus")
        self.actions = data.get("actions")
        self.target = data.get("target")
        self.params = params
        self.threadType = params.get("threadType")
        self.duration = params.get("duration")

        # --- push notification (topic 10) ---
        payload = data.get("payload", {})
        self.payload: Notification = Notification(payload)

        self.comId = data.get("ndcId") or payload.get("ndcId")

        self.sub_client = (
            self.client.get_community_client(self.comId) if self.comId else None
        )

        self.id = data.get("id") or payload.get("id")


class Notification:
    """push notification payload (topic 10)"""

    def __init__(self, data: dict):
        self.data = data or {}

        self.type = data.get("notifType")
        self.chatId = data.get("tid")
        self.comId = data.get("ndcId")
        self.uid = data.get("uid")
        self.author: UserProfile = UserProfile(data.get("userProfile", {}))
        self.nickname = data.get("nickname")
        self.threadType = data.get("ttype")
        self.icon = data.get("picUrl")
        self.picType = data.get("picType")
        self.url = data.get("u")
        self.createdTime = data.get("ts")
        self.expireTime = data.get("exp")
        self.community = data.get("community")
        self.extensions = data.get("ext", {})