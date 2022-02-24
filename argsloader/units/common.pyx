# distutils:language=c++
# cython:language_level=3

import cython

from .base cimport _CResultInfo, _c_res_valid, _c_res_error, _CUnitWrapper

cdef class _IsTypeUnit(_CBaseUnit):
    def __cinit__(self, type type_):
        self._type = type_

    cpdef _CResultInfo _validate(self, object v):
        if isinstance(v, self._type):
            return _c_res_valid(v)
        else:
            return _c_res_error(TypeError(f"{repr(self._type)} expected, but {repr(type(v))} given actually."))

@cython.binding(True)
cpdef inline _CUnitWrapper is_type(type t):
    return _CUnitWrapper(_IsTypeUnit(t))

cdef class _ToTypeUnit(_CBaseUnit):
    def __cinit__(self, type type_):
        self._type = type_

    cpdef _CResultInfo _validate(self, object v):
        return _c_res_valid(self._type(v))

@cython.binding(True)
cpdef inline _CUnitWrapper to_type(type t):
    return _CUnitWrapper(_ToTypeUnit(t))
