from services.service import Service


class Cache(Service):
    def __init__(self, config, service_resolver):
        Service.__init__(self, config=config, service_resolver=service_resolver)

    def try_get(self, key):
        raise Exception('Method must be overridden')

    def set(self, obj, key):
        raise Exception('Method must be overridden')