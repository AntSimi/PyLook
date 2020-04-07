import matplotlib.axes
import os
from . import coast 


class PlatCarreAxes(matplotlib.axes.Axes):

    name = 'plat_carre'
    def __init__(self, *args, **kwargs):
        self._coast_object = None
        self.coast_mappable = None
        self.coast_flag = kwargs.pop('coast', True)
        super(PlatCarreAxes, self).__init__(*args, **kwargs)
        self.set_aspect('equal')
        self.set_env()

    @property
    def coast_object(self):
        if self._coast_object is None:
            self._coast_object = coast.CoastFile(f'{os.environ["GSHHS_DATA"]}/binned_GSHHS_i.nc')
        return self._coast_object
    
    @property
    def coordinates_bbox(self):
        return self.get_xlim(), self.get_ylim()
    
    def set_env(self):
        # print(self.bbox)
        pass

    def update_env(self):
        xlim, ylim = self.coordinates_bbox
        if self.coast_mappable is not None:
            self.coast_mappable.remove()
            self.coast_mappable = None
        self.coast_mappable = self.add_collection(self.coast_object.lines(xlim[0], ylim[0], xlim[1], ylim[1]))
        

    def end_pan(self, *args, **kwargs):
        super(PlatCarreAxes, self).end_pan(*args, **kwargs)
        self.update_env()


def register_projection():
    from matplotlib.projections import projection_registry
    for axes in (PlatCarreAxes,):
        projection_registry._all_projection_types[axes.name] = axes
