class PyscriptInterpreter:

    def __init__(self, log_id=None, debug_as_info=True):
        self.log_id = log_id

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
        self.log_debug(f"Getting state of {entity_name}")
        try:
            value = state.get(entity_name)
            return value
        except:
            self.log_warning(f"Unable to fetch state of {entity_name}")

    def call_service(self, domain, service_name, kwargs):
        try:
            service.call(domain, service_name, **kwargs)
            return True
        except:
            self.log_warning(f"Unable to complete service.call({domain}, {service_name}, **{kwargs}))")
            return False

    def sleep(self,seconds):
        task.sleep(seconds)

    def log_info(self, message):
        log.info(f'{self.log_id}: {message}')

    def log_error(self, message):
        log.error(f'{self.log_id}: {message}')

    def log_warning(self, message):
        log.warning(f'{self.log_id}: {message}')

    def log_debug(self, message):
        if DEBUG_AS_INFO:
            log.info(f'{self.log_id}: {message}')
        else:
            log.debug(f'{self.log_id}: {message}')
