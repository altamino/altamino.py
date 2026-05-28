from altamino.utils import log, loglevel

from altamino.utils.generators import Generator
import altamino.utils.exceptions as exceptions
import altamino.objects.resp as respObject
import altamino.objects.args as args


from altamino.clients.client import Client
from altamino.clients.sub_client import SubClient




def set_log_level(level: int | str = loglevel.INFO):
	"""
	Sets the logging level.

	:param level: The new logging level (loglevel.DISABLE, loglevel.INFO ...).
	"""
	log.set_level(level)


def enable_file_logging(log_file: str = 'kyodo.log'):
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

