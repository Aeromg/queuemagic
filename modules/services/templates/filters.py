import re


def _mobile_phone(value):
    if len(value) == 11:
        return '+{0} {1} {2}-{3}-{4}'.format(value[0], value[1:4], value[4:7], value[7:9], value[9:])
    else:
        return value


def _office_phone(value):
    if len(value) == 11:
        if value[0] == '7':
            return '({0}) {1}-{2}-{3}'.format(value[1:4], value[4:7], value[7:9], value[9:])
        else:
            return '+{0} ({1}) {2}'.format(value[0], value[1:4], value[4:])
    else:
        return value


def phone(value, mobile=False):
    value = str(value)
    value = ''.join(re.findall('\d', value))

    if mobile:
        return _mobile_phone(value)
    else:
        return _office_phone(value)


def camel_case(value):
    return value[0].lower() + value[1:]