import sys
import os
import pathlib
from ottopyscript.helpers import py_reload
from ottopyscript.interpreter import PyscriptInterpreter
sys.path.append("/config/ottoscript")

import ottoscript

# Force pyscript to reload the ottoscript module.
# Otherwise, a full hass restart is required to
# reflect new ottoscript versions
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
            # ensure that each file maintains a separate namespace
            globals = {'area_domains': self.area_domains}
            log.info(f'Reading {f}')
            try:
                scripts = task.executor(load_file, f)

                for script in scripts.split(";")[0:-1]:
                    log.info(f"{script}")
                    interpreter = PyscriptInterpreter(f, debug_as_info=DEBUG_AS_INFO)
                    automation = OttoScript(script, passed_globals=globals)

                    # Have the automation update it's globals with any
                    # newly defined vars. Then fetch those updated
                    # definitons and hang on to them for the next script.
                    automation.update_globals(interpreter)
                    globals.update(automation.global_vars)

                    interpreter.set_controls(automation.controls)
                    interpreter.actions = automation.actions

                    for t in automation.triggers:
                        func = interpreter.register(t)
                        registered_triggers.extend(func)
            except Exception as error:
                log.warning("unable to parse, skipping")
                log.error(error)

    def parse_config(self, data):
        path = data.get('directory')
        if path is None:
            log.error("Script directory is required")
            return False
        else:
            try:
                self._files = task.executor(get_files, path)
            except Exception as error:
                log.error(f'Unable to read files from {path}. Error: {error}')
                return False

        self.area_domains = data.get("area_domains")
        if self.area_domains is None:
            self.area_domains = {}
        return True


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
