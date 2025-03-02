import logging
import os.path
import re

from edalize.tools.edatool import Edatool
from edalize.utils import EdaCommands

logger = logging.getLogger(__name__)


class Primepower(Edatool):

    description = "The Primepower backend executes Synopsys Primepower for performing averaged and dynamic power analysis"

    TOOL_OPTIONS = {
        "pp_script_dir": {
            "type": "str",
            "desc": "Path to Primepower scripts (e.g. /home/user/project/synopsys/scripts)",
        },
        "pp_script": {
            "type": "str",
            "desc": "Name of the primepower script to run [located in script_dir](e.g. synth.tcl)",
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
        "indir_source": {
            "type": "str",
            "desc": "set to true (in quotes) when the search path for the RTL is not in the .core, but output from a previous tool ",
        },
        "rtl_in_name": {
            "type": "str",
            "desc": "Name of the generated RTL to be synthesized",
        },
        "mode": {"type": "str", "desc": "averaged or time_based "},
        "lib_dir": {
            "type": "str",
            "desc": "Add the search paths",
        },
        "verilog_dir": {
            "type": "str",
            "desc": "Add verilog search paths",
        },
        "vcdpath": {"type": "str", "desc": "VCD File for the simulation input"},
        "vcd_strip_path": {"type": "str", "desc": "VCD Strip Path"},
        "netlistpath": {
            "type": "str",
            "desc": "Path to the netlist relative to self.work_root netlist/",
        },
        "netlistname": {
            "type": "str",
            "desc": "Name of the netlist without the extension",
        },
    }

    # To get the same data structure for generated src files to dc
    def _get_fileset_files_ids(self, force_slash=False):
        paths = [
            self.tool_options.get("verilog_dir"),
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
            if os.path.isdir(path):
                for file in os.listdir(path):
                    if file.endswith(".v"):
                        fname = file
                        ftype = "verilogSource"
                        src_files.append(File(fname, ftype, fname))
                    elif file.endswith(".sv"):
                        fname = file
                        ftype = "systemVerilogSource"
                        src_files.append(File(fname, ftype, fname))
                    elif file.endswith(".vhdl"):
                        fname = file
                        ftype = "vhdlSource"
                        src_files.append(File(fname, ftype, fname))
                    elif file.endswith(".sdc"):
                        fname = file
                        ftype = "sdc"
                        src_files.append(File(fname, ftype, fname))
                    elif file.endswith(".sdf"):
                        fname = file
                        ftype = "sdf"
                        src_files.append(File(fname, ftype, fname))
                    elif file.endswith(".spef"):
                        fname = file
                        ftype = "spef"
                        src_files.append(File(fname, ftype, fname))
                    elif file.endswith(".vcd"):
                        fname = file
                        ftype = "vcd"
                        src_files.append(File(fname, ftype, fname))
                    elif file.endswith(".fsdb"):
                        fname = file
                        ftype = "fsdb"
                        src_files.append(File(fname, ftype, fname))
                    else:
                        pass
            elif os.path.isfile(path):
                if file.endswith(".v"):
                    fname = file
                    ftype = "verilogSource"
                    src_files.append(File(fname, ftype, fname))
                elif file.endswith(".sv"):
                    fname = file
                    ftype = "systemVerilogSource"
                    src_files.append(File(fname, ftype, fname))
                elif file.endswith(".vhdl"):
                    fname = file
                    ftype = "vhdlSource"
                    src_files.append(File(fname, ftype, fname))
                elif file.endswith(".sdc"):
                    fname = file
                    ftype = "sdc"
                    src_files.append(File(fname, ftype, fname))
                elif file.endswith(".sdf"):
                    fname = file
                    ftype = "sdf"
                    src_files.append(File(fname, ftype, fname))
                elif file.endswith(".spef"):
                    fname = file
                    ftype = "spef"
                    src_files.append(File(fname, ftype, fname))
                elif file.endswith(".vcd"):
                    fname = file
                    ftype = "vcd"
                    src_files.append(File(fname, ftype, fname))
                elif file.endswith(".fsdb"):
                    fname = file
                    ftype = "fsdb"
                    src_files.append(File(fname, ftype, fname))
                else:
                    pass
            else:
                raise Exception("Path is not a valid directory")

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
        # print("Src Files: ", [i.file_type for i in src_files])
        return (src_files, incdirs)

    def src_file_filter(self, f):
        logger.info("Files: %s", f)
        file_types = {
            "verilogSource": "read_verilog",
            "systemVerilogSource": "read_sverilog",
            "vhdlSource": "read_vhdl",
            "tclSource": "source",
            "sdc": "read_sdc",
            "sdf": "read_sdf",
            "spef": "read_parasitics",
            "vcd": "read_vcd",
            "fsdb": "read_fsdb",
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
                    # + "-time {4990 5730} "
                    + f.name
                )
                return cmd
            elif _file_type == "fsdb":
                cmd += (
                    file_types[_file_type]
                    + " "
                    + "-strip_path"
                    + " "
                    + self.tool_options.get("vcd_strip_path", None)
                    + " "
                    # + "-time {4990 5730} "
                    + f.name
                )
                return cmd
            elif _file_type == "sdc":
                cmd += file_types[_file_type] + " " + f.name
            elif _file_type == "spef":
                cmd += file_types[_file_type] + " " + f.name
            elif _file_type == "sdf":
                cmd += file_types[_file_type] + " " + f.name
            else:
                pass
                # cmd += file_types[_file_type] + " " + f.name
            return cmd

        if _file_type == "user":
            return ""

        _s = "{} has unknown file type '{}', interpretation is up to PrimePower Compiler in tools"
        logger.warning(_s.format(f.name, f.file_type))

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
            "sdc": "read_sdc",
            "sdf": "read_sdf",
            "spef": "read_parasitics",
            "vcd": "read_vcd",
        }

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

    def setup(self, edam):
        super().setup(edam)

        def make_list(opt):
            if opt:
                opt = (
                    ((opt.replace("[", "")).replace("]", "")).replace(",", "")
                ).replace("'", "")
            return opt

        self.jinja_env.filters["src_file_filter"] = self.src_file_filter
        if self.tool_options.get("indirect_source") != "true":
            (src_files, incdirs) = self._get_fileset_files(force_slash=True)

        else:
            (src_files, incdirs) = self._get_fileset_files_ids(force_slash=True)
            logger.warning("indir_source is true")
            logger.warning(f"ids_commands {self.ids_commands}")

        self.synth_tool = self.tool_options.get("synth", "design-compiler")

        vcdpath = ""
        netlistpath = ""
        for file in self.files:
            if file.get("file_type") == "vcd":
                vcdpath = file.get("name")
        if self.tool_options.get("indirect_source") == "true":
            netlistpath = os.path.join(
                os.path.relpath(self.tool_options.get("netlistpath", "")),
                self.tool_options.get("netlistname", "") + ".v",
            )
            print("netlist path:", netlistpath)
            sdc_path = os.path.join(
                self.tool_options.get("netlistpath", ""),
                self.tool_options.get("netlistname", "") + ".sdc",
            )
            spef_path = os.path.join(
                self.tool_options.get("netlistpath", ""),
                self.tool_options.get("netlistname", "") + ".spef",
            )
            sdf_path = os.path.join(
                self.tool_options.get("netlistpath", ""),
                self.tool_options.get("netlistname", "") + ".sdf",
            )
        else:
            for file in self.files:
                if file.get("file_type") == "verilogSource":
                    netlistpath = file.get("name")
                if file.get("file_type") == "sdc":
                    sdc_path = file.get("name")
            spef_path = sdf_path = ""

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
            "vcdpath": vcdpath,
            "netlistpath": netlistpath,
            # "sdc_path": sdc_path,
            # "sdf_path": sdf_path,
            "spef_path": spef_path,
            "vcd_strip_path": self.tool_options.get("vcd_strip_path", ""),
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
            "primepower-project.tcl.j2", self.name + "_pp.tcl", template_vars
        )

        pp_tcl = self.name + "_pp.tcl"

        pp_tcl_scripts = [pp_tcl]

        self.report_dir_path = "".join(self.tool_options.get("report_dir", ["./"]))

        # Write makefile
        commands = EdaCommands()
        # commands.add(["mkdir -p", self.report_dir_path + ""], ["dircreate"], "")

        targets = [
            "poweranalyze",
        ]
        commands.add(
            [
                "mkdir -p",
                self.report_dir_path,
                "&&",
                "pwr_shell -f",
                self.name + "_pp.tcl",
                "|& tee",
                self.report_dir_path + "/pp.log",
            ],
            targets,
            pp_tcl_scripts,
            [],
            # ["dircreate"],
        )

        # commands.add([], ["synth"], targets)
        commands.set_default_target("poweranalyze")
        # logger.warning(f"filesetfileids {self._get_fileset_files_ids}")
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
