from services.service import Service


class DomainKeysSigner(Service):
    def __init__(self, config, service_resolver):
        Service.__init__(self, config=config, service_resolver=service_resolver)

    def get_sign(self, email, sender=None):
        raise Exception('Method must be overridden')