from __future__ import annotations

from altamino.api.base import SyncBaseClass
from altamino.utils.generators import Generator

from altamino import args, respObject
from altamino.utils import exceptions


class AuthModule(SyncBaseClass):


	def login(self, email: str, password: str | None = None, secret: str | None = None, client_type: int = args.ClientTypes.User) -> respObject.AuthData:
		"""
		Login into an account.

		**Parameters**
		- email : Email of the account.
		- password : Password of the account.
		- secret : secret of the account
		- client_type: Type of Client.
		"""
		if password is None and secret is None: raise exceptions.SpecifyType("Either password or secret must be provided.")
		result = self.req.make_request("POST", "/g/s/auth/login", {
			"email": email,
			"v": 2,
			"secret": secret if secret else f"0 {password}",
			"deviceID": self.deviceId,
			"clientType": client_type,
			"action": "normal",
		})

		data = result.json()
		self.me = respObject.AuthData(data)

		self.set_sid(self.me.sid)
		self.set_userId(self.me.auid)
		self.ws_connect()
		return self.me

	def get_account_info(self) -> respObject.UserProfile:
		"""
		Getting account info about you.
		"""
		return respObject.UserProfile(self.req.make_request("GET", "/g/s/account").json())




	def login_sid(self, sid: str) ->  respObject.AuthData:
		"""
		Login into an account.

		**Parameters**
		- sid : auth sid
		"""
		self.set_sid(sid)
		self.set_userId(Generator.sid_to_uid(sid))
		self.ws_connect()
		self.me = respObject.AuthData({"auid": self.userId, "sid": self.sid})
		return self.me


	async def logout(self) -> respObject.BaseObject:
		"""
		Logout from an account.
		"""
		result = self.req.make_request("POST", "/g/s/auth/logout", {
			"deviceID": self.deviceId,
			"clientType": Generator.sid_to_client_type(self.sid),
		}).json()
		self.set_sid(None)
		self.set_userId(None)
		self.me = respObject.AuthData({})
		self.ws_disconnect()
		return respObject.BaseObject(result)
