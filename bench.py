from enum import IntEnum
from typing import Dict, List, Set
import os
import platform
import re
import subprocess
import sys
import time
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


root_dir = os.path.dirname(os.path.realpath(__file__))


class Options:
    code_filename = os.path.join(root_dir, "input", "xul.dll")
    file_code_offs = 0x400
    file_code_len = 0x24603E1
    code_loop_count = 20


class LangKind(IntEnum):
    C = 0
    RUST = 1


class DisasmLib:
    def __init__(self, name: str, language: LangKind, flags: List[str] = []) -> None:
        self.name = name
        self.language = language
        self.flags = sorted(flags)
        if language == LangKind.C:
            self.language_str = "C"
        elif language == LangKind.RUST:
            self.language_str = "Rust"
        else:
            raise ValueError(f"Invalid LangKind: {language}")
        if len(flags) == 0:
            self.name_flags = name
        else:
            self.name_flags = f"{name} ({', '.join(flags)})"
        self.name_flags_lang = f"{self.name_flags} ({self.language_str})"

    def __equals(self, o: "DisasmLib") -> bool:
        return self.name == o.name and self.language == o.language and self.flags == o.flags

    def __eq__(self, o: object) -> bool:
        if type(o) == DisasmLib:
            return self.__equals(o)
        return False

    def __ne__(self, o: object) -> bool:
        if type(o) == DisasmLib:
            return not self.__equals(o)
        return False

    def __hash__(self) -> int:
        return hash(self.name) ^ hash(self.language) ^ sum(hash(a)
                                                           for a in self.flags)


class BenchKind(IntEnum):
    DECODE_FMT = 0
    DECODE = 1
    FMT = 2


class BenchInfo:
    def __init__(self, bench_kind: BenchKind, rel_path: str, lib: DisasmLib) -> None:
        if platform.system() == "Windows":
            rel_path = rel_path.replace("/", "\\") + ".exe"
        if not os.path.exists(rel_path):
            raise ValueError(f"File {rel_path} does not exist")
        self.bench_kind = bench_kind
        self.lib = lib
        self.rel_path = rel_path
        self.full_path = os.path.join(root_dir, rel_path)

        if bench_kind == BenchKind.DECODE_FMT:
            bench_str = "decode+fmt"
        elif bench_kind == BenchKind.DECODE:
            bench_str = "decode"
        elif bench_kind == BenchKind.FMT:
            bench_str = "fmt"
        else:
            raise ValueError(f"Invalid enumvalue {bench_kind}")
        self.bench_name = f"{lib.name_flags} {bench_str}"

        self.time_s = 0.0
        self.mb_per_secs = 0.0


class BenchResult:
    def __init__(self, bench_kind: BenchKind, bench_name: str, lib: DisasmLib, time_s: float, mb_per_secs: float) -> None:
        self.bench_kind = bench_kind
        self.bench_name = bench_name
        self.lib = lib
        self.time_s = time_s
        self.mb_per_secs = mb_per_secs


def to_int(s: str) -> int:
    if s.startswith("0x"):
        return int(s[2:], 16)
    return int(s)


def parse_command_line() -> Options:
    options = Options()

    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 4 or len(sys.argv) == 5:
        options.file_code_offs = to_int(sys.argv[1])
        options.file_code_len = to_int(sys.argv[2])
        options.code_filename = sys.argv[3]
        if len(sys.argv) >= 5:
            options.code_loop_count = to_int(sys.argv[4])
        else:
            # Match the old file + loop-count
            options.code_loop_count = max(
                1, round(0x24603E1 * 20 / options.file_code_len))
    else:
        print("Expected no args or:")
        print(
            f"  {sys.argv[0]} <code-offset> <code-len> <filename> [loop-count]")
        sys.exit(1)

    if not os.path.exists(options.code_filename):
        print(f"File `{options.code_filename}` does not exist")
        sys.exit(1)
    if options.file_code_offs < 0:
        print(f"Invalid code-offset {options.file_code_offs}")
        sys.exit(1)
    if options.file_code_len < 0:
        print(f"Invalid code-len {options.file_code_len}")
        sys.exit(1)
    if options.code_loop_count < 0 or type(options.code_loop_count) != int:
        print(f"Invalid loop-count {options.code_loop_count}")
        sys.exit(1)

    return options


def run_benchmarks(options: Options, targets: List[BenchInfo]) -> None:
    # Open & read file once before to make sure it's in OS cache.
    with open(options.code_filename, "rb") as f:
        f.read()

    print("[*] Running all benchmarks")

    for cur_target in targets:
        print(f"[*] Benchmarking {cur_target.rel_path} ...")
        pwd = os.getcwd()
        os.chdir(os.path.dirname(cur_target.full_path))

        process_args = [
            cur_target.full_path,
            f"0x{options.code_loop_count:X}",
            f"0x{options.file_code_offs:X}",
            f"0x{options.file_code_len:X}",
            options.code_filename
        ]
        prev = time.time()
        process = subprocess.run(process_args, stdout=subprocess.PIPE)
        diff = time.time() - prev
        os.chdir(pwd)
        if process.returncode != 0:
            raise ValueError(
                f"{cur_target.rel_path} exited with code {process.returncode}")
        output = process.stdout.decode("utf-8")
        m = re.search("(\\S+) ms", output)
        if m is None:
            raise ValueError(f"Couldn't parse output: `{output}`")
        groups = m.groups()
        total_s = float(groups[0]) / 1000.0

        print(output, end="")
        cur_target.time_s = total_s
        cur_target.mb_per_secs = options.file_code_len / \
            1024 / 1024 * options.code_loop_count / total_s
        print(f"[+] Completed in {total_s:.2f} ({diff:.2f}) seconds")


def generate_chart(title: str, what: str, filename: str, libs: Set[DisasmLib], targets: List[BenchResult]) -> None:
    plt.rcdefaults()
    TEXT_COLOR = "#DDDDDD"
    mpl.rcParams["text.color"] = TEXT_COLOR
    mpl.rcParams["axes.labelcolor"] = TEXT_COLOR
    mpl.rcParams["xtick.color"] = TEXT_COLOR
    mpl.rcParams["ytick.color"] = TEXT_COLOR
    mpl.rcParams["axes.edgecolor"] = "#2A2A2A"

    fig = plt.figure(figsize=(10, 5), facecolor="#262626")
    ax = fig.add_subplot(1, 1, 1, facecolor="#222222")

    lib_names = [os.path.basename(target.bench_name) for target in targets]
    y_pos = np.arange(len(lib_names))
    mbs = [x for x in map(lambda target: target.mb_per_secs, targets)]
    best = mbs.index(max(mbs))

    ax.barh(
        y_pos,
        mbs,
        align="center",
        color="#3058AD"
    )[best].set_color("#3D7A23")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(lib_names)
    ax.invert_yaxis()
    ax.set_xlabel("MB/s")
    ax.set_title(f"{title} ({what})" if len(what) != 0 else title)
    plt.subplots_adjust(left=0.2, right=0.95, top=0.9, bottom=0.1)
    fig.savefig(filename)

    print_md_table = len(what) != 0
    if len(what) == 0:
        what = "All"
    print()
    print(f"# {what}")
    print()
    print(f"![{what}]({filename})")
    print()
    if print_md_table:
        print("Library | MB/s | %")
        print("--------|------|--")
        # We ignore 'lib.flags' here
        not_used_libs = set((lib.name, lib.language, lib.language_str)
                            for lib in libs)
        sorted_targets = sorted(targets, key=lambda target: (
            target.bench_kind, target.time_s))
        best_time_s = sorted_targets[0].time_s
        for target in sorted_targets:
            print(
                f"{target.bench_name} | {target.mb_per_secs:.2f} MB/s | {best_time_s / target.time_s * 100:.2f}%")
            key = (target.lib.name, target.lib.language,
                   target.lib.language_str)
            if key in not_used_libs:
                not_used_libs.remove(key)
        not_used_libs = sorted(
            not_used_libs, key=lambda lib: (lib[0].lower(), lib[1]))
        not_used_libs = [f"`{lib[0]} ({lib[2]})`" for lib in not_used_libs]
        if len(not_used_libs) != 0:
            dont = "doesn't" if len(not_used_libs) == 1 else "don't"
            print()
            print(f"{', '.join(not_used_libs)} {dont} support `{what}`.")
        print()


def main() -> None:
    # fmt: off
    targets = [
        # Decode + format
        BenchInfo(BenchKind.DECODE_FMT, "bench/cs/bench-cs-fmt", DisasmLib("Capstone", LangKind.C)),
        BenchInfo(BenchKind.DECODE_FMT, "bench/zydis/bench-zydis-full-fmt", DisasmLib("Zydis", LangKind.C)),
        BenchInfo(BenchKind.DECODE_FMT, "bench/xed/bench-xed-fmt", DisasmLib("XED", LangKind.C)),
        BenchInfo(BenchKind.DECODE_FMT, "bench/distorm/bench-distorm-fmt", DisasmLib("diStorm", LangKind.C)),
        BenchInfo(BenchKind.DECODE_FMT, "bench/iced-x86/bench-iced-fmt", DisasmLib("iced", LangKind.RUST)),
        BenchInfo(BenchKind.DECODE_FMT, "bench/bddisasm/bench-bddisasm-fmt", DisasmLib("bddisasm", LangKind.C)),
        BenchInfo(BenchKind.DECODE_FMT, "bench/yaxpeax/bench-yaxpeax-fmt", DisasmLib("yaxpeax", LangKind.RUST)),
        BenchInfo(BenchKind.DECODE_FMT, "bench/udis86/bench-udis86-fmt", DisasmLib("udis86", LangKind.C)),
        BenchInfo(BenchKind.DECODE_FMT, "bench/beaengine/bench-beaengine-fmt", DisasmLib("BeaEngine", LangKind.C)),

        # Decode only
        BenchInfo(BenchKind.DECODE, "bench/zydis/bench-zydis-min-no-fmt", DisasmLib("Zydis", LangKind.C, ["min"])),
        BenchInfo(BenchKind.DECODE, "bench/zydis/bench-zydis-full-no-fmt", DisasmLib("Zydis", LangKind.C)),
        BenchInfo(BenchKind.DECODE, "bench/xed/bench-xed-no-fmt", DisasmLib("XED", LangKind.C)),
        BenchInfo(BenchKind.DECODE, "bench/distorm/bench-distorm-no-fmt", DisasmLib("diStorm", LangKind.C)),
        BenchInfo(BenchKind.DECODE, "bench/iced-x86/bench-iced-no-fmt", DisasmLib("iced", LangKind.RUST)),
        BenchInfo(BenchKind.DECODE, "bench/bddisasm/bench-bddisasm-no-fmt", DisasmLib("bddisasm", LangKind.C)),
        BenchInfo(BenchKind.DECODE, "bench/yaxpeax/bench-yaxpeax-no-fmt", DisasmLib("yaxpeax", LangKind.RUST)),
        BenchInfo(BenchKind.DECODE, "bench/udis86/bench-udis86-no-fmt", DisasmLib("udis86", LangKind.C)),
    ]
    # fmt: on

    options = parse_command_line()
    run_benchmarks(options, targets)

    print("[*] Generating charts and MD tables")
    libs = set(target.lib for target in targets)
    show_all = False
    if show_all:
        generate_chart("Throughput", "", "bench.png", libs, [BenchResult(
            x.bench_kind, x.bench_name, x.lib, x.time_s, x.mb_per_secs) for x in targets])
    generate_chart("Throughput", "decode only", "bench-decode.png", libs, [BenchResult(
        x.bench_kind, x.lib.name_flags_lang, x.lib, x.time_s, x.mb_per_secs) for x in targets if x.bench_kind == BenchKind.DECODE])
    generate_chart("Throughput", "decode + format", "bench-decode-fmt.png", libs, [BenchResult(
        x.bench_kind, x.lib.name_flags_lang, x.lib, x.time_s, x.mb_per_secs) for x in targets if x.bench_kind == BenchKind.DECODE_FMT])

    show_fmt_only = False
    if show_fmt_only:
        to_index = {target: i for i, target in enumerate(targets)}
        d: Dict[str, List[BenchInfo]] = dict()
        for target in targets:
            d.setdefault(target.lib.name_flags_lang, [])
            d.get(target.lib.name_flags_lang).append(target)
        fmt_list: List[(int, BenchInfo)] = []
        for l in d.values():
            if len(l) == 1:
                continue
            if len(l) != 2:
                raise ValueError(f"Expected 1 or 2 elements but got {len(l)}")
            obj = {e.bench_kind: e for e in l}
            if BenchKind.DECODE_FMT not in obj or BenchKind.DECODE not in obj:
                raise ValueError(
                    "Couldn't find decode+fmt and decode benchmarks")
            time_s = obj[BenchKind.DECODE_FMT].time_s - \
                obj[BenchKind.DECODE].time_s
            if time_s <= 0:
                raise ValueError(f"Invalid elapsed time: {time_s}")
            fmt_list.append((min(to_index[l[0]], to_index[l[1]]), BenchResult(
                BenchKind.FMT, l[0].lib.name_flags_lang, l[0].lib, time_s, options.file_code_len / 1024 / 1024 * options.code_loop_count / time_s)))
        fmt_list.sort(key=lambda a: a[0])
        generate_chart("Throughput", "format only", "bench-fmt.png", libs,
                       [info for _, info in fmt_list])
        print(
            "This is `time(format) = time(decode+format) - time(decode)` converted to MB/s.")

    print()
    print("[+] See all created *.png files and all MD tables above")


main()
