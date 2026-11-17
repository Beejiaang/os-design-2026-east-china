import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'src'))
from analysis.core import analyze
from jsonschema import Draft202012Validator,FormatChecker
root=Path.cwd()
base=root/'results/release-20261117/results/release'
summary=analyze(base/'experiment')
assert summary['complete'] and summary['issues']==[]
assert len(summary['eligible'])==15 and len(summary['excluded'])==3
assert all(g['comparable'] and g['n']==5 for g in summary['groups'])
validator=Draft202012Validator(json.loads((root/'schemas/run-1.1.schema.json').read_text()),format_checker=FormatChecker())
records=list((base/'experiment').glob('*/result.json'))
assert len(records)==18
for path in records:
    row=json.loads(path.read_text());validator.validate(row)
    assert row['git_commit']=='086aff71451ffaa4bd15a967a61984e445c5a720',row.keys()
    assert row['git_dirty']=='' and row['cleanup_ok'] and row['status']=='success'
    assert row['stdout_sha256']==hashlib.sha256((path.parent/'stdout.log').read_bytes()).hexdigest()
expected=json.loads((base/'summary.json').read_text())
assert summary['groups']==expected['groups']
output={'source_commit':'086aff71451ffaa4bd15a967a61984e445c5a720','finalized':18,'schema_pass':18,'eligible_nonwarmup':15,'excluded_warmups':3,'issues':summary['issues'],'groups':summary['groups'],'correctness':'all 18 independently verified by pipeline and bound stdout hashes checked again','original_paths':'preserved, not rewritten'}
(root/'evidence/release/audit.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=root/'evidence/release/release-openeuler-20261117.tar.gz'
(root/'evidence/release/SHA256SUMS').write_text(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n',encoding='utf-8')
print(json.dumps({'finalized':18,'schema_pass':18,'eligible':15,'warmups':3,'issues':0,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
