from itertools import product


def state_trigger_factory(interpreter, name, string, hold, clauses,
                          trigger_var="@trigger", kill_me=False):

    @task_unique(name, kill_me=kill_me)
    @state_trigger(string, state_hold=hold)
    def otto_state_func(**kwargs):
        nonlocal clauses
        nonlocal trigger_var
        nonlocal interpreter
        for c in clauses:
            c.set_vars({trigger_var: kwargs})
        log.info("Running")
        for clause in clauses:
            clause.eval(interpreter)

    return otto_state_func


def time_trigger_factory(interpreter, name, string, clauses,
                         trigger_var, kill_me=False):

    @task_unique(name, kill_me=kill_me)
    @time_trigger(string)
    def otto_time_func(**kwargs):
        nonlocal clauses
        nonlocal trigger_var
        nonlocal interpreter
        for c in clauses:
            c.set_vars({trigger_var: kwargs})
        log.info("Running")
        for clause in clauses:
            clause.eval(interpreter)

    return otto_time_func


class PyscriptInterpreter:

    def __init__(self, log_id=None, debug_as_info=True):
        self.log_id = log_id
        self.name = None
        self.debug_as_info = debug_as_info
        self.trigger_funcs = {'state': self.state_trigger,
                              'time': self.time_trigger
                              }
        self.set_controls()

    def set_controls(self, controller=None):
        if controller is None:
            self.name = self.log_id
            self.trigger_var = '@trigger'
            self.restart = False
        else:
            self.name = controller.name
            self.restart = controller.restart
            self.trigger_var = controller.trigger_var

    def register(self, trigger, automation):
        func = self.trigger_funcs[trigger.type]
        result = func(trigger, automation)
        return result

    def state_trigger(self, trigger, clauses):
        funcs = []
        state_hold = trigger.hold_seconds

        for name in trigger.entities:
            basestring = []
            if trigger.new is not None:
                basestring.append(f"{name} == '{trigger.new}'")

            if trigger.old is not None:
                basestring.append(f"{name}.old == '{trigger.old}'")

            if len(basestring) == 0:
                basestring.append(f"{name}")

            string = " and ".join(basestring)
            funcs.append(state_trigger_factory(self,
                                               self.name,
                                               string,
                                               state_hold,
                                               clauses,
                                               self.trigger_var,
                                               self.restart
                                               ))

        return funcs

    def time_trigger(self, trigger, clauses):

        days = trigger.days
        times = trigger.times
        offset = trigger.offset_seconds
        cproduct = product(days, times)
        strings = [f"once({x[0]} {x[1]} + {offset}s)" for x in cproduct]

        return [time_trigger_factory(self,
                                     self.name,
                                     s,
                                     clauses,
                                     self.trigger_var,
                                     self.restart) for s in strings]
        # self.log_info(f"adding {', '.join(triggers)}")

    def set_state(self,
                  entity_name,
                  value=None,
                  new_attributes=None,
                  kwargs=None):
        try:
            state.set(entity_name, value, new_attributes, **kwargs)
            return True
        except Exception as error:
            self.log_warning(f"Unable to complete operation \
                        state.set(entity_name={entity_name}, \
                        value={value}, \
                        new_attributes={new_attributes}, \
                        kwargs = **{kwargs})")
            self.log_error(error)
            return False

    def get_state(self, entity_name):
        self.log_info(f"Getting state of {entity_name}")
        try:
            value = state.get(entity_name)
            return value
        except Exception as error:
            self.log_warning(f"Unable to fetch state of "
                             + f"{entity_name}:{error}")

    def call_service(self, domain, service_name, kwargs):
        try:
            service.call(domain, service_name, **kwargs)
            return True
        except Exception as error:
            message = "Unable to complete"
            message += f"service.call({domain}, {service_name}, **{kwargs}))"
            self.log_warning(message)
            self.log_error(f"{error}")
            return False

    def sleep(self, seconds):
        task.sleep(seconds)

    def format_message(self, message):
        return f"{self.log_id}|{self.name}: {message}"

    def log_info(self, message):
        log.info(self.format_message(message))

    def log_error(self, message):
        log.error(self.format_message(message))

    def log_warning(self, message):
        log.warning(self.format_message(message))

    def log_debug(self, message):
        if self.debug_as_info:
            log.info(self.format_message(message))
        else:
            log.debug(self.format_message(message))
