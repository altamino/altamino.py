from __future__ import annotations

from base64 import b64decode, b64encode, urlsafe_b64decode
from time import timezone as tz_raw
from time import time as timestamp
from random import choice
from hashlib import sha1
from os import urandom
from orjson import loads, dumps
from uuid import uuid4
from hmac import new
import re

from altamino.utils.constants import (
    SIG_KEY,
    DEVICE_KEY,
    PREFIX,
    IPHONE_IDS,
    IOS_VERSIONS,
    APP_VERSIONS
)



class Generator:

    @staticmethod
    def str_uuid4() -> str:
        return str(uuid4())

    @staticmethod
    def reqtime() -> int:
        return int(timestamp() * 1000)

    @staticmethod
    def clientrefid() -> int:
        return int(timestamp() / 10 % 1000000000)

    @staticmethod
    def b64_to_bytes(b64: str, encoding: str = "utf-8") -> str:
        return b64decode(b64).decode(encoding)

    @staticmethod
    def bytes_to_b64(data: bytes, encoding: str = "utf-8") -> str:
        return b64encode(data).decode(encoding)

    @staticmethod
    def gen_deviceId(data: bytes | str | None = None) -> str:
        if isinstance(data, str): data = bytes(data, 'utf-8')
        identifier = PREFIX + (data or urandom(20))
        mac = new(DEVICE_KEY, identifier, sha1)
        return f"{identifier.hex()}{mac.hexdigest()}".upper()


    @staticmethod
    def gen_userAgent() -> str:
        return "Apple iPhone{} iOS v{} Main/{}".format(
            choice(IPHONE_IDS), choice(IOS_VERSIONS), choice(APP_VERSIONS)
        )

    @staticmethod
    def signature(data: str | bytes | dict) -> str:
        data = data.encode("utf-8") if isinstance(data, str) else data
        return Generator.bytes_to_b64(PREFIX + new(SIG_KEY, dumps(data) if isinstance(data, dict) else data, sha1).digest())

    @staticmethod
    def update_deviceId(device: str) -> str:
        return Generator.gen_deviceId(bytes.fromhex(device[2:42]))



    @staticmethod
    def decode_sid(SID: str) -> dict:
        """
        get data from authorization sid
            args:

            - sid: str
        """
        return loads(urlsafe_b64decode(SID + "=" * (4 - len(SID) % 4))[1:-20])

    @staticmethod
    def sid_to_uid(SID: str) -> str:
        """
        get an ID account from the authorization sid
            args:

            - sid: str
        """
        return Generator.decode_sid(SID)["2"]

    @staticmethod
    def sid_to_ip_address(SID: str) -> str:
        """
        get an ip address from the authorization sid
            args:

            - sid: str
        """
        return Generator.decode_sid(SID)["4"]

    @staticmethod
    def sid_to_created_time(SID: str) -> int:
        """
        get created time from the authorization sid
            args:

            - sid: str
        """
        return Generator.decode_sid(SID)["5"]

    @staticmethod
    def sid_to_client_type(SID: str) -> int:
        """
        get client type from the authorization sid
            args:

            - sid: str
        """
        return Generator.decode_sid(SID)["6"]



    @staticmethod
    def json_minify(string, strip_space=True) -> str:
        """
        Took from: https://github.com/getify/JSON.minify/tree/python
        Library under MIT license.

        I think install library to just minify json is stupid,
        so I copied function, sorry.
        """
        tokenizer = re.compile(r'"|(/\*)|(\*/)|(//)|\n|\r')
        end_slashes_re = re.compile(r"(\\)*$")

        in_string = False
        in_multi = False
        in_single = False

        new_str = []
        index = 0

        for match in re.finditer(tokenizer, string):
            if not (in_multi or in_single):
                tmp = string[index : match.start()]
                if not in_string and strip_space:
                    # replace white space as defined in standard
                    tmp = re.sub("[ \t\n\r]+", "", tmp)
                new_str.append(tmp)
            elif not strip_space:
                # Replace comments with white space so that the JSON parser reports
                # the correct column numbers on parsing errors.
                new_str.append(" " * (match.start() - index))

            last_index = index
            index = match.end()
            val = match.group()

            if val == '"' and not (in_multi or in_single):
                escaped = end_slashes_re.search(string, last_index, match.start())

                # start of string or unescaped quote character to end string
                if not in_string or (escaped is None or len(escaped.group()) % 2 == 0):  # noqa
                    in_string = not in_string
                index -= 1  # include " character in next catch
            elif not (in_string or in_multi or in_single):
                if val == "/*":
                    in_multi = True
                elif val == "//":
                    in_single = True
            elif val == "*/" and in_multi and not (in_string or in_single):
                in_multi = False
                if not strip_space:
                    new_str.append(" " * len(val))
            elif val in "\r\n" and not (in_multi or in_string) and in_single:
                in_single = False
            elif not ((in_multi or in_single) or (val in " \r\n\t" and strip_space)):  # noqa
                new_str.append(val)

            if not strip_space:
                if val in "\r\n":
                    new_str.append(val)
                elif in_multi or in_single:
                    new_str.append(" " * len(val))

        new_str.append(string[index:])
        return "".join(new_str)
