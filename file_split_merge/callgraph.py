from pycallgraph2 import PyCallGraph
from pycallgraph2.output import GraphvizOutput
from pycallgraph2 import Config
from pycallgraph2 import GlobbingFilter
from file_split_merge import SplitAndCombineFiles
config = Config(max_depth=100)


# config.trace_filter = GlobbingFilter(include=[
#     '*file_split_merge*',],
#     exclude=['pycallgraph.*',
#              '*decorator*',
#              '*module*',
#              '*threading*',
#              '*multiprocessing*',
#     ]
# )

with PyCallGraph(output=GraphvizOutput(output_file='filter_exclude.png')):

    SplitAndCombineFiles().split(r"C:\Roshan\ZIP\New folder\first_project4.zip", '5')


