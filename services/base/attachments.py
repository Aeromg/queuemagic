from services.service import Service


class Attachments(Service):
    def __init__(self, config, service_resolver):
        Service.__init__(self, config=config, service_resolver=service_resolver)

    def inject_path(self, email, path, name=None):
        raise Exception('Method must be overridden')

    def inject_fd(self, email, fd, name):
        raise Exception('Method must be overridden')