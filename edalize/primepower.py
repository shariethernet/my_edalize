import os
import logging

from edalize.edatool import Edatool

logger = logging.getLogger(__name__)


class Primepower(Edatool):

    argtypes = ["vlogdefine", "vlogparam", "generic"]

    @classmethod
    def get_doc(cls, api_ver):
        if api_ver == 0:
            return {
                "description": "Synopsys Primepower backend that performs averaged and dynamic power analysis",
                "members": [
                    {
                        "name": "pp_script_dir",
                        "type": "String",
                        "desc": "Path to primepower scripts (e.g. /home/user/project/synopsys/scripts)",
                    },
                    {
                        "name": "pp_script",
                        "type": "String",
                        "desc": "Name of the primepower script to run [located in script_dir](e.g. synth.tcl)",
                    },
                    {
                        "name": "report_dir",
                        "type": "String",
                        "desc": "Path to where reports should be stored (e.g. /home/user/project/synopsys/reports)",
                    },
                    {
                        "name": "target_library",
                        "type": "String",
                        "desc": "The Design Compiler target_library",
                    },
                    {
                        "name": "libs",
                        "type": "String",
                        "desc": "Libraries to use in the Design Compiler link_library",
                    },
                    {
                        "name": "jobs",
                        "type": "Integer",
                        "desc": "Number of jobs. Useful for parallelizing syntheses.",
                    },
                    {
                        "name": "mode",
                        "type": "String",
                        "desc": "averaged (or) time_based",
                    },
                    {
                        "name": "vcd_strip_path",
                        "type": "String",
                        "desc": "Defaults to None, enter the path to the signal interface of VCD",
                    },
                    {
                        "name": "lib_dir",
                        "type": "String",
                        "desc": "Add the search paths",
                    },
                    {
                        "name": "verilog_dir",
                        "type": "String",
                        "desc": "Add the search paths",
                    },
                ],
            }

    """ Configuration is the first phase of the build
    This writes the project TCL files and Makefile. It first collects all
    sources, IPs and constraints and then writes them to the TCL file along
     with the build steps.
    """

    def configure_main(self):
        def make_list(opt):
            if opt:
                opt = (
                    ((opt.replace("[", "")).replace("]", "")).replace(",", "")
                ).replace("'", "")
            return opt

        (src_files, incdirs) = self._get_fileset_files(force_slash=True)

        self.jinja_env.filters["src_file_filter"] = self.src_file_filter

        # self.pp_tool = self.tool_options.get("pp", "primewpower")
        vcdname = ""
        netlistpath = ""
        for file in self.files:
            if file.get("file_type") == "vcd":
                vcdname = file.get("name")
            if file.get("file_type") == "verilogSource":
                netlistpath = file.get("name")

        template_vars = {
            "name": self.name,
            "src_files": src_files,
            "incdirs": incdirs + ["."],
            "tool_options": self.tool_options,
            "mode": self.tool_options.get("mode"),
            "lib_dir": self.tool_options.get("lib_dir"),
            "verilog_dir": self.tool_options.get("verilog_dir"),
            "script_dir": self.tool_options.get("pp_script_dir"),
            "pp_script": make_list(self.tool_options.get("pp_script")),
            "report_dir": make_list(self.tool_options.get("report_dir")),
            "target_library": self.tool_options.get("target_library"),
            "libs": make_list(self.tool_options.get("libs")),
            "toplevel": self.toplevel,
            "vcdpath": vcdname,
            "netlistpath": netlistpath,
        }

        pp_settings = self.tool_options.get("design_compiler-settings", None)
        pp_command = (
            "source {} && design_compiler".format(pp_settings)
            if pp_settings
            else "design_compiler"
        )

        self.render_template(
            "primepower-makefile.j2",
            "Makefile",
            {
                "name": self.name,
                "report_dir": make_list(self.tool_options.get("report_dir")),
                "pp_command": pp_command,
            },
        )

        jobs = self.tool_options.get("jobs", None)

        run_template_vars = {"jobs": " -jobs " + str(jobs) if jobs is not None else ""}

        self.render_template(
            "primepower-project.tcl.j2", self.name + ".tcl", template_vars
        )

    def src_file_filter(self, f):
        file_types = {
            "verilogSource": "read_verilog",
            "systemVerilogSource": "read_sverilog",
            "vhdlSource": "read_vhdl",
            "tclSource": "source",
            "sdc": "read_sdc",
            "sdf": "read_sdf",
            "spef": "read_parasitics",
            "vcd": "read_vcd",
        }

        _file_type = f.file_type.split("-")[0]
        if _file_type in file_types:
            cmd = ""

            if _file_type == "vcd":
                cmd += (
                    file_types[_file_type]
                    + " "
                    + "-strip_path"
                    + " "
                    + self.tool_options.get("vcd_strip_path", None)
                    + " "
                    + f.name
                )
                return cmd
            elif _file_type == "verilogSource":
                pass
            else:
                cmd += file_types[_file_type] + " " + f.name
                return cmd

        if _file_type == "user":
            return ""

        _s = "{} has unknown file type '{}', interpretation is up to Prime Power Compiler"
        logger.warning(_s.format(f.name, f.file_type))
        # return "add_files -norecurse" + " " + f.name

    def build_main(self):
        logger.info("Building")
        logger.info(
            "(running make, which runs pwr_shell which has an unbelievably long lag before printing. be patient)"
        )
        logger.info((self.tool_options.get("pp_script_dir")))
        args = []
        self._run_tool("make", args, quiet=True)
