import matplotlib.axes
import os
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
        self.coast_mappable = self.add_collection(
            self.coast_object.lines(
                xlim[0], ylim[0], xlim[1], ylim[1],
                linewidth=.25, color='k'
                )
                )

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


def register_projection():
    from matplotlib.projections import projection_registry
    for axes in (PlatCarreAxes,):
        projection_registry._all_projection_types[axes.name] = axes
