from services.base.speller import Speller

try:
    import simplejson as json
except ImportError:
    import json

# trying to play cross-version way.
try:
    # noinspection PyUnresolvedReferences
    from urllib import request, error
    from urllib.error import HTTPError
    from urllib.parse import quote
except ImportError:
    import urllib2 as request
    from urllib2 import HTTPError
    from urllib import quote


class YandexSpeller(Speller):
    def __init__(self, config, service_resolver):
        Speller.__init__(self, config=config, service_resolver=service_resolver)

    def fix(self, text, is_html=False):
        resp = request.urlopen(
            'http://speller.yandex.net/services/spellservice.json/checkText?ie=%s&text=%s'
            % ('utf-8', quote(text.encode('utf-8'))))

        json_data = json.loads(resp.read().decode('utf-8'))

        if len(json_data) > 0:
            fixed = u''
            fixed_offset = 0
        else:
            return text

        for data in json_data:
            fixed += text[fixed_offset:data['pos']] + (data['s'][0] if data['s'] else data['word'])
            fixed_offset = data['pos'] + data['len']
        fixed += text[fixed_offset:]

        return fixed