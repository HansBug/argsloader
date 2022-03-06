from operator import itemgetter
from textwrap import indent

from ..utils import format_tree


def _prefix_indent(prefix, text):
    txt = indent(text, len(prefix) * " ")
    return prefix + txt[len(prefix):]


class _ITreeFormat:
    def _rinfo(self):
        raise NotImplementedError  # pragma: no cover

    def __repr__(self):
        return format_tree(self._get_format_unit(self, {}, ()), itemgetter(0), itemgetter(1))

    @classmethod
    def _cname(cls):
        return cls.__name__

    @classmethod
    def _get_format_unit(cls, v, id_pool, curpath):
        if isinstance(v, _ITreeFormat):
            attached, _children = v._rinfo()
            attached_content = ", ".join("%s: %s" % (k, repr(v_)) for k, v_ in attached)
            title = f'<{v._cname()}{" " + attached_content if attached else ""}>'
            children = [(k, c) for k, c in _children]
        elif isinstance(v, dict):
            title = f'{type(v).__name__}({", ".join(map(str, v.keys()))})'
            children = [(k, c) for k, c in v.items()]
        elif isinstance(v, (list, tuple)):
            title = f'{type(v).__name__}({len(v)})'
            children = [(i, c) for i, c in enumerate(v)]
        else:
            return repr(v), []

        cs = [cls._get_format_unit(c, id_pool, (*curpath, k)) for k, c in children]
        return title, [(_prefix_indent(f'{k} --> ', ctitle), cchild)
                       for (k, _), (ctitle, cchild) in zip(children, cs)]
