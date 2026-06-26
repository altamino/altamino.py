from __future__ import annotations
from altamino.api.base import AsyncBaseClass
from altamino.objects import args, resp


class AltTeamModule(AsyncBaseClass):



	async def reset_password_by_support(self, email: str) -> dict:
		"""
		Reset password by support.

		**Parameters**
		- email : Email of the account for sending new password.
		"""
		
		result = await self.req.make_async_request("POST", "/g/s/altteam/reset-password", {
			"email": email,
		})

		return await result.json()