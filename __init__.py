import sys
import os
import pathlib
from ottopyscript.helpers import py_reload
from ottopyscript.interpreter import PyscriptInterpreter
sys.path.append("/config/ottoscript")

import ottoscript

py_reload(ottoscript)

from ottoscript import OttoScript

SHOW_TASK_NAME = False
DEBUG_AS_INFO = True

registered_triggers = []


class OttoBuilder:

    def __init__(self, config):
        if not self.parse_config(config):
            log.error(f'INVALID CONFIG {config}')
            return

        for f in self._files:
            log.info(f'Reading {f}')
            scripts = task.executor(load_file, f)
            for script in scripts.split(";")[0:-1]:
                log.info(f"{script}")
                interpreter = PyscriptInterpreter(f, debug_as_info=DEBUG_AS_INFO)
                automation = OttoScript(interpreter, script)
                interpreter.set_controls(automation.controls)
                for t in automation.triggers:
                    func = interpreter.register(t, automation.clauses)
                    registered_triggers.extend(func)

    def parse_config(self, data):
        path = data.get('directory')
        if path is None:
            log.error("Script directory is required")
            return False
        else:
            try:
                self._files = task.executor(get_files, path)
                return True
            except Exception as error:
                log.error(f'Unable to read files from {path}. Error: {error}')
                return False

    def build_automation(self, automation):

        def otto_func():
            nonlocal automation
            log.info(f"Running {type(automation)}")
            automation.eval()

        return otto_func

    def wrap(self, trigger, func):
        trigger_dict = {'state_change': self.state_trigger,
                        'time': self.time_trigger}
        wrapped = trigger_dict[trigger.trigger_type](func)
        return wrapped


# Helpers
@pyscript_compile
def fileexists(path):
    return os.path.isfile(path)


@pyscript_compile
def get_files(path):
    files = []
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)):
            if pathlib.Path(f).suffix == '.otto':
                files.append(os.path.join(path, f))
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
