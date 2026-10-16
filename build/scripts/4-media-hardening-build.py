from pathlib import Path
import subprocess,shutil,os,json,hashlib,urllib.request,time
qa=Path('$WORK/remote-qa/20261013')
base=qa.parents[1]/'native-media-candidate'
root=qa/'media-hardening';root.mkdir(exist_ok=True)
ndk=Path.home()/'Library/Android/sdk/ndk/28.2.13676358/toolchains/llvm/prebuilt/darwin-x86_64/bin'
host=base/'host-tools/bin'
selected=json.loads((qa/'upstream-fixes/selected-summary.json').read_text())
fixes=[x for x in selected if x['project']=='ffmpeg']
pdir=root/'patches';pdir.mkdir(exist_ok=True)
for x in fixes:
 p=pdir/(x['sha']+'.patch')
 if not p.exists():
  url=f"https://github.com/FFmpeg/FFmpeg/commit/{x['sha']}.patch"
  p.write_bytes(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'QYZEL-release-audit'}),timeout=30).read())
(root/'patches.json').write_text(json.dumps([{'sha':x['sha'],'title':x['message'].splitlines()[0],'patchSHA256':hashlib.sha256((pdir/(x['sha']+'.patch')).read_bytes()).hexdigest()} for x in fixes],indent=2)+'\n')
results=[]
for abi,arch in [('arm64-v8a','arm64'),('armeabi-v7a','armv7'),('x86_64','x64')]:
 work=root/abi;work.mkdir(exist_ok=True)
 source=work/'ffmpeg';prefix=work/'prefix'
 oldbase=base/'clean-build'/abi
 if not source.exists():
  shutil.copytree(oldbase/'deps/ffmpeg',source,symlinks=True)
  for x in fixes:
   p=pdir/(x['sha']+'.patch')
   subprocess.run(['patch','--batch','--forward','--fuzz=0','-p1','-i',str(p)],cwd=source,check=True,stdout=subprocess.DEVNULL)
 if not prefix.exists():shutil.copytree(oldbase/'prefix',prefix,symlinks=True)
 build=source/('_build-'+arch)
 oldsource=oldbase/'deps/ffmpeg'
 for p in [build/'Makefile',build/'ffbuild/config.mak']:
  p.write_text(p.read_text().replace(str(oldsource),str(source)))
 link=build/'src'
 if link.is_symlink():link.unlink()
 link.symlink_to(source,target_is_directory=True)
 env=dict(os.environ,PATH=f'{host}:{ndk}:/opt/homebrew/bin:'+os.environ['PATH'])
 env['PKG_CONFIG_LIBDIR']=str(prefix/'lib/pkgconfig');env['PKG_CONFIG_SYSROOT_DIR']=str(prefix);env.pop('PKG_CONFIG_PATH',None)
 started=time.monotonic()
 with (work/'ffmpeg-build.log').open('w') as log:
  subprocess.run(['make','-j2'],cwd=build,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 for name in ['avcodec','avformat','avutil','avfilter','swresample','swscale']:
  a=build/f'lib{name}/lib{name}.a';assert a.is_file();shutil.copy2(a,prefix/f'lib/lib{name}.a')
 # Object files are reproducible; retain linked archives/config/source and logs.
 for p in build.rglob('*'):
  if p.is_file() and p.suffix in ['.o','.d']:p.unlink()
 cross=oldbase/f'clean-{arch}.cross'
 mpv=work/'mpv-build'
 args=[str(host/'meson'),'setup',str(mpv),str(qa/'native-fix/mpv'),'--cross-file',str(cross),'--prefix=/','--libdir=lib','--prefer-static','--default-library=shared','-Dgpl=false','-Db_lundef=true',"-Dc_link_args=['-Wl,-z,max-page-size=16384','-Wl,--exclude-libs,ALL','-lc++_static','-lc++abi','-lunwind']",'-Dlibmpv=true','-Dbuild-date=false','-Dlua=disabled','-Dcplayer=false','-Diconv=disabled','-Dvulkan=disabled','-Dmanpage-build=disabled']
 with (work/'mpv-build.log').open('w') as log:
  if not (mpv/'build.ninja').exists():subprocess.run(args,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
  subprocess.run([str(host/'ninja'),'-C',str(mpv),'-j2'],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 dest=root/'binaries'/abi/'libmpv.so';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(mpv/'libmpv.so',dest)
 subprocess.run([str(ndk/'llvm-strip'),'--strip-all',str(dest)],check=True)
 def run(tool,*args):return subprocess.check_output([str(ndk/tool),*map(str,args)],text=True)
 syms=run('llvm-nm','-D',dest);oldsyms=run('llvm-nm','-D',qa/'native-fix/binaries'/abi/'libmpv.so')
 def exports(s):return {x.split()[-1] for x in s.splitlines() if ' T mpv_' in x}
 loads=[int(x.split()[-1],16) for x in run('llvm-readelf','-lW',dest).splitlines() if x.strip().startswith('LOAD')]
 checks={'exportsPreserved':not(exports(oldsyms)-exports(syms)),'JNI':'mpv_lavc_set_java_vm' in exports(syms),'ELF16KB':bool(loads) and min(loads)>=16384,'noUndefinedNDKCpp':not any(' U _ZNSt6__ndk1' in x for x in syms.splitlines())}
 assert all(checks.values()),checks
 result={'abi':abi,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'bytes':dest.stat().st_size,'checks':checks,'seconds':round(time.monotonic()-started),'status':'not-runtime-tested-not-release-approved'}
 results.append(result);(root/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(result),flush=True)
