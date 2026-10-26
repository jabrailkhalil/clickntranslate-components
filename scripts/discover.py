"""Report upstream candidates; never modify approval metadata or release assets."""
import json
import os
from pathlib import Path
import re
import requests
from packaging.version import Version

ROOT=Path(__file__).resolve().parents[1]


def latest_windows_cpu_build(releases):
    # /releases/latest selects a separate v0.x stable track. The application's
    # Windows CPU bundles belong to the bNNNN rolling track.
    ready=[release for release in releases
           if re.fullmatch(r'b\d+',release.get('tag_name',''))
           and not release.get('draft')
           and any(asset.get('name')==f"llama-{release['tag_name']}-bin-win-cpu-x64.zip"
                   for asset in release.get('assets',()))]
    if not ready:raise ValueError('No published Windows CPU rolling bundle')
    return max(ready,key=lambda release:int(release['tag_name'][1:]))['tag_name']


def collect(get=requests.get, root=ROOT):
    results=[]
    token=os.environ.get('GITHUB_TOKEN')
    headers={'Authorization':'Bearer '+token} if token else {}
    def fetch(url):
        response=get(url,timeout=30,headers=headers if url.startswith('https://api.github.com/') else {})
        response.raise_for_status()
        return response.json()
    def record(package,pinned,load,*,revision=False,numeric_prefix=''):
        try:
            latest=load()
            changed=(latest!=pinned if revision else
                     Version(latest.removeprefix(numeric_prefix))>Version(pinned.removeprefix(numeric_prefix)))
            results.append({'package':package,'pinned':pinned,'upstream':latest,
                            'candidate':changed,'approved':False})
        except Exception as error:
            # A failed source must not hide other results or look up to date.
            # Never copy response headers/tokens into the public report.
            results.append({'package':package,'pinned':pinned,'upstream':None,'candidate':None,
                            'approved':False,'error':type(error).__name__,
                            'http_status':getattr(getattr(error,'response',None),'status_code',None)})
    watched={'rapidocr':'3.10.0','onnxruntime':'1.30.0','easyocr':'1.7.2','argostranslate':'1.11.0'}
    for name in ('rapidocr','argos'):
        recipe=json.loads((root/f'recipes/{name}-windows-x64.json').read_bytes())
        for item in [*recipe.get('requirements',()),*recipe.get('requirements_no_deps',())]:
            match=re.fullmatch(r'([\w-]+)(?:\[[^]]+\])?==([^ ;]+)',item)
            if match and match[1] in watched:watched[match[1]]=match[2]
    for name,pinned in watched.items():
        record(name,pinned,lambda name=name:fetch(f'https://pypi.org/pypi/{name}/json')['info']['version'])
    tesseract=json.loads((root/'recipes/tesseract-windows-x64.json').read_bytes())
    record('tesseract','.'.join(tesseract['version'].split('.')[:3]),
           lambda:fetch('https://api.github.com/repos/tesseract-ocr/tesseract/releases/latest')['tag_name'].removeprefix('v'))
    record('tessdata_fast',tesseract['models']['commit'],
           lambda:fetch('https://api.github.com/repos/tesseract-ocr/tessdata_fast/commits/main')['sha'],revision=True)
    hymt=json.loads((root/'recipes/hymt-windows-x64.json').read_bytes())
    record('llama.cpp-windows-cpu',hymt['runner']['tag'],
           lambda:latest_windows_cpu_build(fetch('https://api.github.com/repos/ggml-org/llama.cpp/releases?per_page=20')),
           numeric_prefix='b')
    record('HY-MT1.5-1.8B-GGUF repository',hymt['model']['revision'],
           lambda:fetch('https://huggingface.co/api/models/tencent/HY-MT1.5-1.8B-GGUF')['sha'],revision=True)
    return results


def main():
    results=collect()
    Path('report.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    summary=os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary,'a',encoding='utf-8') as stream:
            stream.write('# Upstream candidates\n\nNo candidate is published automatically.\n\n')
            for item in results:
                state=('unavailable: '+item['error'] if item.get('error') else
                       f"upstream {item['upstream']}; candidate={item['candidate']}")
                stream.write(f"- {item['package']}: pinned {item['pinned']}; {state}\n")
    failed=any(item.get('error') for item in results)
    print('Upstream report saved; stable catalog unchanged. Source failures: '+str(failed))
    return 1 if failed else 0


if __name__=='__main__':
    raise SystemExit(main())
