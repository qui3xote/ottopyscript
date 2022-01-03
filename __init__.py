import sys
import os
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

from ottolib import OttoParser

registered_triggers = []

class OttoBuilder:
    def __init__(self, config):
        if not self.parse_config(config):
            log.error(f'INVALID CONFIG {config}')
            return

        for f in self._files:
            scripts = task.executor(load_file(f))
            for script in scripts.split(";"):
                intrprt = interpreter()
                parser = OttoParser(intrprt)
                parsed = parser.parse(script)
                registered_triggers.append(intrprt.build_func(), parsed)


    def parse_config(self, data):
        path = data.get('directory')
        if path is None:
            log.error('Script directory is required')
            return False
        else:
            try:
                self._files = task.executor(get_files, path)
                return True
            except:
                log.error(f'Unable to read files from {path}')
                return False


####Helpers
@pyscript_compile
def fileexists(path):
    return os.path.isfile(path)

@pyscript_compile
def get_files(path):
    files = [os.path.join(path,f) for f in os.listdir(path) if os.isfile(os.path.join(path, f))]
    return files

@pyscript_compile
def load_file(path):
    with open('readme.txt') as f:
        contents = f.read()

    return contents


# @pyscript_compile
# def walk_directory(path):
#     # TODO: Add globals support (directory based inheritance)
#     script_list = []
#     try:
#         for dirpath, dirnames, filenames in os.walk(path):
#             if 'globals.otto' in filenames:
#                 filenames.pop('globals.otto')
#                 ottoglobals = os.path.join(dirpath, 'globals.otto')
#             else:
#                 ottoglobals = None
#             for f in filenames:
#                 filepath = os.path.join(dirpath, f)
#                 script_list.append({'globals': ottoglobals}, filepath)

######## What to do ###########
# Startup - fetch config, check it. If bad, fail.
# If good, get directory(ies?) of apps(name?)
# Read all files - split on semicolon, pass each to Otto

########## Config ############
#files: list of files, directories, path
#prefix: by default, otto uses {filename}_{automationname} for naming functions
#postfix: ''
# the prefix & postfix {filename_} can be overridden with plain text or macros:
# {directory}, {filename}, {fullpath}
# shared:
#   file: globals.otto
#

@time_trigger('startup')
def startup():
    for app in pyscript.app_config:
        OttoBuilder(app)
