from altamino.api.base import BaseClass
from altamino.utils.generators import Generator

from altamino import args, respObject
from altamino.utils import exceptions


class AuthModule(BaseClass):


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
		if self.socket_enable:
			final = f"{self.deviceId}|{Generator.reqtime()}"
			#self.ws_connect(final=final, headers=self.ws_headers(self.sid, final, self.deviceId))
		return self.me

	async def get_account_info(self) -> respObject.UserProfile:
		"""
		Getting account info about you.
		"""
		return respObject.UserProfile(await (await self.req.make_async_request("GET", "/g/s/account")).json())
