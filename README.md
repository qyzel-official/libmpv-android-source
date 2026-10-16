# libmpv for QYZEL Drive (Android) — corresponding source

This package is the corresponding source for the `libmpv.so` media library
bundled in **QYZEL Drive for Android, libmpv build 2124**. It is provided so
that users and developers can study, modify and rebuild the library and
replace it in the app, as permitted by the GNU Lesser General Public License.

`libmpv.so` is a separate shared library. It is stored in the APK under
`lib/<abi>/libmpv.so` and loaded at run time. The rest of the app is not
needed to rebuild or replace it.

Source requests and questions: **developer@qyzel.com**

## Shipped binaries covered

Only these two ABIs are shipped. SHA-256 of the files as stored in the APK:

| ABI | File | SHA-256 | Size (bytes) |
|---|---|---|---|
| arm64-v8a | `libmpv.so` | `9fb6c988d8f1097117b2abd4294a3577fb40721c952f337ca1d136bc73e57045` | 13914120 |
| arm64-v8a | `libmediakitandroidhelper.so` | `ab55b1d34665dba8fa7a451e82c466ee71b9698e7da6c9a3cb68a7c0ee7610d4` | |
| armeabi-v7a | `libmpv.so` | `7c86f239b35c53d04d82239b408eae438ca18581b8222432b515cf65fc939ec3` | 12943404 |
| armeabi-v7a | `libmediakitandroidhelper.so` | `506d0bc7775fe9888be6b6e889d8556ca0574dba65813866e2158cbf52a8c8b1` | |

`libmediakitandroidhelper.so` is an unmodified upstream prebuilt from the
media_kit project (MIT license); see "Known limitations".

## Layout

```
README.md            this file
SHA256SUMS           checksums of every file in this package
sources/             upstream source archives (byte-identical to the build inputs)
patches/ffmpeg/      patches applied to FFmpeg (+ patches.json with upstream commit IDs)
patches/mpv/         patches applied to mpv
build/scripts/       the build scripts that were used (paths replaced by placeholders)
build/cross/<abi>/   Meson cross files
build/config/<abi>/  effective FFmpeg configuration, mpv/libplacebo Meson options,
                     mpv build log, and the final libmpv.so link command
licenses/            license and notice files of all components
```

## Components

All components are statically linked into `libmpv.so`.

| Component | Version | License | Upstream | Archive in `sources/` | SHA-256 |
|---|---|---|---|---|---|
| mpv | 0.41.0, commit `41f6a645068483470267271e1d09966ca3b9f413` | LGPL-2.1-or-later (built with `-Dgpl=false`) | https://github.com/mpv-player/mpv | `mpv-maintained.tar.gz` | `068960e89211f2adc80af03f637fa393fb5e407d3dd23592c8fe8c5490bb7ae4` |
| FFmpeg | 6.1.6 | LGPL-3.0-or-later (configured `--disable-gpl --disable-nonfree --enable-version3`) | https://ffmpeg.org/ | `ffmpeg-6.1.6.tar.xz` | `d4fcb164028dd3beee5d92c0ac72e46aac6973c75ea12dc14de07bf8f407370a` |
| libplacebo | 7.360.1 (tag `v7.360.1`, commit `cee9b076f2c63104ccfd497fa79c39a867293ec4`) | LGPL-2.1-or-later | https://code.videolan.org/videolan/libplacebo | `libplacebo-7.360.1.tar.gz` | `d05fdf90bea2f629eaa2d115e909fd356388ac639e54f77b87a018a6d76224bd` |
| libplacebo submodules: glad `73db193f`, fast_float `97b54ca9`, jinja `15206881`, markupsafe `297fc8e3` | as pinned by libplacebo 7.360.1 | glad: MIT (generator) + Apache-2.0 (Khronos specifications); fast_float: Apache-2.0 / MIT / BSL-1.0; jinja, markupsafe: BSD-3-Clause (build-time code generators) | see `.gitmodules` in libplacebo | `libplacebo-3rdparty-submodules.tar.gz` | `750670b8fa1bb7258ee3b982ef784cb611f89d4ecde6fb5af44a7a7ca81c5f7f` |
| libass | 0.17.5 | ISC | https://github.com/libass/libass | `libass-0.17.5.tar.xz` | `2dca25c0e0c837ddf00b52011b3f82cac1e4ddd3ad018227806b0c2288864acc` |
| HarfBuzz | 14.5.1 | MIT ("Old MIT") | https://github.com/harfbuzz/harfbuzz | `harfbuzz-14.5.1.tar.xz` | `7e2fa4e8c7c98e8d8140671f5772542afaaa6acccfbd746506886b6d85f7f8d6` |
| FreeType | 2.14.3 | FreeType License (FTL) | https://freetype.org/ | `freetype-2.14.3.tar.xz` | `36bc4f1cc413335368ee656c42afca65c5a3987e8768cc28cf11ba775e785a5f` |
| GNU FriBidi | 1.0.17 | LGPL-2.1-or-later | https://github.com/fribidi/fribidi | `fribidi-1.0.17.tar.xz` | `6949dcde27d41cebad1fd741fcafc36d55a1020d2d872d4a6eb3914caabbada2` |
| Mbed TLS | 3.6.7 | Apache-2.0 (dual Apache-2.0 / GPL-2.0-or-later; used under Apache-2.0) | https://github.com/Mbed-TLS/mbedtls | `mbedtls-3.6.7.tar.bz2` | `a7e8bcbec0e6f761b4af24f25677626b35f762f68eef79c08677a363212d11f6` |
| libxml2 | 2.15.4 | MIT | https://gitlab.gnome.org/GNOME/libxml2 | `libxml2-2.15.4.tar.xz` | `98087fd181d9070724f3fbc65c7377db03038eb92bd882374daff44940138821` |
| dav1d | 1.5.3 | BSD-2-Clause | https://code.videolan.org/videolan/dav1d | `dav1d-1.5.3.tar.xz` | `732010aa5ef461fa93355ed2c6c5fedb48ddc4b74e697eaabe8907eaeb943011` |
| Android NDK runtime: libc++ (static), libc++abi, libunwind, libatomic, zlib (`libz.a` from the NDK sysroot) | NDK r28c | Apache-2.0 WITH LLVM-exception; zlib license | https://developer.android.com/ndk | (part of the NDK) | — |
| media_kit Android helper (`libmediakitandroidhelper.so`) | commit `42054e5d479f39ccbb0ae604862e2bcaf59b74c2` | MIT | https://github.com/media-kit/media-kit-android-helper | `media-kit-android-helper-42054e5.tar.gz` | `53ea71476d1cbc9a5d63d4898c6b027af4ccb6525800c7b42e267e6128652423` |

Notes:

- `mpv-maintained.tar.gz` contains the upstream mpv tree at commit
  `41f6a645068483470267271e1d09966ca3b9f413` (top-level directory
  `mpv-41f6a645068483470267271e1d09966ca3b9f413/`, `MPV_VERSION` = 0.41.0),
  as served by `https://codeload.github.com/mpv-player/mpv/tar.gz/41f6a645068483470267271e1d09966ca3b9f413`.
- `libplacebo-7.360.1.tar.gz` does not contain git submodules.
  `libplacebo-3rdparty-submodules.tar.gz` contains the exact submodule
  checkouts used (without `.git` metadata) under the same top-level directory
  `libplacebo-7.360.1/`, so it can be extracted on top of the main archive.
  The `Vulkan-Headers` and `demos/3rdparty/nuklear` submodules were not used
  (Vulkan and demos are disabled).
- FFmpeg is configured with `--enable-version3` (needed for Mbed TLS), so
  FFmpeg — and therefore `libmpv.so` as a whole — is covered by the GNU LGPL
  version 3 or later.
- The FFmpeg release tarball's OpenPGP signature (key fingerprint
  `FCF986EA15E6E293A5644F10B4322F04D67658D8`) was checked when it was
  downloaded; the `.asc` file itself is not included. It is published at
  `https://ffmpeg.org/releases/ffmpeg-6.1.6.tar.xz.asc`.

## Patches

### FFmpeg (`patches/ffmpeg/`)

Applied with `patch -p1` to the extracted `ffmpeg-6.1.6` tree, in this order:

| File | Origin | Purpose |
|---|---|---|
| `dash_base_url_escape.patch` | media-kit build recipe | DASH demuxer: XML-escape the resolved BaseURL before writing it back into the manifest node |
| `5cff5a3a5ad09bd77a43e2d5149b1f01a7feb4ce.patch` | FFmpeg `release/6.1` | oggparsevorbis: prevent integer overflow when summing header lengths |
| `8139862d3d034c100cb7fda576aed05c1cfc91db.patch` | FFmpeg `release/6.1` | get_buffer: use the frame pixel format instead of the context's |
| `c13d2d1152ad5e4461edfab445e043f244ce379d.patch` | FFmpeg `release/6.1` | h264_direct: move check before loading data |
| `c277e33a18c0d7f7812b00aced15a56a1b263d28.patch` | FFmpeg `release/6.1` | h264_direct: await both fields of a colocated field pair |
| `facf02226a11d240e8959b97dd837bde6f3f34ee.patch` | FFmpeg `release/6.1` | h264_slice: clear the ER picture when starting a second field |
| `a4f6f7588ed5f68ded49136b321a5ceb72671a63.patch` | FFmpeg `release/6.1` | h264_direct: do not read the other field's rows of colocated mb_type |
| `8452c937149e8d9c9a36ba2e259e10cb715de410.patch` | FFmpeg `release/6.1` | mov demuxer: don't leak on realloc failure |

The seven `release/6.1` patches are the upstream commits with the IDs in
their file names (`https://github.com/FFmpeg/FFmpeg/commit/<id>.patch`);
`patches.json` lists them with titles and SHA-256 in application order.
They were applied with `--forward --fuzz=0`.

### mpv (`patches/mpv/`)

Applied with `patch -p1` to the extracted mpv tree, in this order:

| File | Purpose |
|---|---|
| `mpv_lavc_set_java_vm-maintained.patch` | Adds the exported function `mpv_lavc_set_java_vm()`, which calls FFmpeg's `av_jni_set_java_vm()`. Needed because that symbol is hidden when FFmpeg is linked statically; the Android app calls it so FFmpeg can use MediaCodec. From the media-kit build recipe, rebased onto mpv 0.41.0. |
| `mpv-autoload-upstream.patch` | Upstream mpv commit `6bdacac99153b5a487d108e11d2f8d7678afd2fd` ("player/loadfile: fix stack-overflow on EDL metadata track", GHSA-qpf4-42gw-f286). |

libplacebo, libass, HarfBuzz, FreeType, FriBidi, Mbed TLS, libxml2 and dav1d
are built unmodified.

## Toolchain

- Android NDK r28c (`28.2.13676358`), clang 19.0.1 (Android 13624864,
  based on r530567e), target API level 21; `llvm-ar`, `llvm-ranlib`,
  `llvm-strip` from the NDK.
- Meson 1.9.1, Ninja 1.13.0, NASM 2.16.03, Python 3.13.5, pkg-config 0.29.2,
  GNU make, `patch`. Build host: macOS on Apple silicon.
- Environment: `PKG_CONFIG_LIBDIR=<prefix>/lib/pkgconfig`,
  `PKG_CONFIG_SYSROOT_DIR=<prefix>`, `PKG_CONFIG_PATH` unset for all steps;
  additionally `LC_ALL=C` and `SOURCE_DATE_EPOCH=1781913600` for the
  dependency builds (step 1).

| ABI | Compiler | Cross file |
|---|---|---|
| arm64-v8a | `aarch64-linux-android21-clang` | `build/cross/arm64-v8a/clean-arm64.cross` |
| armeabi-v7a | `armv7a-linux-androideabi21-clang` | `build/cross/armeabi-v7a/clean-armv7.cross` |

`crossfile.txt` (same directory) is the cross file used by the dependency
scripts; `clean-<arch>.cross` adds `-fPIC` and a 16 KB maximum page size and
is used for libplacebo and mpv.

## Build order and how to rebuild

Repeat for each ABI. `<prefix>` is an empty install prefix (create symlinks
`<prefix>/usr -> .` and `<prefix>/local -> .`, and copy
`build/cross/<abi>/crossfile.txt` to `<prefix>/crossfile.txt`).

1. **Static dependencies** — in this order: mbedtls, dav1d, freetype, fribidi,
   harfbuzz, libass, libxml2, ffmpeg. For each: extract the archive to
   `<root>/deps/<name>/`, copy `build/scripts/recovered-recipe/include` and
   `.../scripts` to `<root>/include` and `<root>/scripts`, then run
   `bash -e ../../scripts/<name>.sh build` inside the source directory with:
   `QYZEL_NDK_ROOT=<ndk>`, `ndk_triple` (`aarch64-linux-android` /
   `arm-linux-androideabi`), `ndk_suffix=-arm64` / `-armv7`,
   `prefix_dir=<prefix>`, `native_dir=<prefix>/jni`, `CC`/`CXX` as in the
   table above (`CXX` = `CC` + `++`), `AR=llvm-ar`, `RANLIB=llvm-ranlib`,
   `STRIP=llvm-strip`, and the NDK `bin` directory on `PATH`. On macOS,
   `include/path.sh` expects GNU sed as `gsed`; the original run replaced it
   with `sed`.
   Before building FFmpeg, apply the eight FFmpeg patches (see above).
   `build/config/<abi>/ffmpeg-config.h` (`FFMPEG_CONFIGURATION`) and
   `ffmpeg-config.mak` show the exact resulting configuration.
2. **libplacebo** — extract `libplacebo-7.360.1.tar.gz`, then extract
   `libplacebo-3rdparty-submodules.tar.gz` over it, and run:
   ```
   meson setup build <src> --cross-file clean-<arch>.cross --prefix=/ --libdir=lib \
     --default-library=static -Ddemos=false -Dtests=false -Dvulkan=disabled \
     -Dshaderc=disabled -Dglslang=disabled -Dopengl=enabled -Dlcms=disabled -Dlibdovi=disabled
   ninja -C build && DESTDIR=<prefix> ninja -C build install
   ```
3. **mpv / libmpv.so** — extract `mpv-maintained.tar.gz`, apply both mpv
   patches, and run:
   ```
   meson setup build <src> --cross-file clean-<arch>.cross --prefix=/ --libdir=lib \
     --prefer-static --default-library=shared -Dgpl=false -Db_lundef=true \
     "-Dc_link_args=['-Wl,-z,max-page-size=16384','-Wl,--exclude-libs,ALL','-lc++_static','-lc++abi','-lunwind']" \
     -Dlibmpv=true -Dbuild-date=false -Dlua=disabled -Dcplayer=false \
     -Diconv=disabled -Dvulkan=disabled -Dmanpage-build=disabled
   ninja -C build
   llvm-strip --strip-all build/libmpv.so
   ```
   `build/config/<abi>/mpv-intro-buildoptions.json`, `mpv-build.log` and
   `libmpv-link-command.txt` record the resolved options, enabled features and
   the exact link line.

The scripts in `build/scripts/` are the ones that produced the shipped
binaries, numbered in the order they ran:

1. `1-clean_dependencies.py <abi>` — step 1 (verifies archive hashes, applies
   `dash_base_url_escape.patch`, builds the eight dependencies).
2. `2-link_clean_dependencies.py <abi>` — step 2 (libplacebo), followed by an
   intermediate mpv build.
3. `3-build_candidate.py` — applies `mpv-autoload-upstream.patch` to the
   (already JNI-patched) mpv tree; intermediate mpv build.
4. `4-media-hardening-build.py` — applies the seven FFmpeg `release/6.1`
   patches to the configured FFmpeg tree, re-runs `make` (no reconfigure),
   updates the FFmpeg static libraries in the prefix, builds the final
   `libmpv.so` with the options above and strips it.

Machine-specific paths in these files are replaced by placeholders: `$WORK`
(build workspace root), `$ANDROID_SDK`, `$HOME`, and `$OLDWORK` (an earlier
workspace path, only used as a search string). The scripts expect that
workspace layout and are a record of the build, not a portable installer;
the manual steps above are the portable equivalent.

## Replacing libmpv.so in the app

1. Build `libmpv.so` for the ABI of your device (see above). Your library
   must export the libmpv client API (`mpv_*`) and `mpv_lavc_set_java_vm`,
   and should keep the 16 KB ELF page alignment.
2. Take the APK(s) of the installed app (for a Play install, use
   `adb shell pm path <package>` and `adb pull` the base and split APKs; the
   native libraries are in the `split_config.<abi>.apk` split).
3. Replace `lib/<abi>/libmpv.so` in the APK, remove the old signature
   (`META-INF/`), run `zipalign -P 16 -f 4` and sign every APK of the set with
   your own key (`apksigner`).
4. Uninstall the original app (back up any recordings you want to keep
   first) and install your set with `adb install-multiple`. An APK signed with
   a different key cannot update the store-installed app, and online services
   that check the app signature may not work with a re-signed build;
   video playback does not depend on them.

## Known limitations

- **Bit-for-bit reproduction has not yet been verified.** The sources,
  patches, options and toolchain versions here are the ones used, but an
  independent rebuild producing byte-identical libraries has not been
  demonstrated.
- **The build scripts are derived from the media-kit
  `libmpv-android-video-build` v1.1.7 recipes, with local adjustments**
  (updated dependency versions, explicit NDK selection, and building mpv
  directly with Meson including libplacebo). `recovered-recipe/scripts/mpv.sh`
  is included for reference only; it was not used for the final build.
  The recipe's `hls_mp4_seek.patch` is not included because that change is
  already part of FFmpeg 6.1.6 (the build script checks for it and skips it).
- **`libmediakitandroidhelper.so` is an unmodified upstream prebuilt (MIT)**
  taken from the media_kit project. The matching upstream source
  (commit `42054e5d479f39ccbb0ae604862e2bcaf59b74c2`, the revision pinned by
  `libmpv-android-video-build` v1.1.7) is included as a reference; it has not
  been proven to reproduce the shipped binary. It is not covered by the LGPL.
- `4-media-hardening-build.py` reads its patch list from a file that is not
  included; the same list is `patches/ffmpeg/patches.json`. It downloads the
  patch files only if they are missing; they are all included here.
- Mbed TLS is built from the unmodified 3.6.7 release.
