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


    def add(self, script):
        automation = self.parser().parse_string(script)

        ifthens = []

        for conditions, commands in automation.condition_clauses.as_list():
            ifthens.append([conditions.eval(), [command.eval() for command in commands]])

        @state_trigger(f"{str(automation.when[0])}")
        def otto():
            nonlocal ifthens
            for conditions, commands in ifthens:
                if self.eval_tree(conditions) == True:
                    for command in commands:
                        self.eval(command)
                else:
                    self.log("conditions failed","info")

        return otto

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
