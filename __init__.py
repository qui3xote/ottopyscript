import sys
import os
import pathlib
from ottopyscript.helpers import py_reload
from ottopyscript.interpreter import Interpreter, Logger, Registrar
sys.path.append("/config/ottoscript")

import ottoscript

# Force pyscript to reload the ottoscript module.
# Otherwise, a full hass restart is required to
# reflect new ottoscript versions
py_reload(ottoscript)

from ottoscript.ottoscript import Auto

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
            globals = {}
            log.info(f'Reading {f}')
            scripts = task.executor(load_file, f)

            scripts = file.split(";")[:]
            scripts = [s for s in scripts if len(s.strip()) > 0]
            stored_globals = {'area_shortcuts': {"home": ['floor1', 'floor2'], "floor1": ["room1","room2"]}}
            f = "dir/filename"
            debug_as_info = True

            logger = PrintLogger(log_id=f, task='otto_main', debug_as_info=debug_as_info)
            registrar = Registrar(PrintLogger(log_id=f, task='registrar', debug_as_info=debug_as_info))
            interpreter = TestInterpreter(logger)

            for script in scripts:
                scriptlogger = PrintLogger(log_id=f, debug_as_info=debug_as_info)
                script_interpreter = TestInterpreter(scriptlogger)
                ctx = OttoContext(script_interpreter, scriptlogger)
                ctx.update_global_vars(stored_globals)
                OttoBase.set_context(ctx)

                try:
                    auto = Auto().parse_string(script)[0]
                except Exception as error:
                    await logger.log.error(f"FAILED TO PARSE: {script}\n{error}\n")

                try:
                    await registrar.add(auto.controls, auto.triggers, auto.actions)
                except Exception as error:
                    await logger.error(f"Register: {script}\n{error}\n")

                stored_globals = ctx.global_vars

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
