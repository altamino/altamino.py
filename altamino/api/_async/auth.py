from __future__ import annotations

from altamino.api.base import AsyncBaseClass
from altamino.utils.generators import Generator

from altamino import args, respObject
from altamino.utils import exceptions


class AuthModule(AsyncBaseClass):


	async def login(self, email: str, password: str | None = None, secret: str | None = None, client_type: int = args.ClientTypes.User) -> respObject.AuthData:
		"""
		Login into an account.

		**Parameters**
		- email : Email of the account.
		- password : Password of the account.
		- secret : secret of the account
		- client_type: Type of Client.
		"""
		if password is None and secret is None: raise exceptions.SpecifyType("Either password or secret must be provided.")
		result = await self.req.make_async_request("POST", "/g/s/auth/login", {
			"email": email,
			"v": 2,
			"secret": secret if secret else f"0 {password}",
			"deviceID": self.deviceId,
			"clientType": client_type,
			"action": "normal",
		})

		data = await result.json()
		self.me = respObject.AuthData(data)

		self.set_sid(self.me.sid)
		self.set_userId(self.me.auid)
		await self.ws_connect()
		return self.me

	async def get_account_info(self) -> respObject.UserProfile:
		"""
		Getting account info about you.
		"""
		return respObject.UserProfile(await (await self.req.make_async_request("GET", "/g/s/account")).json())


	async def login_sid(self, sid: str) ->  respObject.AuthData:
		"""
		Login into an account.

		**Parameters**
		- sid : auth sid
		"""
		self.set_sid(sid)
		self.set_userId(Generator.sid_to_uid(sid))
		await self.ws_connect()
		self.me = respObject.AuthData({"auid": self.userId, "sid": self.sid})
		return self.me


	async def logout(self, client_type: int = args.ClientTypes.User) -> respObject.BaseObject:
		"""
		Logout from an account.
		"""
		result = await (await self.req.make_async_request("POST", "/g/s/auth/logout", {
			"deviceID": self.deviceId,
			"clientType": client_type#Generator.sid_to_client_type(self.sid),
		})).json()
		self.set_sid(None)
		self.set_userId(None)
		self.me = respObject.AuthData({})
		await self.ws_disconnect()
		return respObject.BaseObject(result)
