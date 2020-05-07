"""
Plot fake sat
=============
"""
import shlex
from pylook.data_look import data_look

cmd = "DataLook --dem  --method plot_plk --data fake_sat --method_options linew=0 --gallery"
data_look(shlex.split(cmd)[1:])
