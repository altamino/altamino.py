from __future__ import annotations

from altamino.utils import log, loglevel

from altamino.utils.generators import Generator
import altamino.utils.exceptions as exceptions
import altamino.objects.resp as respObject
import altamino.objects.args as args


from altamino.clients.client import Client
from altamino.clients.sub_client import SubClient

from altamino.clients._async.client import Client as AsyncClient
from altamino.clients._async.sub_client import SubClient as AsyncSubClient




def set_log_level(level: int | str = loglevel.INFO):
	"""
	Sets the logging level.

	:param level: The new logging level (loglevel.DISABLE, loglevel.INFO ...).
	"""
	log.set_level(level)


def enable_file_logging(log_file: str = 'altamino.log'):
	"""
	Enables logging to a file.

	:param log_file: The file where logs will be written.
	"""
	log.enable_file_logging(log_file)


def disable_file_logging():
	"""
	Disables logging to a file.
	"""
	if log.log_to_file:
		log.log_to_file = False
		log.logger.removeHandler(log.logger.handlers[-1])




__version__ = '1.1.5'
__newest__ = __version__
__title__ = 'altamino'
__author__ = 'alx0rr'
__license__ = 'MIT'
__copyright__ = f'Copyright 2025-2026 {__author__}'
__link__ = "https://t.me/Alx0rrHub"
__project_link__ = 'https://pypi.org/pypi/altamino'


from httpx import get
from packaging.version import parse as parse_version

try:
    response = get(f"{__project_link__}/json", timeout=3)
    data = response.json()
    __newest__ = data.get("info", {}).get("version", __version__)
except Exception:
    pass 


def check_lib_version():
    """
    Warn the user if the installed library version is outdated.
    Compares the current version against the latest release on PyPI.
    """
    current = parse_version(__version__)
    newest = parse_version(__newest__)

    if newest > current:
        log.warning(
            f'{__title__} made by {__author__}\n'
            f'Please update the library.\n'
            f'Your version: {current}  Latest version: {newest}\n'
            f'Follow our projects and updates: {__link__}'
        )


if __name__ != "__main__":
    check_lib_version()