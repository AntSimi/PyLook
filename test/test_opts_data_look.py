import shlex
from pylook.data_look import data_look

cmds = (
    # '--di -v INFO',
    # '--di -v DEBUG',
    # '--figure_s coor=10',
    # """--figure_o facecolor="'r'"  --di """,
    # """-h""",
    # """--figure_o help""",
    # """--su geo=[coast=[coast_color="'y'",coast_linewidth=25],border=border=True] --di""",
    # """--figure_options[1] sup="'Figure 1'" --figure_options[2] sup="'Figure 2'" --di -h""",
    # """--figure_options[1] sup="'Figure 1'" --figure_options[2] sup="'Figure 2'" face="'y'"
    #  --figure_options[1,2] face="'r'" dpi=99 --figure_options[:]  face="'b'" dpi=101 --figure_options[3] sup="'figure3'" --di """,
    """--figure_set_options[fs1] --figure_set_options[fs0]
    --figure_options[f5,parent=fs0]
    --subplot_options[s5,parent=f5] position=221
    --figure_options[f1,parent=fs1] sup="'Figure 1'" --figure_options[f2,parent=fs1] sup="'Figure 2'" --figure_options[f3,parent=fs1] sup="'Figure 3'"
     --subplot_options[s1,parent=f1,f2] positio=221 title="'subplot multi parent'"
     --subplot_options[s2,parent=:] positio=222 title="'subplot all parent'"
     --subplot_options[s3,parent=f3] positio=223 title="'subplot only fig 3'"
     --subplot_options[s4] positio=224 title="'random'"
      """,
    #   --di """,
)

for cmd in cmds:
    print("-------------  " * 5)
    args = data_look(shlex.split(cmd))
