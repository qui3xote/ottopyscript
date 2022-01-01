
class PyscriptInterpreter:

    def __init__(self):
        #self.funcs = {'set_state',}
        pass

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

    def set_state(self, args, kwargs={}):
        try:
            state.set(*args, **kwargs)
            return True
        except:
            self.log(f"Unable to complete operation state.set({name}, {value}, **{kwargs})","warn")
            return False

    def get_state(self, name):
        value = state.get(name)
        return value

    def service_call(self, args, kwargs):
        try:
            service.call(*args, **kwargs)
            return True
        except:
            self.log(f"Unable to complete operation state.set({name}, {value}, **{attr_kwargs})","warn")
            return False

    def compare(self, comparison):
        operation = comparison.eval()

        for n, i in enumerate(operation['items']):
            self.log(f"Found: {type(i)}, {i}")

            if type(i) == Entity:
                self.log(f"Entity: {type(i)}, {i.name}, {self.get_state(i.name)}")
                operation['items'][n] = self.get_state(i.name)

        result = operation['opfunc'](*operation['items'])
        self.log(f"{result}: {operation['opfunc']}, {operation['items']}")
        return result


    def eval_tree(self, tree):
        statements = []

        for i in tree['items']:
            if type(i) == dict:
                statements.append(eval_tree(i))
            if type(i) == Comparison:
                statements.append(self.compare(i))

        result = tree['opfunc'](statements)
        self.log(f"{result}: {tree}")
        return result

    def testadd(self, script):
        automation = self.parser().parse_string(script)

        ifthens = []

        for conditions, commands in automation.condition_clauses.as_list():
            ifthens.append([conditions.eval(), [command.eval() for command in commands]])

        self.log(f"trigger: {str(automation.when[0])}",'info')

        for conditions, commands in ifthens:
            if self.eval_tree(conditions) == True:
                for command in commands:
                    self.log(command)
            else:
                self.log("conditions failed","info")

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

    def sleep(self,seconds):
        task.sleep(seconds)

    def eval(self, operations):
        for op in operations:
            self.log(f'Operation: {type(op)}, {op}')
            func = op['opfunc']
            args = op['args'] if 'args' in op.keys() else []
            kwargs = op['kwargs'] if 'kwargs' in op.keys() else {}

            if callable(func) == False:
                try:
                    func = getattr(self, func)
                except:
                    self.log(f"No such function {func}")
                    return
                func(args,kwargs)
            else:
                func(*args,**kwargs)


    def log(self, msg, level="info"):
        if level == 'info':
            log.info(msg)
        if level == 'debug':
            if DEBUG_AS_INFO is True:
                log.info(msg)
        if level == 'warn':
            log.warn(msg)
