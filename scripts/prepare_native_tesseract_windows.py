"""Build a PNG-only Windows Tesseract from pinned sources, never an application."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import zipfile
import requests


def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def prepare(recipe_path,output):
    recipe=json.loads(recipe_path.read_bytes())
    if os.name!='nt' or output.exists():raise RuntimeError('Use a fresh directory on native Windows')
    output.mkdir(parents=True);prefix=output/'prefix';sources={};archives=[]
    locator=Path(os.environ['ProgramFiles(x86)'])/'Microsoft Visual Studio/Installer/vswhere.exe'
    installation=subprocess.check_output([str(locator),'-latest','-products','*','-requires',
        'Microsoft.VisualStudio.Component.VC.Tools.x86.x64','-property','installationPath'],text=True).strip()
    if not installation:raise RuntimeError('Microsoft C++ build tools are missing')
    setup=Path(installation)/'VC/Auxiliary/Build/vcvars64.bat'
    result=subprocess.run(['cmd.exe','/s','/c',f'call "{setup}" >nul && set'],capture_output=True,text=True,check=True)
    environment=os.environ.copy()
    environment.update(line.split('=',1) for line in result.stdout.splitlines() if '=' in line and not line.startswith('='))
    for item in recipe['sources']:
        archive=output/(item['name']+'.tar.gz')
        with requests.get(item['url'],stream=True,timeout=120) as response:
            response.raise_for_status()
            with archive.open('wb') as target:
                for block in response.iter_content(1024*1024):target.write(block)
        if archive.stat().st_size!=item['size'] or digest(archive)!=item['sha256']:raise RuntimeError('Source digest mismatch: '+item['name'])
        folder=output/'sources'/item['name'];folder.mkdir(parents=True)
        with tarfile.open(archive,'r:gz') as bundle:bundle.extractall(folder,filter='data')
        sources[item['name']]=next(p for p in folder.iterdir() if p.is_dir());archives.append(archive)
    flags=['-G','Ninja','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_POLICY_VERSION_MINIMUM=3.5',
        '-DCMAKE_POLICY_DEFAULT_CMP0091=NEW','-DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded',
        '-DBUILD_SHARED_LIBS=OFF','-DCMAKE_INSTALL_PREFIX='+str(prefix),'-DCMAKE_PREFIX_PATH='+str(prefix)]
    def build(name,extra):
        build_dir=output/('build-'+name)
        subprocess.run(['cmake','-S',str(sources[name]),'-B',str(build_dir),*flags,*extra],check=True,env=environment)
        subprocess.run(['cmake','--build',str(build_dir),'--parallel','4','--target','install'],check=True,env=environment)
    build('zlib',['-DZLIB_BUILD_EXAMPLES=OFF'])
    zlib=next(p for p in (prefix/'lib').glob('*.lib') if 'static' in p.name.lower() and 'zlib' in p.name.lower())
    flags+=['-DZLIB_LIBRARY='+str(zlib),'-DZLIB_INCLUDE_DIR='+str(prefix/'include'),'-DZLIB_USE_STATIC_LIBS=ON']
    build('libpng',['-DPNG_SHARED=OFF','-DPNG_STATIC=ON','-DPNG_TESTS=OFF','-DPNG_TOOLS=OFF'])
    png=next(p for p in (prefix/'lib').glob('*.lib') if 'png' in p.name.lower() and 'static' in p.name.lower())
    flags+=['-DPNG_LIBRARY='+str(png),'-DPNG_PNG_INCLUDE_DIR='+str(prefix/'include')]
    build('leptonica',['-DBUILD_PROG=OFF','-DENABLE_GIF=OFF','-DENABLE_JPEG=OFF','-DENABLE_TIFF=OFF',
        '-DENABLE_WEBP=OFF','-DENABLE_OPENJPEG=OFF','-DSW_BUILD=OFF'])
    build('tesseract',['-DBUILD_TRAINING_TOOLS=OFF','-DBUILD_TESTS=OFF','-DDISABLE_CURL=ON',
        '-DDISABLE_ARCHIVE=ON','-DDISABLE_TIFF=ON','-DENABLE_NATIVE=OFF','-DGRAPHICS_DISABLED=ON','-DOPENMP_BUILD=OFF'])
    runtime=output/'runtime';runtime.mkdir();executable=runtime/'tesseract.exe'
    shutil.copy2(prefix/'bin/tesseract.exe',executable)
    import pefile
    pe=pefile.PE(str(executable));imports=[entry.dll.decode('ascii') for entry in pe.DIRECTORY_ENTRY_IMPORT]
    allowed={'kernel32.dll','user32.dll','advapi32.dll','shell32.dll','ole32.dll','bcrypt.dll'}
    if any(name.lower() not in allowed and not name.lower().startswith(('api-ms-win-','ext-ms-win-')) for name in imports):
        raise RuntimeError('Review undeclared external dependencies: '+repr(imports))
    pe.close()
    for name,folder in sources.items():
        for path in folder.rglob('*'):
            if path.is_file() and path.name.upper().startswith(('LICENSE','COPYING','NOTICE','COPYRIGHT')):
                target=runtime/'licenses'/name/path.relative_to(folder);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
    (runtime/'SOURCE-PROVENANCE.json').write_text(json.dumps(recipe,indent=2)+'\n')
    (runtime/'NATIVE-DEPENDENCIES.json').write_text(json.dumps({'static_libraries':['tesseract','leptonica','libpng','zlib'],
        'system_imports':imports,'private_runtime_Dlls':[]},indent=2)+'\n')
    moved=output/'relocated runtime with spaces';runtime.rename(moved)
    version=subprocess.check_output([str(moved/'tesseract.exe'),'--version'],text=True,stderr=subprocess.STDOUT)
    assert version.startswith('tesseract 5.5.3'),version
    runtime=moved
    from PIL import Image,ImageDraw
    image=output/'fixture.png';pil=Image.new('RGB',(500,100),'white');ImageDraw.Draw(pil).text((20,20),'TEST 123',fill='black',font_size=40);pil.save(image)
    models=output/'models';models.mkdir();results={}
    for language,item in recipe['test_models'].items():
        response=requests.get(item['url'],timeout=90);response.raise_for_status()
        path=models/(language+'.traineddata');path.write_bytes(response.content)
        assert digest(path)==item['sha256']
        result=subprocess.run([str(runtime/'tesseract.exe'),str(image),'stdout','--tessdata-dir',str(models),'-l',language,'--psm','6'],capture_output=True,text=True,timeout=60)
        assert result.returncode==0,result.stderr
        results[language]=result.stdout.strip()
    assert 'TEST' in results['eng'],results
    archive=output/'tesseract-windows-x64-5.5.3-native-runtime.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as bundle:
        for path in sorted(runtime.rglob('*')):
            if path.is_file():bundle.write(path,path.relative_to(runtime).as_posix())
    # Original source archives and exact build recipe remain downloadable together.
    with zipfile.ZipFile(output/'tesseract-windows-x64-5.5.3-native-sources.zip','w',zipfile.ZIP_STORED) as bundle:
        for path in archives:bundle.write(path,path.name)
        bundle.write(recipe_path,'recipe.json');bundle.write(__file__,'prepare_native_tesseract_windows.py')
    descriptor={'filename':archive.name,'size':archive.stat().st_size,'sha256':digest(archive),
        'unpacked_size':sum(p.stat().st_size for p in runtime.rglob('*') if p.is_file()),'recipe':recipe}
    (output/'runtime-artifact.json').write_text(json.dumps(descriptor,indent=2)+'\n')
    (output/'verification.json').write_text(json.dumps({'relocation_with_spaces':True,'native_models':results,'version':version,
        'imports':imports,'runtime_sha256':descriptor['sha256'],'application_build':False},indent=2)+'\n')
    print(json.dumps({k:v for k,v in descriptor.items() if k!='recipe'}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--recipe',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();prepare(args.recipe,args.output.resolve())
