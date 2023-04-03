import os
import logging
import inspect
from edalize.flows.edaflow import Edaflow, FlowGraph

logger = logging.getLogger(__name__)


class Dc_pp(Edaflow):
    """Synthesis with DC and perform power analysis with primepower"""

    argtypes = ["vlogdefine", "vlogparam"]

    _flow = {
        "sandpipersaas": {"fdto": {}},
        "design_compiler": {"deps": ["sandpipersaas"]},
    }

    FLOW_OPTIONS = {}

    @classmethod
    def get_tool_options(cls, flow_options):
        # Add any frontends used in this flow
        flow = flow_options.get("frontends", []).copy()
        # Adding DC and PP to the flow
        flow_defined_tool_options = {}
        flow.append("sandpipersaas")
        flow.append("design_compiler")
        return cls.get_filtered_tool_options(flow, flow_defined_tool_options)

    def configure_flow(self, flow_options):

        flow = self._flow.copy()

        # No user defined frontends so leaving adding the front end dependency
        # refer icestorm flow for more details
        name = self.edam["name"]
        self.commands.set_default_target("synth")
        self.goal = "synth"

        return FlowGraph.fromdict(flow)

    def build(self):
        logger.info("Test")
        logger.info(self.work_root)
        attributes = inspect.getmembers(self, lambda a: not (inspect.isroutine(a)))
        for i in attributes:
            logger.info(i)
        self._run_tool("make", [self.goal], cwd=self.work_root)
