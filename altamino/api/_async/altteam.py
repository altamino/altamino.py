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

    async def link_telegram(self, telegram_id: int, amino_id: str | None = None) -> dict:
        """
        Link Telegram ID to AltAmino account.
        """
        payload = {"telegramId": telegram_id}
        if amino_id:
            payload["aminoId"] = amino_id

        result = await self.req.make_async_request("POST", "/g/s/altteam/telegram/link", payload)
        return await result.json()

    async def unlink_telegram(self, amino_id: str | None = None) -> dict:
        """
        Unlink Telegram ID from AltAmino account.
        """
        payload = {}
        if amino_id:
            payload["aminoId"] = amino_id

        result = await self.req.make_async_request("POST", "/g/s/altteam/telegram/unlink", payload)
        return await result.json()