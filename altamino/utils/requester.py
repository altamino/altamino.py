from __future__ import annotations

from aiohttp import ClientSession
from httpx import Client

from orjson import loads, dumps
from re import compile
from typing import Any, Callable

from altamino.objects.args import ProxyConfig, ProxyPool, ProxyUsage, ProxyConnector, ProxyType
from altamino.utils import log
from altamino.utils.generators import Generator
from altamino.utils.constants import BASIC_HEADERS, api_url
from altamino.utils.exceptions import checkAsyncException, checkException

class ContentTypeError(Exception):
	"""
	ContentType found is not valid.
	"""



JSONDecoder = Callable[[str], Any]
DEFAULT_JSON_DECODER = loads
json_re = compile(r"^application/(?:[\w.+-]+?\+)?json")


def _is_expected_content_type(
	response_content_type: str, expected_content_type: str
) -> bool:
	if expected_content_type == "application/json":
		return json_re.match(response_content_type) is not None
	return expected_content_type in response_content_type



def resolve_proxy(proxy: ProxyPool | ProxyConfig | None, usage: ProxyUsage = ProxyUsage.ALL) -> ProxyConfig | None:
	if isinstance(proxy, ProxyPool):
		return proxy.random(usage)
	if isinstance(proxy, ProxyConfig):
		return proxy
	return None


class HTTPRequest:
	def __init__(
		self,
		method: str,
		url: str,
		body: str | dict | bytes | None,
		headers: dict | None,
		proxy: ProxyConfig | None,
	):

		self.method = method
		self.url = url
		self.body = body
		self.headers = headers
		self.proxy = proxy

class HTTPResponse:

	def __init__(
		self,
		*,
		status: int,
		body: bytes,
		headers: dict,
		url: str,
		method: str,
		encoding: str,
		request: HTTPRequest
	):
		self.status = status
		self._body = body
		self.url = url
		self.method = method
		self.encoding = encoding
		self.request = request

		self.headers = {
			k.lower(): v
			for k, v in headers.items()
		}


	def get_bytes(self) -> bytes:
		return self._body

	def text(self, encoding: str | None = None, errors: str = "strict") -> str:
		"""Read response payload and decode."""

		if encoding is None:
			encoding = self.encoding
		return self._body.decode(encoding, errors=errors)

	def json(
		self,
		*,
		encoding: str | None = None,
		loads: JSONDecoder = DEFAULT_JSON_DECODER,
		content_type: str = "application/json",
	) -> dict | Any:
		"""Read and decodes JSON response."""
		if content_type:
			ctype = self.headers.get("content-type", "").lower()
			if not _is_expected_content_type(ctype, content_type):
				raise ContentTypeError(
						"Attempt to decode JSON with unexpected mimetype: %s" % ctype
				)

		stripped = self._body.strip()
		if not stripped:
			return None
		if encoding is None:
			encoding = self.encoding
		return loads(stripped.decode(encoding))

class AsyncHTTPResponse:

	def __init__(
		self,
		*,
		status: int,
		body: bytes,
		headers: dict,
		url: str,
		method: str,
		encoding: str,
		request: HTTPRequest
	):
		self.status = status
		self._body = body
		self.url = url
		self.method = method
		self.encoding = encoding
		self.request = request

		self.headers = {
			k.lower(): v
			for k, v in headers.items()
		}


	async def get_bytes(self) -> bytes:
		return self._body

	async def text(self, encoding: str | None = None, errors: str = "strict") -> str:
		"""Read response payload and decode."""

		if encoding is None:
			encoding = self.encoding
		return self._body.decode(encoding, errors=errors)

	async def json(
		self,
		*,
		encoding: str | None = None,
		loads: JSONDecoder = DEFAULT_JSON_DECODER,
		content_type: str = "application/json",
	) -> dict | Any:
		"""Read and decodes JSON response."""

		if content_type:
			ctype = self.headers.get("content-type", "").lower()
			if not _is_expected_content_type(ctype, content_type):
				raise ContentTypeError(
						"Attempt to decode JSON with unexpected mimetype: %s" % ctype
				)

		stripped = self._body.strip()
		if not stripped:
			return None
		if encoding is None:
			encoding = self.encoding
		return loads(stripped.decode(encoding))




class Requester:

	def __init__(self, user_agent: str, deviceId: str, language: str, accept_language: str, proxy: ProxyConfig | ProxyPool | None = None,):
		self.user_agent = user_agent
		self.deviceId = deviceId
		self.language = language
		self.accept_language = accept_language
		self.sid: str | None = None
		self.userId: str | None = None
		self.proxy: ProxyConfig | ProxyPool | None = proxy


	def build_headers(self, data: dict | str | bytes | None = None, headers: dict | None = None) -> dict:

		default_headers = BASIC_HEADERS.copy()
		default_headers["AUID"] = self.userId or Generator.str_uuid4()

		if self.accept_language:default_headers["Accept-Language"] = self.accept_language
		if self.language:default_headers["NDCLANG"] = self.language
		if self.user_agent:default_headers["User-Agent"] = self.user_agent
		if self.deviceId: default_headers["NDCDEVICEID"] = self.deviceId
		if data:
			default_headers["Content-Length"] = str(len(data))
			default_headers["NDC-MSG-SIG"] = Generator.signature(data)
		if self.sid: default_headers["NDCAUTH"] = f"sid={self.sid}"

		if headers: default_headers.update(headers)
		return default_headers


	def make_request(
		self,
		method: str,
		endpoint: str | None = None,
		body: dict | str | bytes | None = None,
		allowed_code: int | list[int] = 200,
		headers: dict | None = None,
		api: str | None = None,
	) -> HTTPResponse:
		if isinstance(body, dict):
			body["timestamp"] = Generator.reqtime()

		data = dumps(body) if isinstance(body, dict) else body
		req_headers = self.build_headers(data, headers)
		url = f"{api or api_url}{endpoint or ''}"

		_proxy = resolve_proxy(self.proxy, ProxyUsage.HTTP)
		proxies = _proxy.for_httpx() if _proxy else None

		with Client(proxy=proxies) as session:
			resp = session.request(method, url, content=data, headers=req_headers)
			response = HTTPResponse(
				status=resp.status_code,
				body=resp.content,
				headers=dict(resp.headers),
				url=str(resp.url),
				method=method,
				encoding=resp.encoding or "utf-8",
				request=HTTPRequest(method, url, data, req_headers, _proxy)
			)
			log.debug(
				f"[https][{method}][{endpoint or ''}][{resp.status_code}]: "
				f"{len(body) if isinstance(body, bytes) else body or '{}'}\n"
				f"Headers: {req_headers}\n"
				f"Proxy: {_proxy.url if _proxy else 'No proxy'}"
			)
			if isinstance(allowed_code, int):
				allowed_code = [allowed_code]
			if resp.status_code not in allowed_code:
				checkException(response)
			return response





	async def make_async_request(
		self,
		method: str,
		endpoint: str | None = None,
		body: dict | bytes | None = None,
		allowed_code: int | list[int] = 200,
		headers: dict | None = None,
		api: str | None = None,
	) -> AsyncHTTPResponse:

		if isinstance(body, dict):
			body["timestamp"] = Generator.reqtime()

		data = dumps(body) if isinstance(body, dict) else body
		req_headers = self.build_headers(data, headers)
		url = f"{api or api_url}{endpoint or ''}"

		_proxy = resolve_proxy(self.proxy, ProxyUsage.HTTP)
		connector: ProxyConnector | None = None
		proxy_url: str | None = None

		if _proxy:
			if _proxy.proxy_type == ProxyType.HTTP:
				proxy_url = _proxy.for_aiohttp()
			else:
				connector = _proxy.for_aiohttp_connector()  # SOCKS4/5

		async with ClientSession(connector=connector) as session:
			async with session.request(
				method, url, data=data, headers=req_headers, proxy=proxy_url
			) as resp:
				response = AsyncHTTPResponse(
					status=resp.status,
					body=await resp.read(),
					headers=dict(resp.headers),
					url=str(resp.url),
					method=method,
					encoding=resp.get_encoding(),
					request=HTTPRequest(method, url, data, req_headers, _proxy)
				)
				log.debug(
					f"[https][{method}][{api or ''}{endpoint or ''}][{response.status}]: "
					f"{len(body) if isinstance(body, bytes) else body or '{}'}\n"
					f"Headers: {req_headers}\n"
					f"Proxy: {_proxy.url if _proxy else 'No proxy'}"
				)
				if isinstance(allowed_code, int):
					allowed_code = [allowed_code]
				if response.status not in allowed_code:
					await checkAsyncException(response)
				return response
