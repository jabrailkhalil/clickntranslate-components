"""Report new upstream candidates without modifying trusted metadata."""
import json
import os
from pathlib import Path
import requests
from packaging.version import Version

WATCHED = {'rapidocr': '3.10.0', 'onnxruntime': '1.30.0',
           'easyocr': '1.7.2', 'argostranslate': '1.11.0'}
results = []
for name, pinned in WATCHED.items():
    response = requests.get(f'https://pypi.org/pypi/{name}/json', timeout=30)
    response.raise_for_status()
    latest = response.json()['info']['version']
    results.append({'package': name, 'pinned': pinned, 'upstream': latest,
                    'candidate': Version(latest) > Version(pinned), 'approved': False})
Path('report.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
summary = os.environ.get('GITHUB_STEP_SUMMARY')
if summary:
    with open(summary, 'a', encoding='utf-8') as stream:
        stream.write('# Upstream candidates\n\nNo candidate is published automatically.\n\n')
        for item in results:
            stream.write(f"- {item['package']}: pinned {item['pinned']}; upstream {item['upstream']}; candidate={item['candidate']}\n")
print('Upstream report saved; stable catalog was not changed.')
