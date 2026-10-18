"""libmpv 2126: seperti 2125, tetapi tanpa RTSP/RTP/UDP di FFmpeg (ADR-0039).

Live view tidak lagi lewat FFmpeg: DashcamLivePlayer membuka RTSP sendiri lalu
memakai MediaCodec (ADR-0006). libmpv hanya memutar rekaman (http/file), jadi
demuxer RTSP — tempat CVE-2026-64834 dan CVE-2026-107696 — dibuang.

Selebihnya sama dengan 2125:

Dasar: sumber FFmpeg 6.1.6 + 7 patch perbaikan dari build 2124
(remote-qa/20261013/media-hardening/<abi>/ffmpeg) dan sumber mpv yang sama.
Bedanya hanya daftar komponen FFmpeg (lihat ENABLE) dan satu patch lokal
(patches/qyzel-mov-skip-pssh.patch, CVE-2026-107678).

Format yang dipakai (diverifikasi dari sampel unit sungguhan):
  - Pro (V85X): rekaman MPEG-TS lewat HTTP (live: decoder native, bukan mpv)
  - Ultra (Allwinner): rekaman MP4/TS H.264 High + AAC LC 16 kHz
  - Berkas lokal hasil unduhan/ekspor (MP4, ekspor memakai Media3, bukan FFmpeg)
"""
from pathlib import Path
import subprocess, shutil, os, json, hashlib, time, sys

root = Path(__file__).resolve().parent
repo = root.parents[2]
old = repo / 'remote-qa/20261013/media-hardening'
qa_old = repo / 'remote-qa/20261013'
base = repo / 'native-media-candidate'
ndk = Path.home() / 'Library/Android/sdk/ndk/28.2.13676358/toolchains/llvm/prebuilt/darwin-x86_64/bin'
host = base / 'host-tools/bin'
local_patches = [root / 'patches/qyzel-mov-skip-pssh.patch']
prev = repo / 'remote-qa/20261016/libmpv-2125'

ENABLE = {
    # h264 perangkat lunak: cadangan kalau MediaCodec menolak rekaman.
    # HEVC hanya lewat MediaCodec (tanpa dekoder hevc perangkat lunak):
    # unit Pro/Ultra merekam H.264; HEVC disiapkan untuk berjaga-jaga saja.
    'decoder': ['h264', 'h264_mediacodec', 'hevc_mediacodec',
                'aac', 'aac_latm', 'pcm_s16le', 'pcm_alaw', 'pcm_mulaw'],
    # 2125 memuat rtsp (+ rtpdec, asf, rm). 2126 tidak.
    'demuxer': ['mpegts', 'mov', 'h264', 'hevc', 'aac'],
    'parser': ['h264', 'hevc', 'aac', 'aac_latm'],
    'protocol': ['file', 'http', 'tcp'],
    # sama dengan 2124; mpv sudah teruji dengan himpunan ini.
    'filter': ['overlay', 'equalizer'],
}

# Harus 0 setelah configure; kalau ada yang 1, build dihentikan.
MUST_BE_OFF = ['RASC_DECODER', 'DASH_DEMUXER', 'HLS_DEMUXER', 'HLS_PROTOCOL',
               'RTMP_PROTOCOL', 'FTP_PROTOCOL', 'HTTPS_PROTOCOL', 'TLS_PROTOCOL',
               'SRT_DEMUXER', 'CRYPTO_PROTOCOL', 'LIBXML2', 'MBEDTLS',
               'LIBDAV1D', 'AV1_DECODER', 'HEVC_DECODER', 'IMF_DEMUXER',
               'CONVOLUTION_FILTER', 'MATROSKA_DEMUXER', 'ASS_DECODER',
               'RTSP_DEMUXER', 'RTSP_MUXER', 'SDP_DEMUXER', 'RTP_DEMUXER',
               'RTPDEC', 'RTP_PROTOCOL', 'UDP_PROTOCOL', 'UDPLITE_PROTOCOL',
               'ASF_DEMUXER', 'RM_DEMUXER']
MUST_BE_ON = ['H264_DECODER', 'H264_MEDIACODEC_DECODER', 'HEVC_MEDIACODEC_DECODER',
              'AAC_DECODER', 'MPEGTS_DEMUXER', 'MOV_DEMUXER',
              'HTTP_PROTOCOL', 'FILE_PROTOCOL', 'TCP_PROTOCOL', 'H264_MP4TOANNEXB_BSF',
              'MEDIACODEC', 'JNI']

ABIS = [
    ('arm64-v8a', 'arm64', ['--cross-prefix=aarch64-linux-android-',
                            '--cc=aarch64-linux-android21-clang',
                            '--arch=aarch64', '--cpu=armv8-a'], ''),
    ('armeabi-v7a', 'armv7', ['--cross-prefix=arm-linux-androideabi-',
                              '--cc=armv7a-linux-androideabi21-clang',
                              '--arch=arm', '--cpu=armv7-a'], ' -mfpu=neon -mcpu=cortex-a8'),
]


def configure_args(prefix, abi_args, extra_cflags):
    args = ['--target-os=android', '--enable-cross-compile', *abi_args,
            '--ar=llvm-ar', '--nm=llvm-nm', '--ranlib=llvm-ranlib',
            '--pkg-config=pkg-config',
            f'--extra-cflags=-I{prefix}/include{extra_cflags}',
            f'--extra-ldflags=-L{prefix}/lib',
            '--disable-gpl', '--disable-nonfree', '--enable-version3',
            '--enable-static', '--disable-shared', '--disable-vulkan',
            '--disable-iconv', '--disable-stripping', '--pkg-config-flags=--static',
            '--disable-everything', '--disable-doc', '--disable-avdevice',
            '--disable-postproc', '--disable-programs', '--disable-gray',
            '--disable-swscale-alpha', '--enable-jni', '--enable-bsfs',
            '--enable-mediacodec', '--disable-dxva2', '--disable-vaapi',
            '--disable-vdpau', '--disable-bzlib', '--disable-linux-perf',
            '--disable-videotoolbox', '--disable-audiotoolbox',
            '--enable-small', '--enable-hwaccels', '--enable-optimizations',
            '--enable-runtime-cpudetect',
            '--enable-avutil', '--enable-avcodec', '--enable-avfilter',
            '--enable-avformat', '--enable-swscale', '--enable-swresample',
            '--enable-network']
    for kind, names in ENABLE.items():
        args.append(f'--enable-{kind}=' + ','.join(names))
    return args


def config_flags(bdir):
    # FFmpeg 6: fitur di config.h, komponen di config_components.h.
    flags = {}
    lines = (bdir / 'config.h').read_text().splitlines() + \
        (bdir / 'config_components.h').read_text().splitlines()
    for line in lines:
        if line.startswith('#define CONFIG_') or line.startswith('#define HAVE_'):
            parts = line.split()
            if len(parts) == 3 and parts[2] in ('0', '1'):
                flags[parts[1].removeprefix('CONFIG_')] = parts[2] == '1'
    return flags


def build(abi, arch, abi_args, extra_cflags):
    work = root / abi
    work.mkdir(exist_ok=True)
    source, prefix = work / 'ffmpeg', work / 'prefix'
    if not source.exists():
        shutil.copytree(old / abi / 'ffmpeg', source, symlinks=True,
                        ignore=shutil.ignore_patterns('_build-*'))
        for p in local_patches:
            subprocess.run(['patch', '--batch', '--forward', '--fuzz=0', '-p1', '-i', str(p)],
                           cwd=source, check=True, stdout=subprocess.DEVNULL)
    if not prefix.exists():
        shutil.copytree(old / abi / 'prefix', prefix, symlinks=True)
        # Buang FFmpeg 2124 supaya mpv pasti melihat hasil build ini.
        for name in ['avcodec', 'avformat', 'avutil', 'avfilter', 'swresample', 'swscale']:
            for f in [prefix / f'lib/lib{name}.a', prefix / f'lib/pkgconfig/lib{name}.pc']:
                f.unlink(missing_ok=True)
            shutil.rmtree(prefix / f'include/lib{name}', ignore_errors=True)

    env = dict(os.environ, PATH=f'{host}:{ndk}:/opt/homebrew/bin:' + os.environ['PATH'])
    env['PKG_CONFIG_LIBDIR'] = str(prefix / 'lib/pkgconfig')
    env['PKG_CONFIG_SYSROOT_DIR'] = str(prefix)
    env.pop('PKG_CONFIG_PATH', None)

    started = time.monotonic()
    bdir = source / ('_build-' + arch)
    bdir.mkdir(exist_ok=True)
    with (work / 'ffmpeg-build.log').open('w') as log:
        args = configure_args(prefix, abi_args, extra_cflags)
        (work / 'ffmpeg-configure-args.json').write_text(json.dumps(args, indent=1) + '\n')
        subprocess.run([str(source / 'configure'), *args], cwd=bdir, env=env,
                       stdout=log, stderr=subprocess.STDOUT, check=True)
        flags = config_flags(bdir)
        bad = [k for k in MUST_BE_OFF if flags.get(k)] + [k for k in MUST_BE_ON if not flags.get(k)]
        assert not bad, f'{abi}: komponen salah: {bad}'
        enabled = sorted(k for k, v in flags.items()
                         if v and k.endswith(('_DECODER', '_DEMUXER', '_PARSER', '_PROTOCOL', '_FILTER', '_BSF')))
        (work / 'ffmpeg-enabled-components.json').write_text(json.dumps(enabled, indent=1) + '\n')
        subprocess.run(['make', '-j4'], cwd=bdir, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        subprocess.run(['make', 'install', f'DESTDIR={prefix}'], cwd=bdir, env=env,
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    for p in bdir.rglob('*'):
        if p.is_file() and p.suffix in ['.o', '.d']:
            p.unlink()

    cross = base / 'clean-build' / abi / f'clean-{arch}.cross'
    mpv = work / 'mpv-build'
    args = [str(host / 'meson'), 'setup', str(mpv), str(qa_old / 'native-fix/mpv'),
            '--cross-file', str(cross), '--prefix=/', '--libdir=lib', '--prefer-static',
            '--default-library=shared', '-Dgpl=false', '-Db_lundef=true',
            "-Dc_link_args=['-Wl,-z,max-page-size=16384','-Wl,--exclude-libs,ALL','-lc++_static','-lc++abi','-lunwind']",
            '-Dlibmpv=true', '-Dbuild-date=false', '-Dlua=disabled', '-Dcplayer=false',
            '-Diconv=disabled', '-Dvulkan=disabled', '-Dmanpage-build=disabled']
    with (work / 'mpv-build.log').open('w') as log:
        if not (mpv / 'build.ninja').exists():
            subprocess.run(args, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        subprocess.run([str(host / 'ninja'), '-C', str(mpv), '-j4'], env=env,
                       stdout=log, stderr=subprocess.STDOUT, check=True)

    def run(tool, *a):
        return subprocess.check_output([str(ndk / tool), *map(str, a)], text=True)

    # Cek simbol sebelum strip: komponen yang dibuang benar-benar tidak ikut.
    allsyms = run('llvm-nm', mpv / 'libmpv.so')
    forbidden = ['ff_rasc_decoder', 'ff_dash_demuxer', 'ff_hls_demuxer', 'ff_hls_protocol',
                 'ff_rtmp_protocol', 'ff_ftp_protocol', 'ff_tls_protocol', 'ff_https_protocol',
                 'ff_hevc_decoder', 'ff_av1_decoder', 'ff_libdav1d_decoder', 'xmlReadMemory',
                 'mbedtls_ssl_setup', 'ff_rtsp_demuxer', 'ff_sdp_demuxer',
                 'ff_rtp_demuxer', 'ff_rtp_protocol', 'ff_udp_protocol',
                 'ff_rtsp_open_transport_ctx', 'ff_rdt_parse_packet',
                 'ff_asf_demuxer', 'ff_rm_demuxer']
    required = ['ff_h264_decoder', 'ff_mov_demuxer', 'ff_mpegts_demuxer', 'ff_aac_decoder']
    present = [s for s in forbidden if f' {s}\n' in allsyms + '\n']
    missing = [s for s in required if f' {s}\n' not in allsyms + '\n']

    dest = root / 'binaries' / abi / 'libmpv.so'
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(mpv / 'libmpv.so', dest)
    subprocess.run([str(ndk / 'llvm-strip'), '--strip-all', str(dest)], check=True)
    syms = run('llvm-nm', '-D', dest)
    oldsyms = run('llvm-nm', '-D', old / 'binaries' / abi / 'libmpv.so')

    def exports(s):
        return {x.split()[-1] for x in s.splitlines() if ' T mpv_' in x}

    loads = [int(x.split()[-1], 16) for x in run('llvm-readelf', '-lW', dest).splitlines()
             if x.strip().startswith('LOAD')]
    needed = [x.split('[')[-1].rstrip(']') for x in run('llvm-readelf', '-dW', dest).splitlines()
              if '(NEEDED)' in x]
    checks = {
        'exportsPreserved': not (exports(oldsyms) - exports(syms)),
        'exportsSameAs2125': exports(syms) == exports(run('llvm-nm', '-D', prev / 'binaries' / abi / 'libmpv.so')),
        'JNI': 'mpv_lavc_set_java_vm' in exports(syms),
        'ELF16KB': bool(loads) and min(loads) >= 16384,
        'noUndefinedNDKCpp': not any(' U _ZNSt6__ndk1' in x for x in syms.splitlines()),
        'removedComponentsAbsent': not present,
        'requiredComponentsPresent': not missing,
    }
    assert all(checks.values()), (checks, present, missing)
    return {
        'abi': abi, 'sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
        'bytes': dest.stat().st_size,
        'bytes2124': (old / 'binaries' / abi / 'libmpv.so').stat().st_size,
        'bytes2125': (prev / 'binaries' / abi / 'libmpv.so').stat().st_size,
        'needed': needed, 'checks': checks,
        'seconds': round(time.monotonic() - started),
        'status': 'not-runtime-tested-not-release-approved',
    }


if __name__ == '__main__':
    patch_info = [{'file': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                  for p in local_patches]
    (root / 'patches.json').write_text(json.dumps(patch_info, indent=2) + '\n')
    wanted = sys.argv[1:] or [a[0] for a in ABIS]
    results = []
    for abi, arch, abi_args, cflags in ABIS:
        if abi not in wanted:
            continue
        results.append(build(abi, arch, abi_args, cflags))
        (root / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
        print(json.dumps(results[-1]), flush=True)
