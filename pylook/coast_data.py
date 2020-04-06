"""
"""
import netCDF4
import numba
import numpy


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
    SEG_INFO = 'Embedded_npts_levels_exit_entry_for_a_segment'
    # int N_polygons_in_file(Dimension_of_scalar) ;
    # int N_segments_in_file(Dimension_of_scalar) ;
    # int N_points_in_file(Dimension_of_scalar) ;
    # int N_nodes_in_file(Dimension_of_scalar) ;
    # int Id_of_parent_polygons(Dimension_of_polygon_array) ;
    # double The_km_squared_area_of_polygons(Dimension_of_polygon_array) ;
    # int Micro_fraction_of_full_resolution_area(Dimension_of_polygon_array) ;
    # int Id_of_node_polygons(Dimension_of_node_arrays) ;
    # short Embedded_node_levels_in_a_bin(Dimension_of_bin_arrays) ;
    # short Embedded_node_levels_in_a_bin_ANT(Dimension_of_bin_arrays) ;
    # int Embedded_npts_levels_exit_entry_for_a_segment(Dimension_of_segment_arrays) ;
    # int Id_of_GSHHS_ID(Dimension_of_segment_arrays) ;
    # byte Embedded_ANT_flag(Dimension_of_segment_arrays) ;


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
            seg_info = h.variables [self.SEG_INFO][:]
            self.nb_pt_seg = seg_info >> 9

    def lines(self, llcrnrlon=0, llcrnrlat=-90, urcrnrlon=360, urcrnrlat=90):
        i0, i1 = int(llcrnrlon // self.bin_size), int(urcrnrlon // self.bin_size)
        j0, j1 = self.nb_bin_y - int((urcrnrlat + 90) // self.bin_size), self.nb_bin_y - int((llcrnrlat + 90) // self.bin_size)
        new_x, new_y = list(), list()

        for j in range(j0, j1):
            for i in range(i0, i1):
                i_box = i % self.nb_bin_x + self.nb_bin_x * j
                
                nb_seg = self.nb_seg_bin[i_box]
                if nb_seg == 0:
                    continue
                start_seg = self.i_first_seg_bin[i_box]
                last_seg = start_seg + nb_seg - 1

                start_pt = self.i_first_pt_seg[start_seg]
                last_pt = self.i_first_pt_seg[last_seg] + self.nb_pt_seg[last_seg]
                sl_seg = slice(start_seg, last_seg + 1)
                sl_pt = slice(start_pt, last_pt)
                x = (self.relative_x[sl_pt] / 65535. + i)* self.bin_size
                y = (self.relative_y[sl_pt] / 65535. + self.nb_bin_y - j)* self.bin_size - 90.
                x, y = break_lines(x, y, self.i_first_pt_seg[sl_seg] - start_pt)
                new_x.append(x)
                new_y.append(y)
        return numpy.concatenate(new_x), numpy.concatenate(new_y)

@numba.njit
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