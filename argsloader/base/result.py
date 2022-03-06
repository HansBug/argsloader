from enum import IntEnum, unique
from typing import Optional, Union, Iterator, Tuple

import enum_tools
from hbutils.collection import nested_walk
from hbutils.model import get_repr_info, int_enum_loads, raw_support, asitems, hasheq

from .exception import ParseError, MultipleParseError, SkippedParseError
from .value import PValue

raw_res, unraw_res, _RawResProxy = raw_support(
    lambda x: isinstance(x, (dict, list, tuple)),
    'raw_res', 'unraw_res', '_RawResProxy',
)
_NoneType = type(None)


class _BaseChildProxy:
    def __init__(self, children):
        self._children = children
        if not isinstance(self._children, (dict, list, tuple, _NoneType)):
            raise ValueError(f'Invalid type of children - {repr(type(children))}.')

    def __getitem__(self, item) -> Union['ParseResultChildProxy', object]:
        """
        Get item from children.

        :param item: Name of item, can be a string or an integer.
        :return: Item got, can be a :class:`argsloader.base.result.ParseResultChildProxy` or an object.
        """
        if self._children is not None:
            child = self._children[item]
            if isinstance(child, (dict, list, tuple)):
                return ParseResultChildProxy(child)
            else:
                return unraw_res(child)
        else:
            raise KeyError(f'Key {repr(item)} not found.')

    def __contains__(self, item) -> bool:
        """
        Check if this children collection contain the given ``item``.

        :param item: Item to be checked.
        :return: Item is contained or not.
        """
        if isinstance(self._children, dict):
            return item in self._children
        elif isinstance(self._children, (list, tuple)):
            return item in range(len(self._children))
        else:
            return False

    def keys(self):
        """
        Get collection of keys, can be a collection of string or integer.

        :return: Collection of keys.
        """
        if isinstance(self._children, dict):
            return self._children.keys()
        elif isinstance(self._children, (tuple, list)):
            return range(len(self._children))
        else:
            return []

    def items(self) -> Iterator[Tuple[Union[int, str], Union['ParseResultChildProxy', object]]]:
        """
        Get collection of pairs.

        :return: Collection of pairs
        """
        if isinstance(self._children, dict):
            for key, value in self._children.items():
                if isinstance(value, (dict, list, tuple)):
                    yield key, ParseResultChildProxy(value)
                else:
                    yield key, unraw_res(value)
        elif isinstance(self._children, (tuple, list)):
            for i, value in enumerate(self._children):
                if isinstance(value, (dict, list, tuple)):
                    yield i, ParseResultChildProxy(value)
                else:
                    yield i, unraw_res(value)
        else:
            return iter([])


@hasheq()
@asitems(['_children'])
class ParseResultChildProxy(_BaseChildProxy):
    """
    Overview:
        Proxy class of children, only used for accessing.
    """

    def __init__(self, children):
        """
        Constructor of class :class:`argsloader.base.result.ParseResultChildProxy`.

        :param children: Child structure.
        """
        _BaseChildProxy.__init__(self, children)


@enum_tools.documentation.document_enum
@int_enum_loads(name_preprocess=str.upper)
@unique
class ResultStatus(IntEnum):
    SKIPPED = 0  # doc: Unit processing is skipped.
    SUCCESS = 1  # doc: Unit processing is not skipped and succeed.
    ERROR = 2  # doc: Unit processing is not skipped and error occurred.

    @property
    def valid(self):
        """
        Validity, which means it is processed and succeed.
        """
        return self == self.SUCCESS

    @property
    def processed(self):
        """
        Processed or not, which means this process is not skipped.
        """
        return self != self.SKIPPED


@enum_tools.documentation.document_enum
@int_enum_loads(name_preprocess=str.upper)
@unique
class ErrMode(IntEnum):
    FIRST = 1  # doc: Raise first error.
    TRY_ALL = 2  # doc: Try raise all errors, if only one error is found, raise it.
    ALL = 3  # doc: Raise all errors, with :class:`argsloader.base.exception.MultipleParseError`.


class ParseResult(_BaseChildProxy):
    """
    Overview:
        Result of one parsing process.
    """

    def __init__(self, input_: Optional[PValue], unit,
                 status, result: Optional[PValue],
                 error: Optional[ParseError], children=None):
        """
        Constructor of class :class:`argsloader.base.result.ParseResult`.

        :param input\\_: Input value object.
        :param unit: Unit to do parsing process.
        :param status: Status of result.
        :param result: Result object of parsing process, should be ``None`` when ``status`` is not valid.
        :param error: Error object of parsing process, should be ``None`` when no error, skipped or \
            the error is caused by child leveled unit.
        :param children: Children information, should be structure like ``dict``, ``list`` or ``tuple``.
        """
        _BaseChildProxy.__init__(self, children)

        self.__input = input_
        self.__unit = unit

        self.__status: ResultStatus = ResultStatus.loads(status)
        self.__result = result if self.__status.valid else None
        self.__error = error if self.__status.processed else None

    def __repr__(self):
        return get_repr_info(self.__class__, [
            ('input', lambda: self.input, lambda: self.__status.processed),
            ('status', lambda: self.__status.name),
            ('result', lambda: self.result, lambda: self.__status.valid),
            (
                'error',
                lambda: self.error.message if self.__error is not None else '<caused by prerequisites>',
                lambda: self.__status.processed and not self.__status.valid,
            ),
        ])

    @property
    def input(self) -> Optional[PValue]:
        """
        Input value object.
        """
        return self.__input

    @property
    def unit(self):
        """
        Unit to do parsing process.
        """
        return self.__unit

    @property
    def status(self) -> ResultStatus:
        """
        Status of result.
        """
        return self.__status

    @property
    def result(self) -> Optional[PValue]:
        """
        Result object of parsing process, should be ``None`` when ``status`` is not valid.
        """
        return self.__result

    @property
    def error(self) -> Optional[ParseError]:
        """
        Error object of parsing process, should be ``None`` when no error, \
            skipped or the error is caused by child leveled unit.
        """
        return self.__error

    def _iter_errors(self) -> Iterator[Tuple[PValue, ParseError]]:
        if self.__status.processed and not self.__status.valid:
            if self.error is not None:
                yield self.input, self.error

            for _, v in nested_walk(self._children):
                if isinstance(v, ParseResult):
                    yield from v._iter_errors()

    def _first_error(self):
        try:
            pval, error = next(self._iter_errors())
            return error
        except StopIteration:  # pragma: no cover
            return None  # pragma: no cover

    def _try_full_error(self):
        all_errors = list(self._iter_errors())
        if len(all_errors) > 1:
            return MultipleParseError(all_errors)
        elif len(all_errors) == 1:
            pval, error = all_errors[0]
            return error
        else:
            return None  # pragma: no cover

    def _full_error(self):
        all_errors = list(self._iter_errors())
        if all_errors:
            return MultipleParseError(all_errors)
        else:
            return None  # pragma: no cover

    def act(self, err_mode):
        """
        Act this result:

        - If success, return value as result.
        - If error, raise the error as the ``err_mode`` saied.
        - If skipped, raise :class:`argsloader.base.result.SkippedParseError`.

        :param err_mode: Error mode.
        """
        err_mode = ErrMode.loads(err_mode)
        if self.__status.processed:
            if self.__status.valid:
                return self.result.value
            else:
                if err_mode == ErrMode.FIRST:
                    raise self._first_error()
                elif err_mode == ErrMode.TRY_ALL:
                    raise self._try_full_error()
                elif err_mode == ErrMode.ALL:
                    raise self._full_error()
        else:
            raise SkippedParseError(self)
