# Copyright edalize contributors
# Licensed under the 2-Clause BSD License, see LICENSE for details.
# SPDX-License-Identifier: BSD-2-Clause

import logging
import os.path

from edalize.tools.edatool import Edatool
from edalize.utils import EdaCommands

logger = logging.getLogger(__name__)


class Sandpipersaas(Edatool):

    description = "SandPiper SaaS Edition runs Redwood EDA's SandPiper™ TL-Verilog compiler as a microservice in the cloud to support low-overhead and zero-cost open-source development using commercial-grade capabilities"

    TOOL_OPTIONS = {
        "sandpiper_saas": {
            "type": "str",
            "desc": "Additional options for sandpiper-saas",
        },
        "sandpiper_jar": {
            "type": "str",
            "desc": "Additional options for sandpiper_jar",
        },
        "output_file": {
            "type": "str",
            "desc": "Name of the output Verilog/System Verilog file (Must contain .v or .sv)",
        },
        "output_dir": {
            "type": "str",
            "desc": "Optional: Path to the output directory",
        },
        "endpoint": {"type": "str", "desc": "Compile service endpoint"},
        "includes": {
            "type": "str",
            "desc": "List of include files to be used during compilation",
        },
    }

    def setup(self, edam):
        super().setup(edam)

        if len(self.files) > 1:
            raise RuntimeError("Only 1 TL-V file is allowed")

        if self.files[0].get("file_type").lower() != "tlverilogsource":
            raise RuntimeError("Expected file type: TLVerilogSource")

        _s = "sandpiper-saas -i {inputfile} -o {outputfile} {outputdir} {includes} {sandpiper_saas_options} {sandpiper_jar_options}"

        sandpiper_saas_options = " ".join(self.tool_options.get("sandpiper_saas", []))
        sandpiper_jar_options = " ".join(self.tool_options.get("sandpiper_jar", []))
        outputfile = " ".join(self.tool_options.get("output_file", ""))
        inputfile = self.files[0].get("name")
        outputdir = ""
        includes = ""
        endpoint = ""
        build_files = self.work_root
        if self.tool_options.get("output_dir", " ") != " ":
            outputdir = "--outdir " + " ".join(self.tool_options.get("output_dir", " "))
        if self.tool_options.get("includes", []) != []:
            includes = "-f " + " ".join(self.tool_options.get("includes", []))
        if self.tool_options.get("endpoint", " ") != " ":
            endpoint = "--endpoint " + " ".join(self.tool_options.get("endpoint", " "))

        _gen_s = _s.format(
            inputfile=inputfile,
            outputfile=outputfile,
            outputdir=outputdir,
            includes=includes,
            endpoint=endpoint,
            sandpiper_saas_options=sandpiper_saas_options,
            sandpiper_jar_options=sandpiper_jar_options,
        )
        print(_gen_s)

        commands = EdaCommands()
        deps = [
            inputfile,
        ]
        targets = [
            outputfile,
        ]
        commands.add([_gen_s], targets, deps)
        commands.add_env_var("RM", "rm -rf")

        commands.add(["${RM} " + self.work_root], ["clean"], " ")
        commands.add([], ["tlv2v"], targets)
        commands.set_default_target("tlv2v")
        self.commands = commands

    def run(self):
        args = ["tlv2v"]
        # Set plusargs
        if self.plusarg:
            plusargs = []
            for key, value in self.plusarg.items():
                plusargs += ["+{}={}".format(key, self._param_value_str(value))]
            args.append("EXTRA_OPTIONS=" + " ".join(plusargs))
        return ("make", args, self.work_root)
