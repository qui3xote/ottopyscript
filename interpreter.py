from itertools import product
from copy import copy

registered_triggers = []
registered_vars = {}


class PyscriptInterpreter:

    def __init__(self, log_id=None, debug_as_info=True):
        self.log_id = log_id
        self.debug_as_info = debug_as_info
        self.trigger_funcs = {'state': self.state_trigger,
                              'time': self.time_trigger
                              }
        # Saving for later....
        # area_registry = hass.helpers.area_registry.async_get_registry()
        # areas = area_registry.async_list_areas()
        # self.hass_area_ids = [x.id for x in areas]
        #
        # self.service_domains = hass.services.async_services().keys()

        # Default Values
        self.name = None
        self.trigger_var = '@trigger'
        self.restart = False
        self.actions = None

    def set_controls(self, controller=None):
        if controller is not None:
            self.name = controller.name
            self.restart = controller.restart
            self.trigger_var = controller.trigger_var

    def register(self, trigger):
        try:
            func = self.trigger_funcs[trigger.type]
            result = func(trigger)
            registered_triggers.extend(result)
            registered_vars[f"{self.log_id}{self.name}"] \
                = copy(self.actions._vars)
            return True
        except Exception as error:
            message = f"Unable to register {str(trigger)}"
            self.log_warning(message)
            self.log_error(error)
            return False

    def state_trigger(self, trigger):
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
            self.log_debug(f"Registering state change: {string} hold:{state_hold}")
            funcs.append(self.state_trigger_factory(string, state_hold))

        return funcs

    def time_trigger(self, trigger):
        times = trigger.times
        offset = trigger.offset_seconds
        days = trigger.days

        self.log_debug(f"Registering times:{times} days:{days} offset:{offset}")
        cproduct = product(days, times)
        strings = [f"once({x[0]} {x[1]} + {offset}s)" for x in cproduct]

        return [self.time_trigger_factory(s) for s in strings]

    def set_state(self,
                  entity_name,
                  value=None,
                  new_attributes=None,
                  kwargs={}}):
        try:
            self.log_debug(f"Setting {entity_name} to {value} with {kwargs}")
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
        self.log_debug(f"Getting state of {entity_name}")
        try:
            value = state.get(entity_name)
            return value
        except Exception as error:
            self.log_warning("Unable to fetch state of "
                             + f"{entity_name}:{error}")

    def call_service(self, domain, service_name, kwargs):
        try:
            message = f"service.call({domain}, {service_name}, **{kwargs})"
            self.log_debug(message)
            service.call(domain, service_name, **kwargs)
            return True
        except Exception as error:
            message = "Unable to complete"
            message += f"service.call({domain}, {service_name}, **{kwargs}))"
            self.log_warning(message)
            self.log_error(f"{error}")
            return False

    def sleep(self, seconds):
        self.log_debug(f"Sleeping for {seconds}")
        task.sleep(seconds)

    def state_trigger_factory(self, string, hold):

        self.log_debug(f"Registering {self.name} with trigger '{string}'")

        @task_unique(self.name, kill_me=self.restart)
        @state_trigger(string, state_hold=hold)
        def otto_state_func(**kwargs):
            nonlocal self
            self.log_info(f"Triggered by f{kwargs}")

            vars = registered_vars[f"{self.log_id}{self.name}"]
            self.actions.update_vars(vars)
            self.actions.update_vars({self.trigger_var: kwargs})
            self.actions.eval(self)

        return otto_state_func

    def time_trigger_factory(self, string):
        self.log_debug(f"Registering {self.name} with trigger '{string}'")

        @task_unique(self.name, kill_me=self.restart)
        @time_trigger(string)
        def otto_time_func(**kwargs):
            nonlocal self
            self.log_info(f"Triggered by f{kwargs}")
            vars = registered_vars[f"{self.log_id}{self.name}"]
            self.actions.update_vars(vars)
            self.actions.update_vars({self.trigger_var: kwargs})
            self.actions.eval(self)

        return otto_time_func

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
