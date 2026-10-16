"""Build isolated Android dependencies from verified archives, never recovered .a files."""
from pathlib import Path
import os,json,hashlib,tarfile,shutil,subprocess,time,sys
r=Path(__file__).resolve().parent;abi=sys.argv[1] if len(sys.argv)>1 else 'arm64-v8a'
arch,triple,compiler = {
 'arm64-v8a':('arm64','aarch64-linux-android','aarch64-linux-android21-clang'),
 'armeabi-v7a':('armv7','arm-linux-androideabi','armv7a-linux-androideabi21-clang'),
 'x86_64':('x64','x86_64-linux-android','x86_64-linux-android21-clang'),
}[abi]
if abi != 'arm64-v8a':
 assert json.loads((r/'clean-build/arm64-v8a/oppo-software-probe.json').read_text())['passed']
root=r/'clean-build'/abi;prefix=root/'prefix';deps=root/'deps'
if shutil.disk_usage(r).free<5*2**30:raise SystemExit('Need 5GiB free for isolated build')
root.mkdir(parents=True,exist_ok=True);prefix.mkdir(exist_ok=True);deps.mkdir(exist_ok=True)
if any(prefix.glob('lib/*.a')):raise SystemExit('Prefix already contains libraries; inspect report before resuming')
for x in ['include','scripts']:shutil.copytree(r/'recovered-recipe'/x,root/x,dirs_exist_ok=True)
p=root/'include/path.sh';p.write_text(p.read_text().replace('export SED=gsed','export SED=sed'))
for a in ['usr','local']:
 if not (prefix/a).exists():(prefix/a).symlink_to('.')
(prefix/'crossfile.txt').write_text((r/'probe-prefix'/abi/'crossfile.txt').read_text())
rows={x['name']:x for x in json.loads((r/'sources-lock.json').read_text())['sources']};order=['mbedtls','dav1d','freetype','fribidi','harfbuzz','libass','libxml2','ffmpeg']
for name in order:
 row=rows[name];archive=r/'source-materials/archives'/row['archive'];assert hashlib.sha256(archive.read_bytes()).hexdigest()==row['sha256']
 dest=deps/name
 if dest.exists():raise SystemExit('Source already exists: '+name)
 stage=root/('unpack-'+name);stage.mkdir()
 with tarfile.open(archive) as tar:tar.extractall(stage,filter='data')
 entries=list(stage.iterdir());assert len(entries)==1 and entries[0].is_dir();entries[0].rename(dest);stage.rmdir()
 # Scripts refer to source-relative ../../include and scripts paths.
 shutil.copy2(root/'scripts'/(name+'.sh'),dest/'qyzel-build.sh');(dest/'qyzel-build.sh').chmod(0o755)
for patch in sorted((r/'recovered-recipe/patches/ffmpeg').glob('*.patch')):
 if patch.name=='hls_mp4_seek.patch':
  assert 'ff_read_frame_flush(pls->ctx);\n\n        /* Reset the init segment' in (deps/'ffmpeg/libavformat/hls.c').read_text();continue
 subprocess.run(['patch','--batch','--dry-run','-p1','-i',str(patch)],cwd=deps/'ffmpeg',check=True,stdout=subprocess.DEVNULL)
 subprocess.run(['patch','--batch','-p1','-i',str(patch)],cwd=deps/'ffmpeg',check=True,stdout=subprocess.DEVNULL)
env=os.environ.copy();ndk=Path.home()/'Library/Android/sdk/ndk/28.2.13676358';bin=ndk/'toolchains/llvm/prebuilt/darwin-x86_64/bin'
env.update(PATH=str(r/'host-tools/bin')+':'+str(bin)+':/opt/homebrew/bin:'+env['PATH'],QYZEL_NDK_ROOT=str(ndk),cores='2',ndk_triple=triple,ndk_suffix='-'+arch,prefix_dir=str(prefix),native_dir=str(prefix/'jni'),CC=compiler,CXX=compiler+'++',AR='llvm-ar',RANLIB='llvm-ranlib',STRIP='llvm-strip',LC_ALL='C',SOURCE_DATE_EPOCH='1781913600')
(prefix/'jni').mkdir(exist_ok=True);stages=[]
for name in order:
 start=time.monotonic();log=root/(name+'.log')
 with log.open('w') as f:result=subprocess.run(['bash','-e','./qyzel-build.sh','build'],cwd=deps/name,env=env,stdout=f,stderr=subprocess.STDOUT)
 stages.append({'name':name,'exit':result.returncode,'seconds':round(time.monotonic()-start,1),'sourceSHA256':rows[name]['sha256']})
 (root/'result.json').write_text(json.dumps({'abi':abi,'recoveredLibrariesUsed':False,'productionUnchanged':True,'approved':False,'stages':stages},indent=2)+'\n');print(json.dumps(stages[-1]),flush=True)
 if result.returncode:print(log.read_text()[-2200:]);raise SystemExit(result.returncode)
print('Clean dependencies built; integration and comparison still required.')
