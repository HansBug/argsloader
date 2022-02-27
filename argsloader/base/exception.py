from hbutils.model import asitems, accessor, visual


@visual(show_id=True)
@accessor(readonly=True)
@asitems(['message', 'unit', 'value', 'info'])
class ParseException(Exception):
    def __init__(self, message, unit, value, info=None):
        Exception.__init__(self, (message, unit, value, info))
        self.__message = message
        self.__unit = unit
        self.__value = value
        self.__info = info
