import os
import logging
import inspect
from edalize.flows.edaflow import Edaflow, FlowGraph

logger = logging.getLogger(__name__)


class Sp_dc(Edaflow):
    """Gen Verilog with Sandpiper and then synthesize with Design Compiler"""

    argtypes = ["vlogdefine", "vlogparam"]

    FLOW_DEFINED_TOOL_OPTIONS = {
        # "sandpipersaas": {"output_dir": ["tlv_out"]},
    }

    FLOW_OPTIONS = {}

    @classmethod
    def get_tool_options(cls, flow_options):
        # Add any frontends used in this flow
        flow = flow_options.get("frontends", []).copy()
        # Adding DC and PP to the flow
        flow.append("sandpipersaas")
        flow.append("design_compiler")
        return cls.get_filtered_tool_options(flow, cls.FLOW_DEFINED_TOOL_OPTIONS)

    def configure_flow(self, flow_options):

        flow = {
            "sandpipersaas": {
                # "fdto": self.FLOW_DEFINED_TOOL_OPTIONS["sandpipersaas"]
            },
            "design_compiler": {"deps": ["sandpipersaas"]},
        }
        # flow = self._flow.copy()

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
        # print(self.edam)
        # self.commands.add([], ["combine"], ["tlv2v", "synth"])
        # self.commands.set_default_target("combine")
        self.commands.set_default_target("synth")

    # def build(self):
    #     logger.info("Test")
    #     logger.info(self.work_root)
    #     #attributes = inspect.getmembers(self, lambda a: not(inspect.isroutine(a)))
    #     ##    logger.info(i)
    #     self._run_tool("make", [self.goal], cwd=self.work_root)
