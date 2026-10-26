import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

import requests

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('discover',ROOT/'scripts/discover.py')
discover=importlib.util.module_from_spec(spec);spec.loader.exec_module(discover)


def release(tag,ready=True,**values):
    return {'tag_name':tag,'assets':[{'name':f'llama-{tag}-bin-win-cpu-x64.zip'}] if ready else [],**values}


class DiscoveryTests(unittest.TestCase):
    def test_rolling_cpu_track_is_selected_instead_of_unrelated_stable_tag(self):
        values=[release('v0.7.0'),release('b11901',False),release('b11900'),release('b11899')]
        self.assertEqual(discover.latest_windows_cpu_build(values),'b11900')

    def test_drafts_and_missing_cpu_assets_are_not_reported_as_ready(self):
        with self.assertRaises(ValueError):
            discover.latest_windows_cpu_build([release('b11900',False),release('b11901',draft=True)])

    def test_failed_source_does_not_hide_other_sources_or_expose_a_token(self):
        calls=[]
        def get(url,**kwargs):
            calls.append((url,kwargs['headers']))
            if 'pypi.org/pypi/easyocr/' in url:
                response=SimpleNamespace(status_code=503)
                raise requests.HTTPError('Untrusted server message',response=response)
            if 'pypi.org' in url:value={'info':{'version':'99.0.0'}}
            elif 'tesseract/releases' in url:value={'tag_name':'5.6.0'}
            elif 'tessdata_fast/commits' in url:value={'sha':'new-tessdata-revision'}
            elif 'llama.cpp/releases?' in url:value=[release('v0.7.0'),release('b11900')]
            else:value={'sha':'new-model-revision'}
            return SimpleNamespace(raise_for_status=lambda:None,json=lambda:value)
        with mock.patch.dict(os.environ,{'GITHUB_TOKEN':'test-secret-value'}):
            rows=discover.collect(get=get)
        self.assertEqual(len(rows),10)
        self.assertEqual(next(row['pinned'] for row in rows if row['package']=='torch'),'2.14.1')
        failed=next(row for row in rows if row['package']=='easyocr')
        self.assertIsNone(failed['candidate']);self.assertEqual(failed['http_status'],503)
        self.assertTrue(all(row['candidate'] for row in rows if row is not failed))
        self.assertTrue(all(row['approved'] is False for row in rows))
        self.assertNotIn('test-secret-value',str(rows))
        for url,headers in calls:
            self.assertEqual(bool(headers),url.startswith('https://api.github.com/'))


if __name__=='__main__':unittest.main()
