import os
import logging
import inspect
from edalize.flows.edaflow import Edaflow, FlowGraph

logger = logging.getLogger(__name__)


class Pt_pp(Edaflow):
    """Perform STA with PT and run perform power analysis with timing info from the STA"""

    argtypes = ["vlogdefine", "vlogparam"]

    _flow = {
        "ptpx": {"fdto": {}},
        "primepower": {"deps": ["ptpx"]},
    }

    FLOW_OPTIONS = {}

    @classmethod
    def get_tool_options(cls, flow_options):
        # Add any frontends used in this flow
        flow = flow_options.get("frontends", []).copy()
        # Adding DC and PP to the flow
        flow_defined_tool_options = {}
        flow.append("ptpx")
        flow.append("primepower")
        return cls.get_filtered_tool_options(flow, flow_defined_tool_options)

    def configure_flow(self, flow_options):

        flow = self._flow.copy()

        # No user defined frontends so leaving adding the front end dependency
        # refer icestorm flow for more details
        # name = self.edam["name"]
        # self.commands.set_default_target("synth")
        # self.goal = "synth"

        return FlowGraph.fromdict(flow)

    def build_tool_graph(self):
        return super().build_tool_graph()

    def configure_tools(self, nodes):
        super().configure_tools(nodes)
        name = self.edam["name"]
        self.commands.add([], ["combine"], ["timing", "poweranalyze"])
        self.commands.set_default_target("combine")
