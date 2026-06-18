from time import timezone as tz_raw


api_url: str = "https://service.altamino.top/api/v1"
ws_url: str = "wss://ws1.altamino.top"


ws_reconnect_time = 600
ws_ping_time = 10


PREFIX = bytes.fromhex("19")
SIG_KEY = bytes.fromhex("DFA5ED192DDA6E88A12FE12130DC6206B1251E44")
DEVICE_KEY = bytes.fromhex("E7309ECC0953C6FA60005B2765F99DBBC965C8E9")

BASIC_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
	"Host": "service.altamino.top",
    "NDCLANG": "en",
    "Content-Type": "application/json; charset=utf-8"
}

IPHONE_IDS = [
    "11,2",
    "11,4",
    "11,6",
    "11,8",
    "12,1",
    "12,3",
    "12,5",
    "12,8",
    "13,1",
    "13,2",
    "13,3",
    "13,4",
    "14,2",
    "14,3",
    "14,4",
    "14,5",
    "14,6",
    "14,7",
    "14,8",
    "15,2",
    "15,3",
    "15,4",
    "15,5",
    "16,1",
    "16,2",
]
IOS_VERSIONS = [
    "14.2",
    "14.3",
    "14.4",
    "14.4.1",
    "14.4.2",
    "14.5",
    "14.5.1",
    "14.6",
    "14.7",
    "14.7.1",
    "14.8",
    "14.8.1",
    "15.0",
    "15.0.1",
    "15.0.2",
    "15.1",
    "15.1.1",
    "15.2",
    "15.2.1",
    "15.3",
    "15.3.1",
    "15.4",
    "15.4.1",
    "15.5",
    "15.6",
    "15.6.1",
    "15.7",
    "15.7.1",
    "16.0",
    "16.0.2",
    "16.0.3",
    "16.1",
    "16.1.1",
    "16.1.2",
    "16.2",
    "16.3",
    "16.3.1",
    "16.4",
    "16.4.1",
    "16.5",
    "16.5.1",
    "16.6",
    "16.6.1",
    "16.7",
    "16.7.1",
    "16.7.2",
    "17.0",
    "17.0.1",
    "17.0.2",
    "17.0.3",
    "17.1",
    "17.1.1",
    "17.1.2",
    "17.2",
    "17.2.1",
    "17.3",
    "17.3.1",
    "17.4",
    "17.4.1",
    "17.5",
]
APP_VERSIONS = ["3.24.0", "3.23.0", "3.22.0", "3.21.0", "3.20.0"]

LOCAL_TIMEZONE = -tz_raw // 1000
