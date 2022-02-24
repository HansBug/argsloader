# distutils:language=c++
# cython:language_level=3

import cython
from libcpp cimport bool

cdef class _CResultInfo:
    def __cinit__(self, bool is_valid, object value, object error):
        self._is_valid = is_valid
        self._value = value
        self._error = error

    cdef inline bool is_valid(self):
        return self._is_valid

    cdef inline object value(self):
        return self._value

    cdef inline object error(self):
        return self._error

cdef inline _CResultInfo _c_res_valid(object v):
    return _CResultInfo(True, v, None)

cdef inline _CResultInfo _c_res_error(object e):
    return _CResultInfo(False, None, e)

cdef class _CBaseUnit:
    cpdef _CResultInfo _validate(self, object v):
        raise NotImplementedError  # pragma: no cover

cdef inline object _c_unit_validate(object v, _CBaseUnit u):
    cdef _CResultInfo _res = u._validate(v)
    if _res.is_valid():
        return _res.value()
    else:
        raise _res.error()

cdef class _CUnitWrapper:
    def __cinit__(self, _CBaseUnit unit):
        self._unit = unit

    @cython.binding(True)
    def __call__(self, object v):
        return _c_unit_validate(v, self._unit)
