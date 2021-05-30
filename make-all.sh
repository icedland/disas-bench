#!/usr/bin/env bash
set -e

#compiler=clang
#compiler=gcc
compiler=whatever

if [[ `uname -s` == "MINGW"* ]]; then
    is_windows=y
elif [[ `uname -s` == "Darwin" ]]; then
    is_mac=y
else
    is_linux=y
fi

case "$compiler" in
"clang")
    if [[ "$is_windows" == "y" ]]; then
        if [[ ! `which clang-cl.exe` ]]; then
            echo "[-] Unable to find clang-cl, is it installed?" 1>&2
            exit 1
        fi
        export CC=$(cygpath -m "$(which clang-cl.exe)")
        export CXX="$CC"
        export AR=$(cygpath -m "$(which llvm-ar)")
        export RANLIB=$(cygpath -m "$(which llvm-ranlib)")
    else
        export CC=$(which clang)
        export CXX=$(which clang++)
        export AR=$(which llvm-ar)
        export RANLIB=$(which llvm-ranlib)
    fi
    BEAENGINE_CLANG=-DUSE_CLANG=on
    export BEA_COMPILER_NAME=clang
    XEDCOMPILER="--compiler=clang"
    MSBUILD_TOOLSET=-p:PlatformToolset=ClangCL
    ;;
"gcc")
    export CC=$(which gcc)
    export CXX=$(which g++)
    export AR=$(which gcc-ar)
    export RANLIB=$(which gcc-ranlib)
    export BEA_COMPILER_NAME=gnu
    XEDCOMPILER="--compiler=gnu"
    ;;
"whatever")
    MSBUILD_TOOLSET=-p:PlatformToolset=v142
    if [[ "$is_windows" == "y" ]]; then
        export CC=$(cygpath -w "$(which cl.exe)")
        export CXX="$CC"
    else
        # Assume gcc
        export CC=$(which gcc)
        export CXX=$(which g++)
        export AR=$(which gcc-ar)
        export RANLIB=$(which gcc-ranlib)
        export BEA_COMPILER_NAME=gnu
        XEDCOMPILER="--compiler=gnu"
    fi
    ;;
*)
    echo "Invalid compiler option: $compiler";
    exit 1
    ;;
esac

if [[ "$is_windows" == "y" ]]; then
    make='nmake -f Makefile.win'
else
    make=make
fi

python=python

if [[ "$is_windows" == "y" ]]; then
    if ! link.exe --help 2>&1 | grep -i Microsoft > /dev/null; then
        export PATH=$(echo "$PATH" | tr ':' '\n' | grep HostX64):$PATH
    fi
    if ! link.exe --help 2>&1 | grep -i Microsoft > /dev/null; then
        echo "[-] Couldn't find VS 64-bit link.exe. Make sure it's in your path!"
        exit 1
    fi
else
    if [[ ! `which cmake` ]]; then
        echo "[-] Unable to find CMake, is it installed?" 1>&2
        exit 1
    fi
    if [[ $(which python3) ]]; then
        python=python3
    elif [[ ! `which $python` ]]; then
        echo "[-] Unable to find Python, is it installed?" 1>&2
        exit 1
    fi
    if [[ ! `which cargo` ]]; then
        echo "[-] Unable to find cargo (Rust), is it installed?" 1>&2
        exit 1
    fi
fi

# Build Capstone

echo "[*] Building Capstone ..."
cd libs/capstone
mkdir -p build
cd build
if [[ "$is_windows" == "y" ]]; then
    cmake -DCMAKE_BUILD_TYPE=Release -DCAPSTONE_BUILD_STATIC_RUNTIME=ON -DCAPSTONE_ARCHITECTURE_DEFAULT=OFF -DCAPSTONE_X86_SUPPORT=ON ..
    msbuild.exe capstone-static.vcxproj -p:Configuration=Release -p:Platform=x64 $MSBUILD_TOOLSET -p:WholeProgramOptimization=true
else
    CFLAGS=-flto cmake -DCMAKE_BUILD_TYPE=Release -DCAPSTONE_BUILD_STATIC_RUNTIME=ON -DCAPSTONE_ARCHITECTURE_DEFAULT=OFF -DCAPSTONE_X86_SUPPORT=ON -DCMAKE_AR="$AR" -DCMAKE_RANLIB="$RANLIB" ..
    make capstone-static
fi
cd ../../..

# Build XED

echo "[*] Building XED ..."
cd libs/intelxed
if [[ "$is_windows" == "y" ]]; then
    # No clang, it fails when building it. Also disabled in Makefile.win
    $python mfile.py --no-encoder -v 3 --opt=3 --extra-flags=-GL
else
    $python mfile.py --no-encoder -v 3 --opt=3 --extra-flags=-flto $XEDCOMPILER --ar="$AR"
fi
cd ../..

# Build diStorm

echo "[*] Building diStorm ..."
if [[ "$is_mac" == "y" ]]; then 
    distorm_subdir=mac
elif [[ "$is_windows" == "y" ]]; then
    distorm_subdir=win32
else
    distorm_subdir=linux
fi
cd libs/distorm/make/${distorm_subdir}
if [[ "$is_windows" == "y" ]]; then
    msbuild.exe cdistorm.vcxproj -p:Configuration=clib -p:Platform=x64 $MSBUILD_TOOLSET -p:WholeProgramOptimization=true
else
    if [[ "$compiler" == "clang" ]]; then
        sed -i -e 's/^CC\s*=\s*gcc$/CC = clang/' Makefile
    fi
    sed -i -e "s#ar rs#$AR rs#" Makefile
    sed -i -e 's/CFLAGS\s*=/CFLAGS +=/' Makefile
    CFLAGS=-flto make
    git checkout Makefile
fi
cd ../../../..

# Build bddisasm

echo "[*] Building bddisasm ..."
cd libs/bddisasm
if [[ "$is_windows" == "y" ]]; then
    if [[ "$compiler" == "clang" ]]; then
        sed -i -e 's/.*IgnoreAllDefaultLibraries.*//' bddisasm/bddisasm.vcxproj
    fi
    msbuild.exe bddisasm/bddisasm.vcxproj -p:Configuration=Release -p:Platform=x64 $MSBUILD_TOOLSET -p:WholeProgramOptimization=true
    git checkout bddisasm/bddisasm.vcxproj
    cd ../..
else
    mkdir -p build
    cd build
    CFLAGS=-flto cmake -DCMAKE_BUILD_TYPE=Release -DBDD_USE_EXTERNAL_VSNPRINTF=ON -DBDD_USE_EXTERNAL_MEMSET=ON -DCMAKE_AR="$AR" -DCMAKE_RANLIB="$RANLIB" ..
    make bddisasm
    cd ../../..
fi

# Build udis86

echo "[*] Building udis86 ..."
cd libs/udis86
# Patch code that doesn't work with Python 3.x
sed -i -e 's/indent, k, e/indent, int(k), e/' scripts/ud_opcode.py
if [[ "$is_windows" == "y" ]]; then
    $python scripts/ud_itab.py docs/x86/optable.xml libudis86/
    msbuild.exe BuildVS2010/libudis86.vcxproj -p:Configuration=Release -p:Platform=x64 $MSBUILD_TOOLSET -p:WholeProgramOptimization=true
else
    ./autogen.sh
    # We can't enable lto because it gets extremely slow
    #     ./configure [...] CFLAGS=-flto AR=$(which gcc-ar) RANLIB=$(which gcc-ranlib) [...]
    # It's been disabled in bench/udis86/Makefile too
    ./configure --enable-static=yes PYTHON=$(which $python)
    make libudis86
fi
git checkout scripts/ud_opcode.py
cd ../..

echo "[*] Building BeaEngine ..."
cd libs/beaengine
mkdir -p build
cd build
sed -i -e 's/APPEND BEA_FLAGS -fomit-frame-pointer -O2/APPEND BEA_FLAGS -fomit-frame-pointer -O3 -flto/' ../CMakeLists.txt
# It's decode+disasm unless `-DoptBUILD_LITE=on` is used (decode only), but if we add it, we get errors
cmake -DoptHAS_OPTIMIZED=on -DoptHAS_SYMBOLS=off -DoptBUILD_64BIT=on $BEAENGINE_CLANG ..
if [[ "$is_windows" == "y" ]]; then
    msbuild.exe BeaEngine.sln -p:Configuration=Release -p:Platform=x64 $MSBUILD_TOOLSET -p:WholeProgramOptimization=true
else
    make
fi
git checkout ../CMakeLists.txt
cd ../../..

# Build benchmark tools

echo "[*] Building Capstone benchmark ..."
cd bench/cs
$make
cd ../..

echo "[*] Building Zydis benchmark ..."
cd bench/zydis
if [[ "$is_windows" == "y" ]]; then
    mkdir -p build
    cd build
    cmake -DCMAKE_BUILD_TYPE=Release ..
    msbuild.exe bench-zydis.sln -p:Configuration=Release -p:Platform=x64 $MSBUILD_TOOLSET -p:WholeProgramOptimization=true
    cp Release/*.exe ..
    cd ..
else
    CFLAGS=-flto cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_AR="$AR" -DCMAKE_RANLIB="$RANLIB" .
    $make
fi
cd ../..

echo "[*] Building XED benchmark ..."
cd bench/xed
$make
cd ../..

echo "[*] Building diStorm benchmark ..."
cd bench/distorm
$make
cd ../..

echo "[*] Building iced benchmark ..."
cd bench/iced-x86
$make
cd ../..

echo "[*] Building bddisasm benchmark ..."
cd bench/bddisasm
$make
cd ../..

echo "[*] Building yaxpeax-x86 benchmark ..."
cd bench/yaxpeax
$make
cd ../..

echo "[*] Building udis86 benchmark ..."
cd bench/udis86
$make
cd ../..

echo "[*] Building BeaEngine benchmark ..."
cd bench/beaengine
$make
cd ../..

echo "[+] All done!"
