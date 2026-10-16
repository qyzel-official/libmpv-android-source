"""Isolated native compatibility builds. Production artifacts are never modified."""
from pathlib import Path
import subprocess, os, json, time, sys
r=Path(__file__).resolve().parent
abi=sys.argv[1]
arch={'arm64-v8a':'arm64','armeabi-v7a':'armv7','x86_64':'x64'}[abi]
prefix=r/'clean-build'/abi/'prefix'
report_dir=r/'clean-build'/abi
assert (report_dir/'result.json').exists()
assert len(json.loads((report_dir/'result.json').read_text())['stages'])==8
assert all(x['exit']==0 for x in json.loads((report_dir/'result.json').read_text())['stages'])
old='$OLDWORK/native-media-candidate/upstream/buildscripts/prefix/'+abi
for p in (prefix/'lib/pkgconfig').glob('*.pc'):
 p.write_text(p.read_text().replace(old+'/usr/local','/usr/local').replace(old,'/usr/local'))
env=os.environ.copy()
ndk='$ANDROID_SDK/ndk/28.2.13676358/toolchains/llvm/prebuilt/darwin-x86_64/bin'
env['PATH']=str(r/'host-tools/bin')+':'+ndk+':'+env['PATH']
env['PKG_CONFIG_LIBDIR']=str(prefix/'lib/pkgconfig');env['PKG_CONFIG_SYSROOT_DIR']=str(prefix)
env.pop('PKG_CONFIG_PATH',None)
cross=report_dir/('clean-'+arch+'.cross')
cross.write_text((prefix/'crossfile.txt').read_text().replace("wrap_mode = 'nodownload'", "wrap_mode = 'nodownload'\nc_args = ['-fPIC']\ncpp_args = ['-fPIC']\nc_link_args = ['-Wl,-z,max-page-size=16384']\ncpp_link_args = ['-Wl,-z,max-page-size=16384']"))
results=[]
def run(stage,args,extra_env=None):
 started=time.monotonic()
 with (report_dir/(stage+'-'+arch+'.log')).open('w') as log:
  x=subprocess.run(args,env=dict(env,**(extra_env or {})),stdout=log,stderr=subprocess.STDOUT)
 results.append({'stage':stage,'exit_code':x.returncode,'elapsed_seconds':round(time.monotonic()-started,1)})
 print(json.dumps(results[-1]),flush=True)
 (report_dir/'link-result.json').write_text(json.dumps({'abi':abi,'scope':'Clean dependencies built from locked source archives; integration candidate only','stages':results,'release_approved':False},indent=2)+'\n')
 if x.returncode:
  print((report_dir/(stage+'-'+arch+'.log')).read_text()[-2500:],flush=True);raise SystemExit(x.returncode)
def setup(name,source,extra):
 build=report_dir/'linked'/(name+'-'+arch)
 args=['meson','setup',str(build),str(source),'--cross-file',str(cross),'--prefix=/','--libdir=lib']+extra
 if (build/'meson-private/coredata.dat').exists():args.insert(2,'--reconfigure')
 run(name+'-configure',args)
 run(name+'-build',['ninja','-C',str(build),'-j2'])
 return build
b=setup('libplacebo',r/'libplacebo-maintained',['--default-library=static','-Ddemos=false','-Dtests=false','-Dvulkan=disabled','-Dshaderc=disabled','-Dglslang=disabled','-Dopengl=enabled','-Dlcms=disabled','-Dlibdovi=disabled'])
run('libplacebo-install',['ninja','-C',str(b),'install'],{'DESTDIR':str(prefix)})
setup('mpv',r/'maintained-src/mpv',['--prefer-static','--default-library=shared','-Dgpl=false','-Db_lundef=true',"-Dc_link_args=['-Wl,-z,max-page-size=16384','-Wl,--exclude-libs,ALL','-lc++_static','-lc++abi','-lunwind']",'-Dlibmpv=true','-Dbuild-date=false','-Dlua=disabled','-Dcplayer=false','-Diconv=disabled','-Dvulkan=disabled','-Dmanpage-build=disabled'])
