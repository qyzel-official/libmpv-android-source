from pathlib import Path
import hashlib,json,os,subprocess,shutil
r=Path(__file__).resolve().parent
base=r.parents[2]/'native-media-candidate'
# r is remote-qa/date/native-fix; workspace is parents[2].
assert (base/'clean-build').is_dir(), base
ndk=Path.home()/'Library/Android/sdk/ndk/28.2.13676358/toolchains/llvm/prebuilt/darwin-x86_64/bin'
host=base/'host-tools/bin'
source=r/'mpv'; patch=r/'mpv-autoload-upstream.patch'
if 'int sc[STREAM_TYPE_COUNT + 1]' not in (source/'player/loadfile.c').read_text():
 subprocess.run(['patch','--batch','-p1','-i',str(patch)],cwd=source,check=True)
results=[]
for abi,arch in [('arm64-v8a','arm64'),('armeabi-v7a','armv7'),('x86_64','x64')]:
 prefix=base/'clean-build'/abi/'prefix'
 env=dict(os.environ,PATH=f'{host}:{ndk}:/opt/homebrew/bin:'+os.environ['PATH'],PKG_CONFIG_LIBDIR=str(prefix/'lib/pkgconfig'),PKG_CONFIG_SYSROOT_DIR=str(prefix))
 env.pop('PKG_CONFIG_PATH',None)
 build=r/abi
 args=[str(host/'meson'),'setup',str(build),str(source),'--cross-file',str(base/'clean-build'/abi/f'clean-{arch}.cross'),'--prefix=/','--libdir=lib','--prefer-static','--default-library=shared','-Dgpl=false','-Db_lundef=true',"-Dc_link_args=['-Wl,-z,max-page-size=16384','-Wl,--exclude-libs,ALL','-lc++_static','-lc++abi','-lunwind']",'-Dlibmpv=true','-Dbuild-date=false','-Dlua=disabled','-Dcplayer=false','-Diconv=disabled','-Dvulkan=disabled','-Dmanpage-build=disabled']
 with (r/f'{abi}-build.log').open('w') as log:
  if not (build/'build.ninja').exists():subprocess.run(args,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
  subprocess.run([str(host/'ninja'),'-C',str(build),'-j2'],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 dest=r/'binaries'/abi/'libmpv.so';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(build/'libmpv.so',dest)
 subprocess.run([str(ndk/'llvm-strip'),'--strip-all',str(dest)],check=True)
 def run(tool,*args):return subprocess.check_output([str(ndk/tool),*map(str,args)],text=True)
 symbols=run('llvm-nm','-D',dest); old=run('llvm-nm','-D',base/'clean-build'/abi/'probe/libmpv.so')
 def exports(s):return {x.split()[-1] for x in s.splitlines() if ' T mpv_' in x}
 loads=[int(x.split()[-1],16) for x in run('llvm-readelf','-lW',dest).splitlines() if x.strip().startswith('LOAD')]
 checks={'exports_preserved':not (exports(old)-exports(symbols)),'jni_export':'mpv_lavc_set_java_vm' in exports(symbols),'elf16kb':bool(loads) and min(loads)>=16384,'no_unresolved_cpp_symbols':not any(' U _ZNSt6__ndk1' in x for x in symbols.splitlines())}
 assert all(checks.values()),checks
 result={'abi':abi,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'bytes':dest.stat().st_size,'checks':checks,'status':'blocked_pending_runtime_and_remaining_audit'}
 results.append(result);(r/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(result),flush=True)
