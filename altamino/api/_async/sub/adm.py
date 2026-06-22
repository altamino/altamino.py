from __future__ import annotations
from altamino.api.base import SyncBaseClass
from altamino.objects import args, resp


class CommunityAdminModule(SyncBaseClass):
	comId: str | int | None