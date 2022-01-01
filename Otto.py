import os
import asyncio

if "/config/otto" not in sys.path:
     sys.path.append("/config/ottolib")

from ottolib import parser
from interpreter import PyscriptInterpreter

SHOW_TASK_NAME = False
DEBUG_AS_INFO = False

registered_triggers = []

class Otto:
    def __init__(self):
        if not self.parse_config(config):
            log.error(f'INVALID CONFIG {config}')
            return

    def log_info(self, message):
        log.info(f'{self.log_id()}: {message}')

    def log_error(self, message):
        log.error(f'{self.log_id()}: {message}')

    def log_warning(self, message):
        log.warning(f'{self.log_id()}: {message}')

    def log_debug(self, message):
        if DEBUG_AS_INFO:
            log.info(f'{self.log_id()} DEBUG: {message}')
        else:
            log.debug(f'{self.log_id()}: {message}')

    def parse_config(self, data):
    # TODO: use voluptuous
        self.script_dir = data.get('script_directory')

        if self.script_dir is None:
            log.error('script_directory is required')
            return False

        if not os.path.isfile(self.script_dir):


#####Helpers
@pyscript_compile
def fileexists(path):
    return os.path.isfile(path)

@pyscript_compile
def filelist(path):
    return os.path.isfile(path)
