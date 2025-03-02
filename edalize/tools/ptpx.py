import logging
import os.path
import re

from edalize.tools.edatool import Edatool
from edalize.utils import EdaCommands

logger = logging.getLogger(__name__)


class Ptpx(Edatool):

    description = (
        "Synopsys PTPX backend that can be used to invoke PrimeTime and PrimePower"
    )

    TOOL_OPTIONS = {
        "pt_script_dir": {
            "type": "str",
            "desc": "Path to Primepower scripts (e.g. /home/user/project/synopsys/scripts)",
        },
        "pt_script": {
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
        "lib_dir": {
            "type": "str",
            "desc": "Add the search paths",
        },
        "verilog_dir": {
            "type": "str",
            "desc": "Add verilog search paths",
        },
        "postbuildpy": {
            "type": "str",
            "desc": "Post build python script to run",
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
        return (src_files, incdirs)

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
        print("file type", _file_type)
        if _file_type in file_types:
            cmd = ""
            if _file_type == "sdc":
                cmd += file_types[_file_type] + " " + f.name
            elif _file_type == "spef":
                cmd += file_types[_file_type] + " " + f.name
            elif _file_type == "sdf":
                cmd += file_types[_file_type] + " " + f.name
            else:
                pass
                # cmd += file_types[_file_type] + " " + f.name
            print("cmd:", cmd)
            return cmd

        if _file_type == "user":
            return ""

        _s = "{} has unknown file type '{}', interpretation is up to PrimePower Compiler in tools"
        logger.warning(_s.format(f.name, f.file_type))

    ids_commands = []

    def setup(self, edam):
        super().setup(edam)

        def make_list(opt):
            if opt:
                opt = (
                    ((opt.replace("[", "")).replace("]", "")).replace(",", "")
                ).replace("'", "")
            return opt

        self.jinja_env.filters["src_file_filter"] = self.src_file_filter
        (src_files, incdirs) = self._get_fileset_files(force_slash=True)

        self.synth_tool = self.tool_options.get("synth", "design-compiler")
        vcdname = ""
        netlistpath = ""
        logger.info("All Files %s", self.files)
        for file in self.files:
            if file.get("file_type") == "vcd":
                vcdname = file.get("name")
                # logger.info("vcd name: %s", vcdname)
            if file.get("file_type") == "verilogSource":
                netlistpath = file.get("name")
                # logger.info("netlist path: %s", netlistpath)
        logger.info("Here")
        template_vars = {
            "name": self.name,
            "src_files": src_files,
            "incdirs": incdirs + ["."],
            "tool_options": self.tool_options,
            "mode": self.tool_options.get("mode"),
            "lib_dir": self.tool_options.get("lib_dir"),
            "verilog_dir": self.tool_options.get("verilog_dir"),
            "script_dir": self.tool_options.get("pt_script_dir"),
            "pp_script": make_list(self.tool_options.get("pt_script")),
            "report_dir": make_list(self.tool_options.get("report_dir")),
            "target_library": self.tool_options.get("target_library"),
            "libs": make_list(self.tool_options.get("libs")),
            "toplevel": self.toplevel,
            "vcdpath": "",
            "netlistpath": netlistpath,
            "postbuildpy": self.tool_options.get("postbuildpy"),
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
            "ptpx-project.tcl.j2", self.name + "_pt.tcl", template_vars
        )

        pp_tcl = self.name + "_pp.tcl"

        pp_tcl_scripts = [pp_tcl]

        self.report_dir_path = "".join(self.tool_options.get("report_dir", ["./"]))
        self.edam = edam.copy()
        # print("EDAM here:", self.edam)
        for k, v in self.edam.items():
            if k == "files":
                for f in v:
                    if f["file_type"] == "sdc" and "max_freq_sdc.sdc" in f["name"]:
                        self.edam["files"].remove(f)

        self.edam["files"].append({"name": "post_sta_max_freq.sdc", "file_type": "sdc"})
        # print("EDAM after:", self.edam)
        # Write makefile
        commands = EdaCommands()
        # commands.add(["mkdir -p", self.report_dir_path + ""], ["dircreate"], "")

        targets = [
            "timing",
        ]
        commands.add([], [".PHONY"], targets)
        # commands.add([],[".PHONY"],["dircreate"])
        commands.add(
            [
                "mkdir -p",
                self.report_dir_path,
                "&&",
                "pt_shell -f",
                self.name + "_pt.tcl",
                "|& tee",
                self.report_dir_path + "/pt.log",
                "|| true",
            ],
            targets,
            [],
            [],
        )

        # commands.add([], ["synth"], targets)
        commands.set_default_target("timing")
        # logger.warning(f"filesetfileids {self._get_fileset_files_ids}")
        self.commands = commands

    def run(self):
        args = ["timing"]
        logger.info("Test")
        logger.info(self.name)
        # Set plusargs
        if self.plusarg:
            plusargs = []
            for key, value in self.plusarg.items():
                plusargs += ["+{}={}".format(key, self._param_value_str(value))]
            args.append("EXTRA_OPTIONS=" + " ".join(plusargs))
        return ([], [], [])
        # return ("make", args, self.work_root)
