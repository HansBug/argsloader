# distutils:language=c++
# cython:language_level=3

from libcpp cimport bool

cdef class _CResultInfo:
    cdef object _value
    cdef bool _is_valid
    cdef object _error

    cdef bool is_valid(self)
    cdef object value(self)
    cdef object error(self)

cdef _CResultInfo _c_res_valid(object v)
cdef _CResultInfo _c_res_error(object e)

cdef class _CBaseUnit:
    cpdef _CResultInfo _validate(self, object v)

cdef object _c_unit_validate(object v, _CBaseUnit u)

cdef class _CUnitWrapper:
    cdef _CBaseUnit _unit
