# distutils:language=c++
# cython:language_level=3

from .base cimport _CResultInfo, _CBaseUnit, _CUnitWrapper

cdef class _IsTypeUnit(_CBaseUnit):
    cdef type _type
    cpdef _CResultInfo _validate(self, object v)

cpdef _CUnitWrapper is_type(type t)

cdef class _ToTypeUnit(_CBaseUnit):
    cdef type _type
    cpdef _CResultInfo _validate(self, object v)

cpdef inline _CUnitWrapper to_type(type t)
