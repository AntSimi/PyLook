import logging
import uuid
import json
from copy import deepcopy


logger = logging.getLogger("pylook")


class PyLookEncoder(json.JSONEncoder):
    INTERN_ATTR = ("building_options", "help", "id", "init_value")

    def default(self, o):
        dump = {k: v for k, v in o.__dict__.items() if k not in self.INTERN_ATTR}
        dump["__type__"] = o.__class__.__name__
        return dump


def as_pylook_object(dct):
    object_type = dct.get("__type__", None)
    for obj in (FigureSet, Figure, GeoSubplot, SimpleSubplot, Method, Data, Legend):
        if obj.__name__ == object_type:
            new_obj = obj()
            new_obj.appends(*dct["child"])
            for k, v in dct.items():
                if k in ("__type__", "child"):
                    continue
                setattr(new_obj, k, v)
            return new_obj
    return dct


class Choices(list):
    def __init__(self, *choices, default=None):
        super().__init__(choices)
        self.default = self[0] if default is None else default

    def summary(self, shorten=False):
        if shorten and len(self) > 10:
            return ", ".join(self[:6]) + ", ..."
        return ", ".join(self)

    @classmethod
    def from_generator(cls, generator, default=None):
        pass


class Bool(Choices):
    def __init__(self):
        super().__init__("True", "False")


class FBool(Bool):
    def __init__(self):
        super().__init__()
        self.default = self[1]


class Option(dict):
    pass


class Base:
    __slot__ = (
        "current_value",
        "init_value",
        "child",
        "help",
        "id",
        "building_options",
    )

    COLORS = ("'r'", "'b'", "'y'", "'g'", "'k'", "'c'", "'w'", "'olive'")
    COLOR = Choices("'None'", *COLORS)
    COLOR_K = Choices("'k'", *COLORS)
    FONTSIZE = Choices(
        "None",
        "'xx-small'",
        "'x-small'",
        "'small'",
        "'medium'",
        "'large'",
        "'x-large'",
        "'xx-large'",
    )
    FONTNAME = Choices("'monospace'", "'serif'", "'fantasy'",)
    FONTWEIGHT = Choices("'normal'", "'bold'", "'heavy'", "'light'")
    FONTSTYLE = Choices("'normal'", "'italic'")
    LINESTYLE = Choices("'-'", "'--'", "'-.'")

    def __init__(self):
        super().__init__()
        self.child = list()
        self.start_current_value()
        self.id = uuid.uuid1().int
        self.building_options = tuple()

    def __new__(cls):
        return super().__new__(cls)

    def save(self, filename):
        logger.debug(f"Object will be save in {filename}")
        with open(filename, "w") as f:
            json.dump(
                self, f, cls=PyLookEncoder, sort_keys=True, indent=4, ensure_ascii=False
            )

    @classmethod
    def with_options(cls, options):
        obj = cls()
        obj.update_options(obj.options, options)
        return obj

    @classmethod
    def update_options(cls, new_options, options):
        for k, v in options.items():
            if isinstance(v, dict):
                cls.update_options(new_options[k], v)
            else:
                new_options[k] = v

    def copy(self):
        new = self.__new__(self.__class__)
        new.child = [child.copy() for child in self.child]
        new.init_value = deepcopy(self.init_value)
        new.current_value = deepcopy(self.current_value)
        new.help = self.help
        new.id = self.id
        new.building_options = self.building_options
        return new

    def start_current_value(self):
        self.current_value = self.copy_options(self.init_value)

    @classmethod
    def copy_options(cls, options):
        new_options = dict()
        for k, v in options.items():
            if isinstance(v, Choices):
                v = v.default
            if isinstance(v, dict):
                v = cls.copy_options(v)
            new_options[k] = v
        return new_options

    @property
    def options_names(self):
        return list(self.current_value.keys())

    def get_option(self, name, evaluate=True):
        if evaluate:
            return eval(self.current_value[name])
        else:
            return self.current_value[name]

    @property
    def options(self):
        return self.current_value

    def __iter__(self):
        for i in self.child:
            yield i

    def pop_childs(self):
        childs = self.child
        self.child = list()
        return childs

    def append(self, elt):
        self.child.append(elt)

    def appends(self, *elt):
        self.child.extend(elt)

    def __str__(self):
        return self.summary(full=False, compress=True)

    def _repr_html_(self):
        text = self.summary(full=False, color_bash=False, html=True)
        return f"<pre>{text}</pre>"

    @property
    def known_children(self):
        return []

    @classmethod
    def summary_options(cls, options, init_options, compress=False, only_modify=False):
        if len(options):
            elts = list()
            keys = list(options.keys())
            keys.sort()
            for k in keys:
                v = options[k]
                v_init = init_options[k]
                v_dict = isinstance(v, dict)
                if v_dict:
                    v = cls.summary_options(v, v_init, compress, only_modify)
                    if v is None:
                        continue
                    v = v.replace("\n", "\n  | ")
                if compress:
                    if v_dict:
                        elts.append(f"\n{k}: {v}\n")
                    else:
                        if v == v_init and only_modify:
                            continue
                        elts.append(f"{k}: {v}")
                else:
                    elts.append(f"{k:8}: {v}")
            if compress:
                if only_modify and len(elts) == 0:
                    return None
                out = "\n" + " /".join(elts).replace("\n /", "\n").replace("/\n", "\n")
                return out.replace("\n\n", "\n")
            else:
                return "\n" + "\n".join(elts)
        else:
            return ""

    def summary(self, color_bash=True, full=True, extra_info="", html=True, **kwargs):
        summaries = list()
        for child in self:
            summaries.append(child.summary(color_bash, full, **kwargs))
        if len(summaries):
            synthesis = "\n    " + "\n".join(summaries).replace("\n", "\n    ")
        else:
            synthesis = ""
        if color_bash:
            c = self.BASH_COLOR
            c_escape = "\033[0;0m"
        elif html:
            c = f'<span style="color:{self.QT_COLOR}";>'
            c_escape = "</span>"
        else:
            c = c_escape = ""
        options = self.summary_options(
            self.options, self.copy_options(self.init_value), **kwargs
        )
        if options is None:
            options = ""
        else:
            options = options.replace("\n", "\n      | ")
        sup = f" ({self.id})" if full else ""
        sup += extra_info
        return f"{c}{self.__class__.__name__}{sup}{c_escape}{options}{synthesis}"

    @property
    def name(self):
        raise Exception("must be define")

    def build(self, *args, **kwargs):
        raise Exception("must be define")

    def build_child(self, parent, ids=None):
        for item in self:
            if ids is not None and item.id not in ids:
                continue
            child = item.build(parent)
            parent.child_id[child.id] = child

    def get_set(self, item, k):
        if k in self.building_options:
            logger.debug(f"{self.__class__.__name__} : only for building : {k}")
            return None, None
        set_func = getattr(item, f"set_{k}", None)
        get_func = getattr(item, f"get_{k}", None)
        if set_func is None and hasattr(item, "has_") and item.has_cbr(k):
            set_func, get_func = lambda value: item.set_cbr(k, value), lambda: item.get_cbr(k)
        if set_func is None or get_func is None:
            logger.warning(
                f"{self.__class__.__name__} : set ({set_func}) or/and get ({get_func}) doesn't exist for {k}"
            )
            return None, None
        return set_func, get_func

    def apply_options(self, item, options, init_options):
        for k, v in options.items():
            v_ = init_options[k]
            is_option = isinstance(v_, Option)
            if isinstance(v, dict) and not is_option:
                self.apply_options(item, v, v_)
                continue
            set_func, get_func = self.get_set(item, k)
            if set_func is None:
                continue
            new_value = self.effective_value(v)
            current_value = get_func()
            if type(new_value) != type(current_value) or current_value != new_value:
                logger.trace(f"We will set {k} with {v} on {item}")
                if is_option:
                    set_func(**new_value)
                else:
                    set_func(new_value)

    @classmethod
    def effective_value(cls, value):
        if isinstance(value, dict):
            out = dict()
            for k, v in value.items():
                out[k] = cls.effective_value(v)
            return out
        else:
            return eval(value)

    def update(self, item, recursive=True):
        self.apply_options(item, self.options, self.init_value)
        if recursive:
            for child in self:
                if child.id not in item.child_id:
                    self.build_child(item, [child.id])
                child.update(item.child_id[child.id], recursive=recursive)

    @classmethod
    def fontdict(cls):
        return dict(
            fontsize=cls.FONTSIZE,
            color=cls.COLOR_K,
            family=cls.FONTNAME,
            weight=cls.FONTWEIGHT,
            style=cls.FONTSTYLE,
        )
