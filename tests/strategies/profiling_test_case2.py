from xlseries.strategies.strategies import ParameterDiscovery
from xlseries.utils.general import load_file
from xlseries.strategies.discover.parameters import Parameters
from openpyxl import load_workbook
from xlseries.utils.general import get_data_frames, change_working_dir
import yappi


REL_WORKING_DIR = r"tests\integration_cases"
PACKAGE_NAME = "xlseries"


def parse_t_name(fn_name):
    """Parse the test name from a function name."""
    return "_".join(fn_name.split("_")[:2])


@load_file("parameters/", parse_t_name, ".json", Parameters, "params")
@load_file("original/", parse_t_name, ".xlsx", load_workbook, "test_wb")
@change_working_dir(PACKAGE_NAME, REL_WORKING_DIR)
def test_case2_with_params(test_wb, params):
    strategy_obj = ParameterDiscovery(test_wb, params)
    test_dfs = strategy_obj.get_data_frames()

    print test_dfs


if __name__ == '__main__':
    from pycallgraph import PyCallGraph
    from pycallgraph.output import GraphvizOutput

    # with PyCallGraph(output=GraphvizOutput()):

    graphviz = GraphvizOutput()
    graphviz.output_file = 'basic.png'
    with PyCallGraph(output=graphviz):
        test_case2_with_params()
