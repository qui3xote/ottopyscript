import sys
import os
from importlib import reload
import asyncio
from pyparsing import *
from ottopyscript.interpreter import TestInterpreter, PyscriptInterpreter

SHOW_TASK_NAME = False
DEBUG_AS_INFO = True

if sys.executable == '/usr/local/Cellar/jupyterlab/3.2.4/libexec/bin/python3.9':
    ENVIRONMENT = 'DEV'
    sys.path.append("./ottolib")
    interpreter = TestInterpreter
else:
    ENVIRONMENT = 'PROD'
    sys.path.append("/config/ottolib")
    interpreter = PyscriptInterpreter

if 'ottolib' in sys.modules:
    import ottolib
    reload(ottolib)

from ottolib import OttoScript

registered_triggers = []

class OttoBuilder:
    def __init__(self, config):
        if not self.parse_config(config):
            log.error(f'INVALID CONFIG {config}')
            return

        for f in self._files:
            log.info(f'Reading {f}')
            scripts = task.executor(load_file, f)
            for script in scripts.split(";"):
                log.info(f"{script}")
                automation = OttoScript(interpreter(f), script)
                registered_triggers.append(self.build_automation(automation))


    def parse_config(self, data):
        path = data.get('directory')
        if path is None:
            log.error("Script directory is required")
            return False
        else:
            try:
                self._files = task.executor(get_files, path)
                return True
            except:
                log.error(f'Unable to read files from {path}')
                return False

    def build_automation(self, automation):
        @state_trigger(f"{automation.trigger}")
        def automation_func():
            nonlocal automation
            log.info(f"Running {type(automation)}")
            automation.execute()

        return automation_func


########################   Helpers #############################
@pyscript_compile
def fileexists(path):
    return os.path.isfile(path)

@pyscript_compile
def get_files(path):
    files = [os.path.join(path,f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files

@pyscript_compile
def load_file(path):
    with open(path) as f:
        contents = f.read()

    return contents

@time_trigger('startup')
def startup():
    for app in pyscript.app_config:
        OttoBuilder(app)
