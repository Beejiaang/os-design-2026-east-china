from pathlib import Path
import sys,re,subprocess
root=Path.cwd();sys.path[:0]=[str(root/'src'),str(root)]
from analysis.core import analyze,compare
from report.html import render
source=root/'results/comparison-20261117/results/regression'
base=analyze(source/'baseline/experiment')
out=root/'work/p1-visual';out.mkdir(exist_ok=True)
for name in ('healthy-1','boundary-15'):
 current=analyze(source/name/'experiment');assert current['complete'] and base['complete']
 render(current,out/(name+'.html'),compare(base,current))
 full=(out/(name+'.html')).read_text(encoding='utf-8')
 style=re.search(r'<style>(.*?)</style>',full,re.S).group(0)
 section=next(part for part in re.findall(r'<section>.*?</section>',full,re.S) if '<h2>历史比较的观察范围</h2>' in part)
 page=out/(name+'-section.html');page.write_text('<!doctype html><meta charset="utf-8">'+style+section,encoding='utf-8')
 browser=Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')
 args=[str(browser),'--headless','--hide-scrollbars','--no-first-run','--user-data-dir='+str(out/('profile-'+name)), '--window-size=1000,520','--screenshot='+str(out/(name+'.png')),page.as_uri()]
 result=subprocess.run(args,capture_output=True,timeout=40,creationflags=subprocess.CREATE_NO_WINDOW)
 (out/(name+'-browser.log')).write_bytes(result.stdout+result.stderr)
 assert (out/(name+'.png')).exists()
 print(name,compare(base,current)['comparisons'][0]['observed_range_ratio_bounds'])
