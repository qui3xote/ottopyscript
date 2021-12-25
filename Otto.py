from pyparsing import *

if "/config/otto" not in sys.path:
     sys.path.append("/config/ottolib")

from ottolib import *

SHOW_TASK_NAME = False
DEBUG_AS_INFO = False

registered_triggers = []


class Otto:
    def __init__(self):
        pass


    @property
    def parser(self):
        command = Or([cls.parser() for cls in BaseCommand.__subclasses__()])
        trigger = Or([cls.parser() for cls in BaseTrigger.__subclasses__()])
        condition = Or([cls.parser() for cls in BaseCondition.__subclasses__()])

        WHEN, THEN = map(CaselessKeyword, ["WHEN", "THEN"])


        when_expr = WHEN.suppress() + Group(trigger)("when")
        then_clause = THEN.suppress() + Group(OneOrMore(command))("actions")
        conditionclause = condition("conditions") + then_clause
        ottoparser = when_expr + OneOrMore(Group(conditionclause))("condition_clauses")
        return ottoparser

    def add(self,script):
        automation = self.parser.parse_string(script)

        @state_trigger(str(automation.when[0]), **automation.when[0].kwargs)
        @task_unique(f"ottomation_{str(automation.when[0])}")
        def ottomation():
            nonlocal automation
            for clause in automation.condition_clauses:
                if clause.conditions[0].value == True:
                    for command in clause.actions:
                        command.run()

        return ottomation
