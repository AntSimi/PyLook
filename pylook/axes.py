import logging
import matplotlib.transforms as mtransforms
import matplotlib.axes
import matplotlib.axis as maxis
import matplotlib.ticker as mticker
import matplotlib.gridspec as mgridspec
import os
import os.path
import pyproj
import numpy
import numba
from . import coast


logger = logging.getLogger("pylook")


class PyLookAxes(matplotlib.axes.Axes):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback_axes_properties = None
        self.child_id = dict()

    def set_callback_axes_properties(self, callback):
        self.callback_axes_properties = callback

    def set_grid(self, state):
        return self.grid(state)

    def get_grid(self):
        return self.xaxis._gridOnMajor

    def set_position(self, *args, **kwargs):
        # TODO maybe compare get_position result with args before to apply
        if type(args[0]) is int:
            nb_x, nb_y, n = tuple(map(int, str(args[0])))
            i, j = (n - 1) // nb_y, (n - 1) % nb_y
            logger.trace(
                f"Axes will be set with (i={i}, j={j}) for a grid ({nb_x}, {nb_y})"
            )
            bbox = mgridspec.GridSpec(nb_x, nb_y)[i, j].get_position(self.figure)
            args = ((bbox.x0, bbox.y0, bbox.width, bbox.height),)
        elif len(args[0]) == 3:
            nb_x, nb_y, n = args[0]
            i, j = (n - 1) // nb_x, (n - 1) % nb_y
            bbox = mgridspec.GridSpec(nb_x, nb_y)[i, j].get_position(self.figure)
            args = ((bbox.x0, bbox.y0, bbox.width, bbox.height),)
        return super().set_position(*args, **kwargs)

    def pcolormesh(self, *args, **kwargs):
        grid_state = self.get_grid()
        mappable = super().pcolormesh(*args, **kwargs)
        self.set_grid(grid_state)
        return mappable

    def update_pylook_mappable(self):
        logger.debug("Start mappable update")
        if not hasattr(self, "child_id"):
            return
        for k, v in self.child_id.items():
            v.remove()
            self.child_id[k] = v.pylook_object.build(self)
            v.pylook_object.update(self.child_id[k])


class SimpleAxes(PyLookAxes):
    name = "standard"


class MapAxes(PyLookAxes):

    GEO_ELT = ("coast", "border", "river")

    def __init__(self, *args, **kwargs):
        self.default = dict(
            coast=dict(flag=True, color="gray"),
            border=dict(flag=False, color="r"),
            river=dict(flag=False, color="b"),
        )
        self.geo_flag = dict()
        self.geo_kwargs = dict()
        self._geo_object = dict()
        self.geo_mappable = dict()
        for geo in self.GEO_ELT:
            self.geo_flag[geo] = kwargs.pop(geo, self.default[geo]["flag"])
            self._geo_object[geo] = dict()
            self.geo_kwargs[geo] = dict(linewidth=0.25, color="k")
            self.geo_mappable[geo] = None
        super().__init__(*args, **kwargs)

    def has_(self, key):
        return (
            key.startswith("coast")
            or key.startswith("border")
            or key.startswith("river")
        )

    def set_(self, key, value):
        keys = key.split("_")
        if len(keys) == 1:
            self.geo_flag[key] = value
            self.update_geo(key)
        else:
            geo, option = keys
            if self.geo_mappable[geo] is not None:
                if value is "None":
                    value = self.default[geo][option]
                set_func = getattr(self.geo_mappable[geo], f"set_{option}")
                set_func(value)
                self.geo_kwargs[geo][option] = value

    def get_(self, key):
        keys = key.split("_")
        if len(keys) == 1:
            return self.geo_flag[keys[0]]
        else:
            geo, option = keys
            get_func = getattr(self.geo_mappable[geo], f"get_{option}", None)
            if get_func is None:
                return None
            return get_func()

    @property
    def gshhs_resolution(self):
        (x0, x1), (y0, y1) = self.coordinates_bbox
        r = (y1 - y0) / self.bbox.height
        if r > 0.3:
            return "c"
        elif r > 0.05:
            return "l"
        elif r > 0.01:
            return "i"
        elif r > 0.002:
            return "h"
        else:
            return "f"

    def geo_object(self, geo):
        pattern = dict(coast="GSHHS").get(geo, geo)
        if geo == "coast":
            class_ = coast.CoastFile
        else:
            class_ = coast.BorderRiverFile
        if "GSHHS_DATA" in os.environ:
            res = self.gshhs_resolution
            if res not in self._geo_object[geo]:
                self._geo_object[geo][res] = class_(
                    f'{os.environ["GSHHS_DATA"]}/binned_{pattern}_{res}.nc'
                )
            return self._geo_object[geo][res]
        else:
            res = "l"
            if res not in self._geo_object[geo]:
                fwd = os.path.join(os.path.dirname(__file__))
                self._geo_object[geo][res] = class_(
                    f"{fwd}/gshhs_backup/binned_{pattern}_{res}.nc"
                )
            return self._geo_object[geo][res]

    def update_geo(self, geo):
        xlim, ylim = self.coordinates_bbox
        if self.geo_mappable[geo] is not None:
            self.geo_mappable[geo].remove()
            self.geo_mappable[geo] = None
        if self.geo_flag[geo]:
            self.geo_mappable[geo] = self.add_collection(
                self.geo_object(geo).lines(
                    xlim[0], ylim[0], xlim[1], ylim[1], **self.geo_kwargs[geo]
                )
            )

    def update_env(self):
        for geo in self.GEO_ELT:
            self.update_geo(geo)

    def update_renderer(self):
        self.update_pylook_mappable()
        self.update_env()

    def end_pan(self, *args, **kwargs):
        super().end_pan(*args, **kwargs)
        self.update_renderer()
        self.emit_axes_properties()

    def _set_view_from_bbox(self, *args, **kwargs):
        """call after zoom action
        """
        result = super()._set_view_from_bbox(*args, **kwargs)
        self.update_renderer()
        self.emit_axes_properties()
        return result

    @property
    def coordinates_bbox(self):
        raise Exception("Must be define")

    def emit_axes_properties(self):
        kwargs = dict()
        kwargs["llcrnrlon"], kwargs["urcrnrlon"] = self.get_xlim()
        kwargs["llcrnrlat"], kwargs["urcrnrlat"] = self.get_ylim()
        if self.callback_axes_properties:
            logger.trace(f"We will notify all axes from axes {self.id} with : {kwargs}")
            self.callback_axes_properties(self.id, kwargs)


class PlatCarreAxes(MapAxes):

    name = "plat_carre"

    def __init__(self, *args, **kwargs):
        llcrnrlon = kwargs.pop("llcrnrlon", -180)
        urcrnrlon = kwargs.pop("urcrnrlon", 180)
        llcrnrlat = kwargs.pop("llcrnrlat", -180)
        urcrnrlat = kwargs.pop("urcrnrlat", 180)
        self.maximize_screen = kwargs.pop("maximize_screen", False)
        super().__init__(*args, **kwargs)
        self.set_aspect("equal")
        self.set_xlim(llcrnrlon, urcrnrlon)
        self.set_ylim(llcrnrlat, urcrnrlat)
        self.update_env()

    @property
    def coordinates_bbox(self):
        return self.get_xlim(), self.get_ylim()

    def set_ylim(self, *bounds):
        if len(bounds) == 1:
            y0, y1 = bounds[0]
        else:
            y0, y1 = bounds
        y0, y1 = max(y0, -90), min(y1, 90)
        super().set_ylim(y0, y1)

    def set_axes_with_message(self, properties):
        x0, x1 = properties.get("llcrnrlon", None), properties.get("urcrnrlon", None)
        if x0 is not None and x1 is not None:
            self.set_xlim(x0, x1)
        y0, y1 = properties.get("llcrnrlat", None), properties.get("urcrnrlat", None)
        if y0 is not None and y1 is not None:
            self.set_ylim(y0, y1)
        self.update_renderer()


class ProjTransform(mtransforms.Transform):
    input_dims = 2
    output_dims = 2

    def __init__(self, name, lon0, lat0, ellps, inverted=False):
        self.name = name
        self.lon0, self.lat0 = lon0, lat0
        self.ellps = ellps
        self.proj = pyproj.Proj(
            proj=self.name, lat_0=self.lat0, lon_0=self.lon0, ellps=self.ellps
        )
        self.invalid = self.proj(numpy.nan, numpy.nan, inverse=inverted)[0]
        self.flag_inverted = inverted
        super().__init__(self)

    def transform_non_affine(self, vertices):
        return reduce_array(
            *self.proj(vertices[:, 0], vertices[:, 1], inverse=self.flag_inverted),
            invalid=self.invalid,
        )

    def inverted(self):
        return self.__class__(
            self.name, self.lon0, self.lat0, self.ellps, inverted=~self.flag_inverted
        )


@numba.njit
def reduce_array(xs, ys, invalid):
    """Could add parameter to simplify path"""
    nb_in = xs.shape[0]
    if nb_in < 10:
        # Only replace of invalid, merge and transpose
        vertice = numpy.empty((nb_in, 2), dtype=xs.dtype)
        for i in range(nb_in):
            if xs[i] == invalid or ys[i] == invalid:
                vertice[i, 0] = numpy.nan
                vertice[i, 1] = numpy.nan
            else:
                vertice[i, 0] = xs[i]
                vertice[i, 1] = ys[i]
    else:
        # Remove all consecutive invalid value to reduce array
        m = numpy.empty(nb_in, dtype=numpy.bool_)
        previous_nan = False
        for i in range(nb_in):
            x, y = xs[i], ys[i]
            if x == invalid or y == invalid or numpy.isnan(x) or numpy.isnan(y):
                if previous_nan:
                    m[i] = False
                else:
                    xs[i] = numpy.nan
                    ys[i] = numpy.nan
                    m[i] = True
                    previous_nan = True
            else:
                m[i] = True
                previous_nan = False
        nb = m.sum()
        vertice = numpy.empty((nb, 2), dtype=xs.dtype)
        i_ = 0
        for i in range(nb_in):
            if m[i] == 1:
                vertice[i_, 0] = xs[i]
                vertice[i_, 1] = ys[i]
                i_ += 1
    return vertice


class TransformAxes(MapAxes):
    def _get_core_transform(self, reoslution):
        return ProjTransform(self.name, self.lon0, self.lat0, self.ellps)

    def _get_affine_transform(self):
        return mtransforms.Affine2D().scale(0.5 / self.scale_norm).translate(0.5, 0.5)

    @property
    def scale_norm(self):
        return ProjTransform(self.name, 0, 0, self.ellps).transform_point((0, 90))[1]

    RESOLUTION = 75

    def _init_axis(self):
        self.xaxis = maxis.XAxis(self)
        self.yaxis = maxis.YAxis(self)
        # Do not register xaxis or yaxis with spines -- as done in
        # Axes._init_axis() -- until GeoAxes.xaxis.cla() works.
        # self.spines['geo'].register_axis(self.yaxis)
        self._update_transScale()

    def cla(self):
        super().cla()
        self.yaxis.set_major_formatter(mticker.NullFormatter())
        self.xaxis.set_major_formatter(mticker.NullFormatter())
        self.set_longitude_grid(15)
        # self.set_latitude_grid(15)
        # self.set_longitude_grid_ends(75)

    def _set_lim_and_transforms(self):
        self.transProjection = self._get_core_transform(self.RESOLUTION)

        self.transAffine = self._get_affine_transform()

        self.transAxes = mtransforms.BboxTransformTo(self.bbox)

        # The complete data transformation stack -- from data all the
        # way to display coordinates
        self.transData = self.transProjection + self.transAffine + self.transAxes

        # This is the transform for longitude ticks.
        self._xaxis_pretransform = (
            mtransforms.Affine2D()
            .scale(1, self._longitude_cap * 2)
            .translate(0, -self._longitude_cap)
        )
        self._xaxis_transform = self._xaxis_pretransform + self.transData
        self._xaxis_text1_transform = (
            mtransforms.Affine2D().scale(1, 0)
            + self.transData
            + mtransforms.Affine2D().translate(0, 4)
        )
        self._xaxis_text2_transform = (
            mtransforms.Affine2D().scale(1, 0)
            + self.transData
            + mtransforms.Affine2D().translate(0, -4)
        )

        # This is the transform for latitude ticks.
        yaxis_stretch = mtransforms.Affine2D().scale(1, 1)
        yaxis_space = mtransforms.Affine2D().scale(1, 1.1)
        self._yaxis_transform = yaxis_stretch + self.transData
        yaxis_text_base = (
            yaxis_stretch
            + self.transProjection
            + (yaxis_space + self.transAffine + self.transAxes)
        )
        self._yaxis_text1_transform = yaxis_text_base + mtransforms.Affine2D().translate(
            -8, 0
        )
        self._yaxis_text2_transform = yaxis_text_base + mtransforms.Affine2D().translate(
            8, 0
        )

    def get_xaxis_transform(self, which="grid"):
        assert which in ["tick1", "tick2", "grid"]
        return self._xaxis_transform

    def get_xaxis_text1_transform(self, pad):
        return self._xaxis_text1_transform, "bottom", "center"

    def get_xaxis_text2_transform(self, pad):
        return self._xaxis_text2_transform, "top", "center"

    def get_yaxis_transform(self, which="grid"):
        assert which in ["tick1", "tick2", "grid"]
        return self._yaxis_transform

    def get_yaxis_text1_transform(self, pad):
        return self._yaxis_text1_transform, "center", "right"

    def get_yaxis_text2_transform(self, pad):
        return self._yaxis_text2_transform, "center", "left"

    def _gen_axes_spines(self):
        return {}

    def set_longitude_grid(self, degrees):
        grid = numpy.arange(-180 + degrees, 180, degrees)
        self.xaxis.set_major_locator(mticker.FixedLocator(grid))

    def set_latitude_grid(self, degrees):
        grid = numpy.arange(-90 + degrees, 90, degrees)
        self.yaxis.set_major_locator(mticker.FixedLocator(grid))

    def set_longitude_grid_ends(self, degrees):
        """
        Set the latitude(s) at which to stop drawing the longitude grids.
        """
        self._longitude_cap = degrees
        self._xaxis_pretransform.clear().scale(
            1.0, self._longitude_cap * 2.0
        ).translate(0.0, -self._longitude_cap)

    def get_data_ratio(self):
        return 1.0

    def can_zoom(self):
        return False

    def start_pan(self, x, y, button):
        self._pan_start = self.transData.inverted().transform_point((x, y))

    def drag_pan(self, button, key, x, y):
        pan_current = self.transData.inverted().transform_point((x, y))
        delta = self._pan_start - pan_current
        if numpy.isnan(delta).any():
            return
        self.go_to(self.lon0 + delta[0], self.lat0 + delta[1])

    def go_to(self, lon, lat):
        if self.lon0 != lon or self.lat0 != lat:
            self.lon0 = lon
            self.lat0 = lat
            self.transProjection.lon0 = lon
            self.transProjection.lat0 = lat
            self.transProjection.proj = pyproj.Proj(
                proj=self.name, lat_0=lat, lon_0=lon, ellps=self.ellps
            )
            return True
        return False


class OrthoAxes(TransformAxes):

    name = "ortho"

    def __init__(self, *args, **kwargs):
        self.lon0 = kwargs.pop("lon0", 50)
        self.lat0 = kwargs.pop("lat0", 50)
        self.ellps = "sphere"
        self._longitude_cap = 80
        super().__init__(*args, **kwargs)
        self.set_aspect("equal")
        self.update_env()

    @property
    def coordinates_bbox(self):
        return (-180, 180), (-90, 90)


def register_projection():
    import matplotlib.projections as mprojections

    for axes in (PlatCarreAxes, OrthoAxes, SimpleAxes):
        mprojections.register_projection(axes)
