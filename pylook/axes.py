import matplotlib.transforms as mtransforms
import matplotlib.axes
import matplotlib.axis as maxis
import matplotlib.ticker as mticker
import os
import pyproj
import numpy 
from . import coast 


class PyLookAxes(matplotlib.axes.Axes):
    pass


class MapAxes(PyLookAxes):

    def __init__(self, *args, **kwargs):
        self._coast_object = dict()
        self.coast_mappable = None
        self.coast_flag = kwargs.pop('coast', True)
        super(MapAxes, self).__init__(*args, **kwargs)
        self.set_env()

    @property
    def gshhs_resolution(self):
        (x0, x1), (y0, y1) = self.coordinates_bbox
        r = (y1 - y0) / self.bbox.height
        if r > 0.3:
            return 'c'
        elif r > 0.05:
            return 'l'
        elif r > 0.01:
            return 'i'
        elif r > 0.002:
            return 'h'
        else:
            return 'f'

    @property
    def coast_object(self):
        res = self.gshhs_resolution
        if res not in self._coast_object:
            self._coast_object[res] = coast.CoastFile(f'{os.environ["GSHHS_DATA"]}/binned_GSHHS_{res}.nc')
        return self._coast_object[res]

    def update_env(self):
        xlim, ylim = self.coordinates_bbox
        if self.coast_mappable is not None:
            self.coast_mappable.remove()
            self.coast_mappable = None
        if self.coast_flag:
            self.coast_mappable = self.add_collection(
                self.coast_object.lines(
                    xlim[0], ylim[0], xlim[1], ylim[1],
                    linewidth=.25, color='k'
                    ))

    def set_env(self):
        # print(self.bbox)
        pass

    def end_pan(self, *args, **kwargs):
        super(MapAxes, self).end_pan(*args, **kwargs)
        self.update_env()
    

class PlatCarreAxes(MapAxes):

    name = 'plat_carre'
    def __init__(self, *args, **kwargs):
        llcrnrlon = kwargs.pop('llcrnrlon', -180)
        urcrnrlon = kwargs.pop('urcrnrlon', 180)
        llcrnrlat = kwargs.pop('llcrnrlat', -180)
        urcrnrlat = kwargs.pop('urcrnrlat', 180)
        super(PlatCarreAxes, self).__init__(*args, **kwargs)
        self.set_aspect('equal')
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
        super(PlatCarreAxes, self).set_ylim(y0, y1)


class ProjTransform(mtransforms.Transform):
    input_dims = 2
    output_dims = 2
    is_separable = False
    has_inverse = True

    def __init__(self, name, lon0, lat0, ellps, inverted=False):
        self.name = name
        self.lon0, self.lat0 = lon0, lat0
        self.ellps = ellps
        self.proj = pyproj.Proj(proj=self.name, lat_0=self.lat0, lon_0=self.lon0, ellps=self.ellps)
        self.flag_inverted = inverted
        super(ProjTransform, self).__init__(self)

    def transform_non_affine(self, vertices):
        invalid = self.proj(numpy.nan, numpy.nan)[0]
        coordinates = numpy.array(self.proj(vertices[:, 0], vertices[:, 1], inverse=self.flag_inverted))
        coordinates[coordinates == invalid] = numpy.nan
        return coordinates.T

    def inverted(self):
        return self.__class__(self.name, self.lon0, self.lat0, self.ellps, inverted=~self.flag_inverted)


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
        super(TransformAxes, self).cla()
        self.yaxis.set_major_formatter(mticker.NullFormatter())
        self.yaxis.set_major_formatter(mticker.NullFormatter())
        self.xaxis.set_major_formatter(mticker.NullFormatter())
        self.set_longitude_grid(15)
        self.set_latitude_grid(15)
        self.set_longitude_grid_ends(75)

    def _set_lim_and_transforms(self):
        self.transProjection = self._get_core_transform(self.RESOLUTION)

        self.transAffine = self._get_affine_transform()

        self.transAxes = mtransforms.BboxTransformTo(self.bbox)

        # The complete data transformation stack -- from data all the
        # way to display coordinates
        self.transData = \
            self.transProjection + \
            self.transAffine + \
            self.transAxes

        # This is the transform for longitude ticks.
        self._xaxis_pretransform = \
            mtransforms.Affine2D() \
            .scale(1, self._longitude_cap * 2) \
            .translate(0, -self._longitude_cap)
        self._xaxis_transform = \
            self._xaxis_pretransform + \
            self.transData
        self._xaxis_text1_transform = \
            mtransforms.Affine2D().scale(1, 0) + \
            self.transData + \
            mtransforms.Affine2D().translate(0, 4)
        self._xaxis_text2_transform = \
            mtransforms.Affine2D().scale(1, 0) + \
            self.transData + \
            mtransforms.Affine2D().translate(0, -4)

        # This is the transform for latitude ticks.
        yaxis_stretch = mtransforms.Affine2D().scale(1, 1)
        yaxis_space = mtransforms.Affine2D().scale(1, 1.1)
        self._yaxis_transform = \
            yaxis_stretch + \
            self.transData
        yaxis_text_base = \
            yaxis_stretch + \
            self.transProjection + \
            (yaxis_space + \
             self.transAffine + \
             self.transAxes)
        self._yaxis_text1_transform = \
            yaxis_text_base + \
            mtransforms.Affine2D().translate(-8, 0)
        self._yaxis_text2_transform = \
            yaxis_text_base + \
            mtransforms.Affine2D().translate(8, 0)

    def get_xaxis_transform(self, which='grid'):
        assert which in ['tick1', 'tick2', 'grid']
        return self._xaxis_transform

    def get_xaxis_text1_transform(self, pad):
        return self._xaxis_text1_transform, 'bottom', 'center'

    def get_xaxis_text2_transform(self, pad):
        return self._xaxis_text2_transform, 'top', 'center'

    def get_yaxis_transform(self, which='grid'):
        assert which in ['tick1', 'tick2', 'grid']
        return self._yaxis_transform

    def get_yaxis_text1_transform(self, pad):
        return self._yaxis_text1_transform, 'center', 'right'

    def get_yaxis_text2_transform(self, pad):
        return self._yaxis_text2_transform, 'center', 'left'

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
        self._xaxis_pretransform \
            .clear() \
            .scale(1.0, self._longitude_cap * 2.0) \
            .translate(0.0, -self._longitude_cap)

    def get_data_ratio(self):
        return 1.0

    def can_zoom(self):
        return False

    def start_pan(self, x, y, button):
        self.pan_ori = self.transData.inverted().transform_point((x, y))

    def drag_pan(self, button, key, x, y):
        pan_current = self.transData.inverted().transform_point((x, y))
        delta = self.pan_ori - pan_current
        if numpy.isnan(delta).any():
            return
        self.go_to(self.lon0 + delta[0], self.lat0 + delta[1])

    def go_to(self, lon, lat):
        if self.lon0 != lon or self.lat0 != lat:
            self.lon0 = lon
            self.lat0 = lat
            self.transProjection.lon0 = lon
            self.transProjection.lat0 = lat
            self.transProjection.proj = pyproj.Proj(proj=self.name, lat_0=lat, lon_0=lon, ellps=self.ellps)
            return True
        return False

class OrthoAxes(TransformAxes):

    name = 'ortho'
    def __init__(self, *args, **kwargs):
        self.lon0 = kwargs.pop('lon0', 50)
        self.lat0 = kwargs.pop('lat0', 50)
        self.ellps = 'sphere'
        self._longitude_cap = 80
        super(OrthoAxes, self).__init__(*args, **kwargs)
        self.set_aspect('equal')
        self.update_env()

    @property
    def coordinates_bbox(self):
        return (-180,180), (-90, 90)
    

def register_projection():
    from matplotlib.projections import projection_registry
    for axes in (PlatCarreAxes, OrthoAxes):
        projection_registry._all_projection_types[axes.name] = axes
