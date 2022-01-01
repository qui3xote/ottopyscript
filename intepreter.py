class PyscriptInterpreter:

    def __init__(self):
        pass

    def set_state(self, entity_name, value=None, new_attributes=None, kwargs):
        try:
            state.set(entity_name, value, new_attributes, **kwargs)
            return True
        except:
            self.log_warning(f"Unable to complete operation \
                        state.set(entity_name={entity_name}, \
                        value={value}, \
                        new_attributes={new_attributes}, \
                        kwargs = **{kwargs})")
            return False

    def get_state(self, entity_name):
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

    def log_info(self, message):
        log.info(f'{self.log_id()}: {message}')

    def log_error(self, message):
        log.error(f'{self.log_id()}: {message}')

    def log_warning(self, message):
        log.warning(f'{self.log_id()}: {message}')

    def log_debug(self, message):
        if DEBUG_AS_INFO:
            log.info(f'{self.log_id()} DEBUG: {message}')
        else:
            log.debug(f'{self.log_id()}: {message}')

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




class TestInterpreter:

    def __init__(self):
        pass

    def set_state(self, entity_name, value=None, new_attributes=None, kwargs):
        self.log_info"state.set(entity_name={entity_name}, \
                            value={value}, \
                            new_attributes={new_attributes}, \
                            kwargs = **{kwargs})")
        return True

    def get_state(self, entity_name):
        self.log_info(f"Getting State of {entity_name}")
        return 1

    def call_service(self, domain, service_name, kwargs):
        self.log_info(f"service.call({domain}, {service_name}, **{kwargs}))")
        return True

    def sleep(self,seconds):
        self.log_info(f"task.sleep({seconds}))")

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

    def log_info(self, message):
        print(f'INFO: {message}')

    def log_error(self, message):
        log.error(f'ERROR: {message}')

    def log_warning(self, message):
        log.warning(f'WARNING:  {message}')

    def log_debug(self, message):
        if DEBUG_AS_INFO:
            log.info(message)
        else:
            log.debug(message)