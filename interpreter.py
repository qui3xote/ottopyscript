pyscript_registry = {}


class PyscriptLogger:

    def __init__(self, log_id='test', task=None, debug_as_info=False):
        self.log_id = log_id
        self.debug_as_info = debug_as_info
        self.task = task

    def set_task(self, task):
        self.task = task

    async def info(self, message):
        log.info(f'{self.log_id} {self.task} {message}')

    async def error(self, message):
        log.error(f'{self.log_id} {self.task} {message}')

    async def warning(self, message):
        log.warning(f'{self.log_id}  {self.task} {message}')

    async def debug(self, message):
        if self.debug_as_info:
            log.info(f'{self.log_id}  {self.task} {message}')
        else:
            log.debug(f'{self.log_id}  {self.task} {message}')

    def format_message(self, message):
        return f"{self.log_id}|{self.name}: {message}"

    def log_info(self, message):
        log.info(self.format_message(message))


class Registrar:
    """Register functions and hold runtime vars"""

    def __init__(self, logger):
        self.log = logger
        self.log.set_task('registrar')
        self.registry = {}

    async def add(self, controls, triggers, actions):
        namespace = controls.ctx.log.log_id
        name = controls.name
        key = (namespace, name)

        if namespace not in self.registry.keys():
            self.registry[namespace] = {}

        self.registry[namespace].update(
            {
                name:
                {
                    'actions': actions,
                    'controls': controls,
                    'triggers': triggers
                }
            }
        )

        if key not in pyscript_registry:
            pyscript_registry.update({key: []})

        for trigger in triggers.as_list():
            self.log.debug(f"Registering {key} with trigger {trigger}")

            if trigger['type'] == 'state':
                func = state_trigger_factory(
                    self,
                    key,
                    controls,
                    trigger['string'],
                    trigger['hold']
                )

            elif trigger['type'] == 'time':
                func = time_trigger_factory(
                    self,
                    key,
                    controls,
                    trigger['string']
                )

            pyscript_registry[key].append(func)

    async def eval(self, key, kwargs):
        actions = self.registry[key[0]][key[1]]['actions']
        # actions.ctx.update_vars(kwargs)
        await actions.eval()


def state_trigger_factory(registrar, key, controls, string, hold):

    @task_unique(controls.name, kill_me=controls.restart)
    @state_trigger(string, state_hold=hold)
    async def otto_state_func(**kwargs):
        nonlocal registrar, key
        await registrar.eval(key, kwargs)

    return otto_state_func


def time_trigger_factory(registrar, key, controls, string):

    @task_unique(self.name, kill_me=self.restart)
    @time_trigger(string)
    async def otto_time_func(**kwargs):
        nonlocal registrar, key
        await registrar.eval(key, kwargs)

    return otto_time_func


class Interpreter:
    """Convert ottoscript commands to pyscript commands"""

    def __init__(self, logger=None):

        if logger is None:
            self.log = PrintLogger()
        else:
            self.log = logger

    async def set_state(self, entity_name, value=None,
                        new_attributes=None, kwargs=None):

        message = f"state.set(entity_name={entity_name},"
        message += f" value={value},"
        message += f" new_attributes={new_attributes},"
        message += f" kwargs = **{kwargs})"

        await self.log.info(message)

        return state.set(entity_name, value, new_attributes, kwargs)

    async def get_state(self, entity_name):
        await self.log.info(f"Getting State of {entity_name}")
        return state.get(entity_name)

    async def call_service(self, domain, service_name, **kwargs):
        message = f"service.call({domain}, {service_name}, **{kwargs}))"
        await self.log.debug(message)
        return service.call(domain, service_name, **kwargs)

    async def sleep(self, seconds):
        await self.log.info(f"task.sleep({seconds}))")
        return task.sleep(seconds)
