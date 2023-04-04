import logging
import os.path
import re

from edalize.tools.edatool import Edatool
from edalize.utils import EdaCommands

logger = logging.getLogger(__name__)


class Design_compiler(Edatool):

    description = "The design_compiler backend executes Synopsys design_copiler to build a gate-level netlist"

    TOOL_OPTIONS = {
        "script_dir": {
            "type": "str",
            "desc": "Path to Syopsys scripts (e.g. /home/user/project/synopsys/scripts)",
        },
        "dc_script": {
            "type": "str",
            "desc": "Name of the synthesis script to run [located in script_dir](e.g. synth.tcl)",
        },
        "report_dir": {
            "type": "str",
            "desc": "Path to where reports should be stored (e.g. /home/user/project/synopsys/reports)",
        },
        "target_library": {
            "type": "str",
            "desc": "The Design Compiler target_library",
        },
        "libs": {
            "type": "str",
            "desc": "Libraries to use in the Design Compiler link_library",
        },
        "jobs": {
            "type": "str",
            "desc": "Number of jobs. Useful for parallelizing syntheses.",
        },
        "indirect_source": {
            "type": "str",
            "desc": "set to true (in quotes) when the search path for the RTL is not in the .core, but output from a previous tool ",
        },
        "rtl_in_name": {
            "type": "str",
            "desc": "Name of the generated RTL to be synthesized",
        },
    }

    # To get the same data structure for generated src files to dc
    def _get_fileset_files_ids(self, force_slash=False):
        paths = [
            self.work_root,
        ]
        logger.warning("rtl paths", paths[0])

        class File:
            def __init__(self, name, file_type, logical_name):
                self.name = name
                self.file_type = file_type
                self.logical_name = logical_name

        incdirs = []
        src_files = []
        for path in paths:
            _files, _rtl_file_names = self.get_rtl_files(paths)
            for fname, ftype in _files.items():
                src_files.append(File(fname, ftype, fname))
                logger.warning(fname, ftype)

        return (src_files, incdirs)

    def _get_fileset_files(self, force_slash=False):
        class File:
            def __init__(self, name, file_type, logical_name):
                self.name = name
                self.file_type = file_type
                self.logical_name = logical_name

        incdirs = []
        src_files = []
        for f in self.files:
            if not self._add_include_dir(f, incdirs, force_slash):
                _name = f["name"]
                if force_slash:
                    _name = _name.replace("\\", "/")
                file_type = f.get("file_type", "")
                logical_name = f.get("logical_name", "")
                src_files.append(File(_name, file_type, logical_name))
        return (src_files, incdirs)

    def src_file_filter(self, f):
        file_types = {
            "verilogSource": "analyze -format verilog",
            "systemVerilogSource": "analyze -format sverilog",
            "vhdlSource": "analyze -format vhdl",
            "tclSource": "source",
            "SDC": "source",
        }

        _file_type = f.file_type.split("-")[0]
        if _file_type in file_types:
            cmd = ""
            cmd += file_types[_file_type] + " "

            if (_file_type != "tclSource") and (_file_type != "SDC"):
                cmd_define = ""
                if (_file_type != "vhdlSource") and (self.vlogdefine.items() != {}):
                    cmd_define = "-define {"
                    for k, v in self.vlogdefine.items():
                        # Skip reddefinition of SYNTHESIS which is a reserved macro in IEEE Verilog synthesizable subset
                        if k != "SYNTHESIS":
                            cmd_define += " {}={}".format(k, self._param_value_str(v))
                    cmd_define += " }"

                cmd += cmd_define + " " + "-work work " + f.name
            else:
                cmd += " " + f.name

            return cmd

        if _file_type == "user":
            return ""

        _s = "{} has unknown file type '{}', interpretation is up to Design Compiler"
        logger.warning(_s.format(f.name, f.file_type))
        # return "add_files -norecurse" + " " + f.name

    ids_commands = []

    def get_rtl_files(self, paths=[]):
        force_files = []
        rtl_files = {}
        all_files = []
        _f = self.tool_options.get("rtl_in_name", "")
        if not os.path.exists(_f):
            with open(_f, "w"):
                pass
        if self.tool_options.get("rtl_in_name", None) is not None:
            force_files.append(self.tool_options.get("rtl_in_name", None))
            all_paths = paths + force_files
        else:
            all_paths = paths
        logger.warning(f"All Paths {all_paths}")
        file_types = {
            "verilogSource": "analyze -format verilog",
            "systemVerilogSource": "analyze -format sverilog",
            "vhdlSource": "analyze -format vhdl",
            "tclSource": "source",
            "SDC": "source",
        }
        cmd_define = " -define {"
        for k, v in self.vlogdefine.items():
            # Skip reddefinition of SYNTHESIS which is a reserved macro in IEEE Verilog synthesizable subset
            if k != "SYNTHESIS":
                cmd_define += " {}={}".format(k, self._param_value_str(v))
        cmd_define += " }"
        file_path = []
        for path in all_paths:
            if os.path.isdir(path):
                for file in os.listdir(path):
                    file_path.append(os.path.join(path, file))
            if os.path.isfile(path):
                file_path.append(os.path.relpath(path, os.getcwd()))
            file_path = list(set(file_path))
            for file in file_path:
                if file.endswith(".v"):

                    all_files.append(file)
                    rtl_files[os.path.abspath(file)] = "verilogSource"

                    cmd = (
                        file_types["verilogSource"] + cmd_define + " -work work " + file
                    )
                    self.ids_commands.append(cmd)
                elif file.endswith(".sv"):

                    all_files.append(file)
                    rtl_files[os.path.abspath(file)] = "systemVerilogSource"
                    cmd = (
                        file_types["systemVerilogSource"]
                        + cmd_define
                        + " -work work "
                        + file
                    )
                    self.ids_commands.append(cmd)
                elif file.endswith(".vhdl"):

                    all_files.append(file)
                    rtl_files[os.path.abspath(file)] = "vhdlSource"
                    cmd = file_types["vhdlSource"] + cmd_define + " -work work " + file
                    self.ids_commands.append(cmd)
        logger.warning(f"get_rtl_files: File list {rtl_files} ")
        logger.warning(f"ids_commands {self.ids_commands}")
        logger.warning(f"filepaths {file_path}")
        _s = self.tool_options.get("rtl_in_name")
        logger.warning(f"RTL_in name {_s}")
        logger.warning(f"self.files is {self.files}")

    def setup(self, edam):
        super().setup(edam)
        """
        def make_list(opt):
            if opt:
                opt = (
                    ((opt.replace("[", "")).replace("]", "")).replace(",", "")
                ).replace("'", "")
            return opt
        """
        self.jinja_env.filters["src_file_filter"] = self.src_file_filter
        if self.tool_options.get("indirect_source") != "true":
            (src_files, incdirs) = self._get_fileset_files(force_slash=True)

        else:
            src_files = []
            incdirs = []
            paths = [os.path.join(self.work_root)]
            # force_files = [self.tool_options.get("output_file")]
            self.get_rtl_files(paths)
            logger.warning("indir_source is true")
            logger.warning(f"ids_commands {self.ids_commands}")

        self.synth_tool = self.tool_options.get("synth", "design-compiler")

        template_vars = {
            "name": self.name,
            "src_files": src_files,
            "incdirs": incdirs + ["."],
            "tool_options": self.tool_options,
            "script_dir": self.tool_options.get("script_dir"),
            "dc_script": (self.tool_options.get("dc_script")),
            "report_dir": (self.tool_options.get("report_dir")),
            "target_library": self.tool_options.get("target_library"),
            "libs": (self.tool_options.get("libs")),
            "toplevel": self.toplevel,
            "indirect_source": (self.tool_options.get("indirect_source", "")),
            "ids_commands": self.ids_commands,
        }

        design_compiler_settings = self.tool_options.get(
            "design_compiler-settings", None
        )
        design_compiler_command = (
            "source {} && design_compiler".format(design_compiler_settings)
            if design_compiler_settings
            else "design_compiler"
        )

        jobs = self.tool_options.get("jobs", None)

        run_template_vars = {"jobs": " -jobs " + str(jobs) if jobs is not None else ""}

        self.render_template(
            "design-compiler-project.tcl.j2", self.name + ".tcl", template_vars
        )

        self.render_template(
            "design-compiler-read-sources.tcl.j2",
            self.name + "-read-sources.tcl",
            template_vars,
        )

        read_tcl = self.name + "-read-sources.tcl"
        synth_tcl = self.name + ".tcl"

        dc_tcl_scripts = [read_tcl, synth_tcl]

        self.report_dir_path = "".join(self.tool_options.get("report_dir", ["./"]))

        # Write makefile
        commands = EdaCommands()
        commands.add(["mkdir -p", self.report_dir_path + ""], ["dircreate"], "")

        targets = [
            f"{self.name}.v",
        ]
        commands.add(
            [
                "dc_shell-t -f",
                self.name + ".tcl",
                "|& tee",
                self.report_dir_path + "/synth.log",
            ],
            targets,
            dc_tcl_scripts,
            ["dircreate"],
        )

        commands.add([], ["synth"], targets)
        commands.set_default_target("synth")
        self.commands = commands

    def run(self):
        args = ["synth"]
        logger.info("Test")
        logger.info(self.name)
        # Set plusargs
        if self.plusarg:
            plusargs = []
            for key, value in self.plusarg.items():
                plusargs += ["+{}={}".format(key, self._param_value_str(value))]
            args.append("EXTRA_OPTIONS=" + " ".join(plusargs))
        return ("make", args, self.work_root)
