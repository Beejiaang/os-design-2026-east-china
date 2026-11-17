from pathlib import Path
import importlib.util,tempfile,json
spec=importlib.util.spec_from_file_location('materials','scripts/material_manifest.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(dir='work') as temp:
 root=Path(temp).resolve(); (root/'demo/delivery').mkdir(parents=True)
 (root/'demo/delivery/release-manifest.json').write_text(json.dumps({'files':{'demo/delivery/frozen.pdf':'0'*64},'implementation_snapshot':'fixture','measurement_sources':[],'analysis_source':'fixture'}))
 (root/'demo/delivery/frozen.pdf').write_bytes(b'explicit non-PDF fixture')
 m.ROOT=root;m.git=lambda *args:''
 try:m.generate(root/'out.md')
 except ValueError as exc: assert 'hash mismatch' in str(exc);print('PASS: altered frozen bytes rejected; production materials unchanged')
 else:raise AssertionError('Drift accepted')
