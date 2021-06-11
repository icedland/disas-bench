Disassembler Benchmark
======================

This repository holds benchmarking code for various x86/x86-64 disassembler libraries.

## Results

Kubuntu 21.04, gcc 10.3.0, Rust 1.52.1, i5-6600K.

Test file: xul.dll from Firefox 86.0.1.7739 (77MB code section).

# decode only

![decode only](bench-decode.png)

Library | MB/s | %
--------|------|--
iced (Rust) | 256.69 MB/s | 100.00%
yaxpeax (Rust) | 182.08 MB/s | 70.93%
diStorm (C) | 92.17 MB/s | 35.91%
udis86 (C) | 80.72 MB/s | 31.44%
Zydis (min) (C) | 61.33 MB/s | 23.89%
XED (C) | 55.39 MB/s | 21.58%
bddisasm (C) | 35.48 MB/s | 13.82%
Zydis (C) | 34.19 MB/s | 13.32%

`BeaEngine (C)`, `Capstone (C)` don't support `decode only`.


# decode + format

![decode + format](bench-decode-fmt.png)

Library | MB/s | %
--------|------|--
iced (Rust) | 149.21 MB/s | 100.00%
diStorm (C) | 58.85 MB/s | 39.44%
yaxpeax (Rust) | 40.05 MB/s | 26.84%
Zydis (C) | 22.24 MB/s | 14.91%
bddisasm (C) | 16.00 MB/s | 10.72%
XED (C) | 15.67 MB/s | 10.50%
Capstone (C) | 14.02 MB/s | 9.39%
BeaEngine (C) | 13.42 MB/s | 8.99%
udis86 (C) | 12.02 MB/s | 8.05%


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
cd disas-bench
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
