from services.service import Service


class Speller(Service):
    def __init__(self, config, service_resolver):
        Service.__init__(self, config=config, service_resolver=service_resolver)

    def fix(self, text, is_html=False):
        raise Exception('Method must be overridden')