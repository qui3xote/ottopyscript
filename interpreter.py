from itertools import product


class PyscriptInterpreter:

    def __init__(self, log_id=None, debug_as_info=False):
        self.log_id = log_id
        self.debug_as_info = debug_as_info
        self.trigger_funcs = {'state': self.state_trigger,
                              'time': self.time_trigger
                              }

    async def register(self, trigger, automation):
        func = self.trigger_funcs[trigger['type']]
        result = await func(trigger, automation)
        return result

    async def state_trigger(self, trigger, clauses):
        trigger_strings = []

        for name in trigger.entities:
            basestring = []
            if trigger.new is not None:
                basestring.append(f"{name} == '{trigger.new}'")

            if trigger.old is not None:
                basestring.append(f"{name}.old == '{trigger.old}'")

            if len(basestring) == 0:
                basestring.append(f"{name}")

            trigger_strings.append(" and ".join(basestring))

        @state_trigger(*trigger_strings, state_hold=trigger.hold_seconds)
        def otto_state_func(**kwargs):
            nonlocal clauses
            self.log_info("Running")
            for clause in clauses:
                clause.eval()

        return otto_state_func

    async def time_trigger(self, trigger, clauses):

        days = trigger['days']
        times = trigger['times']

        triggers = [f"once({x[0]} {x[1]})" for x in product(days, times)]

        @time_trigger(*triggers)
        def otto_time_func(**kwargs):
            nonlocal clauses
            self.log_info("Running")
            for clause in clauses:
                clause.eval()

        return otto_time_func

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

    def log_info(self, message):
        log.info(f'{self.log_id}: {message}')

    def log_error(self, message):
        log.error(f'{self.log_id}: {message}')

    def log_warning(self, message):
        log.warning(f'{self.log_id}: {message}')

    def log_debug(self, message):
        if self.debug_as_info:
            log.info(f'{self.log_id}: {message}')
        else:
            log.debug(f'{self.log_id}: {message}')
