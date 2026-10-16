#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"

os=linux
[[ "$OSTYPE" == "darwin"* ]] && os=mac
export os

if [ "$os" == "mac" ]; then
	[ -z "$cores" ] && cores=$(sysctl -n hw.ncpu)
	# various things rely on GNU behaviour
	export INSTALL=`which ginstall`
	export SED=gsed
else
	[ -z "$cores" ] && cores=$(grep -c ^processor /proc/cpuinfo)
fi
cores=${cores:-4}

# configure pkg-config paths if inside buildscripts
if [ -n "$ndk_triple" ]; then
	export PKG_CONFIG_SYSROOT_DIR="$prefix_dir"
	export PKG_CONFIG_LIBDIR="$PKG_CONFIG_SYSROOT_DIR/lib/pkgconfig"
	unset PKG_CONFIG_PATH
fi

if [ -z "${QYZEL_NDK_ROOT:-}" ]; then
    echo "QYZEL_NDK_ROOT must explicitly select the reviewed Android NDK" >&2
    exit 1
fi
toolchain=$(echo "$QYZEL_NDK_ROOT/toolchains/llvm/prebuilt/"*)
export PATH="$toolchain/bin:$DIR/sdk/android-sdk-linux/ndk/$v_ndk:$DIR/sdk/bin:$PATH"
export ANDROID_HOME="$DIR/sdk/android-sdk-$os"
unset ANDROID_SDK_ROOT ANDROID_NDK_ROOT
