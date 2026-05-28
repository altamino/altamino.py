from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as file:
	long_description = file.read()

link = 'https://github.com/altamino/altamino.py/archive/refs/heads/main.zip'
docs_url = 'https://github.com/altamino/altamino.py/blob/main/docs/index.md'
ver = '0.0.1'

setup(
	name = "altamino",
	version = ver,
	url = "https://github.com/altamino/altamino.py",
	download_url = link,
	license = "MIT",
	author = "alx0rr",
	author_email = "anon.mail.al@proton.me",
	description = "Library for creating altamino bots and scripts.",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	docs_url = docs_url,
	keywords = [
		"altamino.py",
		"altamino",
		"altamino-py",
		"altamino-bot",
		"api",
		"python",
		"python3",
		"python3.x",
		"alx0rr",
		"official",
		"async",
		"sync",
		"altamino.top"
	],
	install_requires = [
		"logging",
		"colorama",
		"aiohttp",
		"pyjwt",
		"aiofiles",
		"orjson",
		"websocket-client",
		"httpx",
		"httpx[socks]",
		"aiohttp_socks"
	],
	packages = find_packages()
)
