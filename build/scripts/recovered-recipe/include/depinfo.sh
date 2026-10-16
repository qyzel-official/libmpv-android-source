#!/bin/bash -e

## Dependency versions

v_sdk=9123335_latest
v_ndk=28.2.13676358
v_sdk_build_tools=33.0.2

v_libass=0.17.5
v_harfbuzz=14.5.1
v_fribidi=1.0.17
v_freetype=2-14-3
v_mbedtls=3.6.7
v_dav1d=1.5.3
v_libxml2=2.15.4
v_ffmpeg=6.1.6
v_mpv=78d43740f52db817d98bcf24fb30a76ab6fa13ff
v_libogg=1.3.5
v_libvorbis=1.3.7
v_libvpx=1.13


## Dependency tree
# I would've used a dict but putting arrays in a dict is not a thing

dep_mbedtls=()
dep_dav1d=()
dep_libvorbis=(libogg)
if [ -n "${ENCODERS_GPL+x}" ]; then
	dep_ffmpeg=(mbedtls dav1d libxml2 libvorbis libvpx libx264)
else
	dep_ffmpeg=(mbedtls dav1d libxml2)
fi
dep_freetype2=()
dep_fribidi=()
dep_harfbuzz=()
dep_libass=(freetype fribidi harfbuzz)
dep_lua=()
dep_shaderc=()
if [ -n "${ENCODERS_GPL+x}" ]; then
	dep_mpv=(ffmpeg libass fftools_ffi)
else
	dep_mpv=(ffmpeg libass)
fi
