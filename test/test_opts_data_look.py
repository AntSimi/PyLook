import shlex
from pylook.data_look import data_look
cmds = (
    '',
    # '--figure_s coor=10',
    """--figure_o facecolor="'r'" """,
    # """-h""",
    # """--figure_o help""",
    """--su geo=[coast=[coast_color="'y'",coast_linewidth=.25],border=border=True]""",
    """--su help""",
    )

for cmd in cmds:
    print('-------------  ' * 5)
    print(cmd)
    print(shlex.split(cmd))
    args = data_look(shlex.split(cmd))
    print(args)