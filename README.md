Disassembler Benchmark
======================

This repository holds benchmarking code for various x86/x86-64 disassembler libraries.

## Results

Ubuntu 20.04 (WSL2), GCC 8.4.0, Rust 1.50.0, i5-6600K.

Test file: xul.dll from Firefox 86.0.1.7739.

# decode only

![decode only](bench-decode.png)

Library | MB/s | %
--------|------|--
iced (Rust) | 205.95 MB/s | 100.00%
yaxpeax (Rust) | 180.28 MB/s | 87.54%
diStorm (C) | 91.03 MB/s | 44.20%
udis86 (C) | 76.37 MB/s | 37.08%
Zydis (min) (C) | 66.14 MB/s | 32.11%
XED (C) | 55.75 MB/s | 27.07%
bddisasm (C) | 34.97 MB/s | 16.98%
Zydis (C) | 32.71 MB/s | 15.88%

`BeaEngine (C)`, `Capstone (C)` don't support `decode only`.


# decode + format

![decode + format](bench-decode-fmt.png)

Library | MB/s | %
--------|------|--
iced (Rust) | 115.01 MB/s | 100.00%
diStorm (C) | 58.23 MB/s | 50.63%
yaxpeax (Rust) | 39.85 MB/s | 34.65%
Zydis (C) | 20.99 MB/s | 18.25%
bddisasm (C) | 15.83 MB/s | 13.77%
XED (C) | 15.14 MB/s | 13.17%
Capstone (C) | 13.62 MB/s | 11.84%
BeaEngine (C) | 13.32 MB/s | 11.58%
udis86 (C) | 11.62 MB/s | 10.10%


# format only

![format only](bench-fmt.png)

Library | MB/s | %
--------|------|--
iced (Rust) | 260.45 MB/s | 100.00%
diStorm (C) | 161.59 MB/s | 62.04%
Zydis (C) | 58.56 MB/s | 22.49%
yaxpeax (Rust) | 51.16 MB/s | 19.64%
bddisasm (C) | 28.94 MB/s | 11.11%
XED (C) | 20.79 MB/s | 7.98%
udis86 (C) | 13.70 MB/s | 5.26%

`BeaEngine (C)`, `Capstone (C)` don't support `format only`.

This is `time(format) = time(decode+format) - time(decode)` converted to MB/s.

## Candidates

[Capstone](https://github.com/aquynh/capstone)

[DiStorm](https://github.com/gdabah/distorm)

[XED](https://github.com/intelxed/xed)

[Zydis](https://github.com/zyantific/zydis)

[iced](https://github.com/icedland/iced)

[bddisasm](https://github.com/bitdefender/bddisasm)

[yaxpeax-x86](https://github.com/iximeow/yaxpeax-x86)

[udis86](https://github.com/vmt/udis86)

[BeaEngine](https://github.com/BeaEngine/beaengine)

## Benchmarking

Windows:

```cmd
REM Start "x64 Native Tools Command Prompt for VS 2019"
REM Start git bash:
"C:\Program Files\Git\bin\bash.exe"
```

Windows/Linux/macOS:

```bash
git clone --recursive 'https://github.com/icedland/disas-bench.git'
cd disas-bench.git
./make-all.sh
# Windows: python
python3 -mvenv venv
# Windows: source venv/Scripts/activate
source venv/bin/activate
pip install -r requirements.txt
# Optional args: <code-offset> <code-len> <filename> [loop-count]
python bench.py
```

The optional `bench.py` arguments are:

- `<code-offset>` = offset of the code section (in decimal or 0x hex)
- `<code-len>` = length of the code section (in decimal or 0x hex)
- `<filename>` = 64-bit x86 binary file to decode and format
- `[loop-count]` = optional loop count. Total number of bytes decoded and formatted is `<code-len> * [loop-count]`

You can use `dumpbin.exe` (Windows) or `objdump` to get the offset and size of the code section.

### dumpbin (start "x64 Native Tools Command Prompt for VS 2019")

Find `.text` section and use `<code-len> = virtual size` (`4CFA6B6` below) and `<code-offset> = file pointer to raw data` (`400` below). All values are in hex so add a 0x prefix when passing the values to `bench.py`.

```text
C:\path> dumpbin -headers filename.dll

...
SECTION HEADER #1
   .text name
 4CFA6B6 virtual size
    1000 virtual address (0000000180001000 to 0000000184CFB6B5)
 4CFA800 size of raw data
     400 file pointer to raw data (00000400 to 04CFABFF)
...
```

### objdump

Find `.text` section and set `<code-len>` to the first 32-bit value (`04cfa6b6` below) and `<code-offset>` to the last 32-bit value (`00000400` below). All values are in hex so add a 0x prefix when passing the values to `bench.py`.

```text
$ objdump -h filename

...
Sections:
Idx Name          Size      VMA               LMA               File off  Algn
  0 .text         04cfa6b6  0000000180001000  0000000180001000  00000400  2**4
                  CONTENTS, ALLOC, LOAD, READONLY, CODE
...
```

## Contributing

If you feel like the benchmark for a lib doesn't drive it to its full potential or treats it unfairly, I'd be happy to accept PRs with improvements!
