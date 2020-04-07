"""
"""
import netCDF4
import numba
import numpy
import matplotlib.collections as mc


class GSHHSFile:

    __slots__ = (
        'bin_size',
        'nb_bin_x',
        'nb_bin_y',
        'relative_x',
        'relative_y',
        'i_first_seg_bin',
        'nb_seg_bin',
        'i_first_pt_seg',
        'nb_pt_seg'
        )

    BIN_SIZE = 'Bin_size_in_minutes'
    NB_BIN_X = 'N_bins_in_360_longitude_range'
    NB_BIN_Y = 'N_bins_in_180_degree_latitude_range'
    RELATIVE_X = 'Relative_longitude_from_SW_corner_of_bin'
    RELATIVE_Y = 'Relative_latitude_from_SW_corner_of_bin'
    INDEX_FIRST_SEG_IN_BIN = 'Id_of_first_segment_in_a_bin'
    NB_SEG_BY_BIN = 'N_segments_in_a_bin'
    INDEX_FIRST_PT_IN_SEG = 'Id_of_first_point_in_a_segment'


    def __init__(self, filename):
        self.load(filename)
        
    def load(self, filename):
        with netCDF4.Dataset(filename) as h:
            h.set_auto_maskandscale(False)
            self.bin_size = h.variables[self.BIN_SIZE][0] / 60.
            self.nb_bin_x = h.variables[self.NB_BIN_X][0]
            self.nb_bin_y = h.variables[self.NB_BIN_Y][0]
            self.relative_x = h.variables[self.RELATIVE_X][:].astype('u2')
            self.relative_y = h.variables[self.RELATIVE_Y][:].astype('u2')
            self.i_first_seg_bin = h.variables[self.INDEX_FIRST_SEG_IN_BIN][:]
            self.nb_seg_bin = h.variables[self.NB_SEG_BY_BIN][:]
            self.i_first_pt_seg = h.variables[self.INDEX_FIRST_PT_IN_SEG][:]


    def lines(self, llcrnrlon=0, llcrnrlat=-90, urcrnrlon=360, urcrnrlat=90, **kwargs_line_collection):
        lines = get_lines(
            self.relative_x, self.relative_y,
            self.nb_seg_bin, self.i_first_seg_bin, self.nb_pt_seg, self.i_first_pt_seg,
            self.nb_bin_x, self.nb_bin_y, self.bin_size, llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat)
        return mc.LineCollection((lines,), **kwargs_line_collection)


class CoastFile(GSHHSFile):

    __slots__ = (
        'level_seg',
        'id_seg'
    )
    SEG_INFO = 'Embedded_npts_levels_exit_entry_for_a_segment'
    POLYGON_ID = 'Id_of_GSHHS_ID'
    # int Id_of_parent_polygons(Dimension_of_polygon_array) ;
    # double The_km_squared_area_of_polygons(Dimension_of_polygon_array) ;
    # int Micro_fraction_of_full_resolution_area(Dimension_of_polygon_array) ;
    # int Id_of_node_polygons(Dimension_of_node_arrays) ;
    # short Embedded_node_levels_in_a_bin(Dimension_of_bin_arrays) ;
    # short Embedded_node_levels_in_a_bin_ANT(Dimension_of_bin_arrays) ;
    
    # byte Embedded_ANT_flag(Dimension_of_segment_arrays) ;

    def load(self, filename):
        super(CoastFile, self).load(filename)
        with netCDF4.Dataset(filename) as h:
            h.set_auto_maskandscale(False)
            seg_info = h.variables[self.SEG_INFO][:]
            self.nb_pt_seg = seg_info >> 9
            self.level_seg = (seg_info >> 6) & 0x7
            self.id_seg = h.variables[self.POLYGON_ID][:]

    def polygons(self, llcrnrlon=0, llcrnrlat=-90, urcrnrlon=360, urcrnrlat=90, **kwargs_polygon):
        x, y, nb_pt_seg, id_seg  = get_data_for_polygon(
            self.relative_x, self.relative_y,
            self.nb_seg_bin, self.i_first_seg_bin, self.nb_pt_seg, self.i_first_pt_seg, self.id_seg,
            self.nb_bin_x, self.nb_bin_y, self.bin_size, llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat)
        
        polygons = build_polygon(x, y, nb_pt_seg, id_seg)
        # print(len(polygons), id_seg.shape)
        kwargs_polygon['linewidth'] = 0
        kwargs_polygon['closed'] = False
        return mc.PolyCollection(polygons, **kwargs_polygon)

class BorderRiverFile(GSHHSFile):

    __slots__ = tuple()
    SEG_INFO = 'N_points_for_a_segment'

    def load(self, filename):
        super(BorderRiverFile, self).load(filename)
        with netCDF4.Dataset(filename) as h:
            h.set_auto_maskandscale(False)
            self.nb_pt_seg = h.variables [self.SEG_INFO][:]


@numba.njit(cache=True)
def build_polygon(x, y, nb_pt_seg, id_seg):
    polygons = list()
    i = 0
    for nb in nb_pt_seg:
        i1 = i + nb - 1
        if x[i] == x[i1] and y[i] == y[i1]:
            sl = slice(i, i1)
            polygons.append(build_vertice(x[sl], y[sl]))
        i += nb
    return polygons


@numba.njit(cache=True)
def build_vertice(x, y):
    nb = x.shape[0]
    pt = numpy.empty((nb, 2), dtype=x.dtype)
    pt[:, 0] = x
    pt[:, 1] = y
    return pt


@numba.njit(cache=True)
def get_data_for_polygon(
        relative_x, relative_y, nb_seg_bin, i_first_seg_bin, nb_pt_seg, i_first_pt_seg, id_seg,
        nb_bin_x, nb_bin_y, bin_size, llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat):
    i0, i1 = int(llcrnrlon // bin_size), int(urcrnrlon // bin_size)
    j0, j1 = nb_bin_y - int((urcrnrlat + 90) // bin_size), nb_bin_y - int((llcrnrlat + 90) // bin_size)
    new_x, new_y = list(), list()
    nb_pt_seg_list, id_seg_list = list(), list()
    nb_seg_list = list()
    nb_box = 0
    nb_pt = 0
    nb_seg = 0
    for j in range(j0, j1):
        for i in range(i0, i1):
            i_box = int(i % nb_bin_x + nb_bin_x * j)

            nb_seg_box = nb_seg_bin[i_box]
            if nb_seg_box == 0:
                continue
            start_seg = i_first_seg_bin[i_box]
            last_seg = start_seg + nb_seg_box - 1

            start_pt = i_first_pt_seg[start_seg]
            last_pt = i_first_pt_seg[last_seg] + nb_pt_seg[last_seg]
            sl_seg = slice(start_seg, last_seg + 1)
            sl_pt = slice(start_pt, last_pt)
            # re-reference data
            x = (relative_x[sl_pt] / 65535. + i) * bin_size
            y = (relative_y[sl_pt] / 65535. + nb_bin_y - j) * bin_size - 90. - bin_size
            new_x.append(x)
            new_y.append(y)
            id_seg_list.append(id_seg[sl_seg])
            nb_pt_seg_list.append(nb_pt_seg[sl_seg])
            nb_box += 1
            nb_pt += x.shape[0]
            nb_seg += nb_seg_box
            nb_seg_list.append(nb_seg_box)
    x = numpy.empty(nb_pt, dtype=numba.float32)
    y = numpy.empty(nb_pt, dtype=numba.float32)
    nb_pt_seg = numpy.empty(nb_seg, dtype=nb_pt_seg.dtype)
    id_seg = numpy.empty(nb_seg, dtype=id_seg.dtype)
    i = 0
    i_seg = 0
    for i_box in range(nb_box):
        nb = new_x[i_box].shape[0]
        nb_seg = nb_seg_list[i_box]
        x[i: i + nb] = new_x[i_box]
        y[i: i + nb] = new_y[i_box]
        nb_pt_seg[i_seg: i_seg + nb_seg] = nb_pt_seg_list[i_box]
        id_seg[i_seg: i_seg + nb_seg] = id_seg_list[i_box]
        i += nb
        i_seg += nb_seg
    return x, y, nb_pt_seg, id_seg

@numba.njit(cache=True)
def get_lines(
        relative_x, relative_y, nb_seg_bin, i_first_seg_bin, nb_pt_seg, i_first_pt_seg,
        nb_bin_x, nb_bin_y, bin_size, llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat):
    i0, i1 = int(llcrnrlon // bin_size), int(urcrnrlon // bin_size)
    j0, j1 = nb_bin_y - int((urcrnrlat + 90) // bin_size), nb_bin_y - int((llcrnrlat + 90) // bin_size)
    new_x, new_y = list(), list()
    nb_pt = 0
    nb_box = 0
    for j in range(j0, j1):
        for i in range(i0, i1):
            i_box = int(i % nb_bin_x + nb_bin_x * j)

            nb_seg = nb_seg_bin[i_box]
            if nb_seg == 0:
                continue
            start_seg = i_first_seg_bin[i_box]
            last_seg = start_seg + nb_seg - 1

            start_pt = i_first_pt_seg[start_seg]
            last_pt = i_first_pt_seg[last_seg] + nb_pt_seg[last_seg]
            sl_seg = slice(start_seg, last_seg + 1)
            sl_pt = slice(start_pt, last_pt)
            # re-reference data
            x = (relative_x[sl_pt] / 65535. + i) * bin_size
            y = (relative_y[sl_pt] / 65535. + nb_bin_y - j) * bin_size - 90. - bin_size
            # Insert nan
            x, y = break_lines(x, y, i_first_pt_seg[sl_seg] - start_pt)
            new_x.append(x)
            new_y.append(y)
            nb_pt += x.shape[0]
            nb_box += 1
    # Create a vertices
    lines = numpy.empty((2, nb_pt), dtype=numba.float32)
    i = 0
    for i_box in range(nb_box):
        nb = new_x[i_box].shape[0]
        lines[0, i: i + nb] = new_x[i_box]
        lines[1, i: i + nb] = new_y[i_box]
        i += nb
    return lines.T


@numba.njit(cache=True)
def break_lines(x, y, i_first_pt):
    nb_seg = i_first_pt.shape[0]
    nb_pt = x.shape[0]
    out_size = nb_seg + nb_pt
    new_x = numpy.empty(out_size, dtype=x.dtype)
    new_y = numpy.empty(out_size, dtype=y.dtype)
    i_previous = 0
    shift = 0
    for i in i_first_pt[1:]:
        new_x[i_previous + shift:i + shift] = x[i_previous:i]
        new_y[i_previous + shift:i + shift] = y[i_previous:i]
        new_x[i + shift] = numpy.nan
        new_y[i + shift] = numpy.nan
        shift += 1
        i_previous = i
    new_x[i_previous + shift:-1] = x[i_previous:]
    new_y[i_previous + shift:-1] = y[i_previous:]
    new_x[-1] = numpy.nan
    new_y[-1] = numpy.nan
    return new_x, new_y