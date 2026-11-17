import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const FONT='Microsoft YaHei';
export async function build(presentation) {
  if (presentation.slides.items.length) throw new Error('Use an empty presentation; preserve existing artifacts');
  const ink='#19334A',muted='#506477',teal='#168A86';
  function text(slide,value,x,y,w,h,size=25,color=ink,bold=false){
    const shape=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
    shape.text=value;shape.text.style={typeface:FONT,fontSize:size,color,bold};return shape;
  }
  function page(title,source){
    const s=presentation.slides.add({width:1280,height:720});s.background.fill='#FFFFFF';
    text(s,title,64,48,1152,92,39,ink,true);
    text(s,`RC2  |  2026-11-17  |  ${presentation.slides.items.length}`,64,673,1152,25,15,muted);
    s.speakerNotes.text=source+'\n本轮为材料更新；旧测量保留原提交。代理验证不等于人工验收或赛事提交。';return s;
  }
  function table(s,values,y=165,height=350,width=1152){
    const t=s.tables.add({rows:values.length,columns:values[0].length,left:64,top:y,width,height,values});
    t.borders.assign({fill:'#D5DFE7',width:1,style:'solid'});
    for(let r=0;r<values.length;r++)for(let c=0;c<values[r].length;c++){
      const cell=t.getCell(r,c);cell.fill=r===0?ink:(r%2?'#F0F5F7':'#FFFFFF');
      cell.text.style={typeface:FONT,fontSize:25,color:r===0?'#FFFFFF':ink,bold:r===0};
    }return t;
  }
  let s=page('面向 openEuler 的数据任务实验','docs/implementation/design-and-test-report-rc2.md；测量源码bb288cb；材料起点7ef8f88');
  text(s,'CPU资源约束\n与性能回归分析',64,170,1135,210,58,ink,true);
  text(s,'固定输入  ·  独立正确性  ·  原始证据追溯',68,425,1110,70,31,teal);
  text(s,'37项目标机测试通过，0跳过\n候选材料RC2，尚未人工验收或正式提交',68,535,1100,95,26,muted);
  s=page('实验分别回答三个问题','docs/project/project-contract.md；docs/contracts/glossary.md');
  [['01','配额是否实际生效','读取服务内cpu.max及可见父级，不能只看耗时倍数'],['02','任务结果是否正确','SQLite独立聚合校验每份stdout，退出0并不足够'],['03','历史变化是否需要复核','先检查兼容条件，再读探索性阈值与无法比较原因']].forEach((v,i)=>{
    text(s,v[0],64,175+i*145,100,75,47,teal,true);text(s,v[1],205,175+i*145,1000,45,30,ink,true);text(s,v[2],205,232+i*145,1000,68,25,muted);
  });
  s=page('固定数据到可追溯报告','docs/implementation/system-design.md；docs/implementation/pipeline.md');
  [['固定CSV','LCG种子与规模\n输入SHA256'],['受限服务','单进程分组聚合\n配额与生命周期'],['独立校验','SQLite参考结果\n逐份stdout核对'],['离线报告','完整性及兼容门槛\n分布与原始run_id']].forEach((v,i)=>{
    const x=64+i*296;const bar=s.shapes.add({geometry:'rect',position:{left:x,top:190,width:264,height:72},fill:ink,line:{fill:'none',width:0}});
    text(s,v[0],x+15,203,235,45,29,'#FFFFFF',true);text(s,v[1],x,300,265,120,25,ink);if(i<3)text(s,'→',x+266,206,35,40,26,teal);
  });
  text(s,'输入生成与SQLite参考计算不属于受限负载计时\n每次运行独立保存最终记录、原始输出、实际控制和清理证据',64,490,1150,120,29,muted);
  s=page('成功结论必须逐层举证','docs/contracts/data-contract.md；docs/implementation/member-a.md');
  table(s,[['结论','需要的证据','不能替代的结论'],['执行成功','最终success、退出0','算法正确'],['功能正确','SQLite独立校验','配额已生效'],['配额生效','实际控制与父级快照','wall精确翻倍'],['性能变化','同口径样本与分布','统计显著或根因'],['历史复核信号','前提通过且超过阈值','已确认性能事故']],160,390);
  text(s,'失败、超时、中断、恢复与清理失败分别保留；未知或缺失证据拒绝比较',64,580,1150,62,24,muted);
  s=page('最终源码通过37项目标机测试','docs/validation/improvement-p1-validation.md；evidence/improvement/p1-final-openeuler-20261117.tar.gz；源码bb288cb');
  text(s,'37',64,190,370,170,128,teal,true);text(s,'通过  /  0跳过',70,365,390,60,35,ink,true);
  text(s,'原有29项 + 新增8项\n采样异常3项，SVG2项\n源码指纹2项，内存解析1项\n\n默认完整流程18次：15测量、3预热\npip check、Ruff与清理检查通过',520,175,690,380,28,ink);
  text(s,'六个代码提交分别干净检出复验，默认流程总108次；不同源码数据不混为历史基线\nWindows纯测试有9项集成跳过，GitHub在线CI尚未运行',64,565,1150,85,22,muted);
  s=page('时间随规模增长是本机观察','docs/validation/improvement-p1-validation.md#三种规模实测任务10；bb288cb；每组n=5，9条预热排除');
  const chart=s.charts.add('bar',{position:{left:64,top:155,width:830,height:420},categories:['50万行','200万行','800万行'],series:[{name:'null',values:[0.20,0.77,3.06],fill:'#7D91A6'},{name:'100%',values:[0.20,0.77,3.05],fill:teal},{name:'50%',values:[0.38,1.50,6.06],fill:'#C78A43'}],barOptions:{direction:'column',grouping:'clustered'},hasLegend:true,legend:{position:'bottom'},yAxis:{title:{text:'wall中位数 秒'},majorGridlines:{fill:'#DDE5EC',width:1,style:'solid'}},dataLabels:{showValue:true,position:'outEnd'}});
  for(const style of [chart.legend?.textStyle,chart.dataLabels?.textStyle,chart.xAxis?.textStyle,chart.yAxis?.textStyle,chart.yAxis?.title?.textStyle])if(style){style.typeface=FONT;style.fontSize=20;}
  text(s,'约17 MiB',925,210,290,70,37,teal,true);text(s,'固定1000组时\nRSS峰值中位数\n基本同量级',925,300,290,170,28,ink);
  text(s,'54次全部SQLite、配额、内存与清理核验通过。GNU time口径含内层timer开销，0.01秒分辨率\n不能泛化为普遍线性或生产规模上限，也不能与runner不同计时边界直接排速度',64,590,1152,70,21,muted);
  s=page('工具计时边界不同 不排名速度','docs/implementation/tool-comparison.md；d8a331e；400万行同输入；三档合计54次');
  table(s,[['100%配额','内部wall 秒','外部命令 秒'],['本队','1.5672','1.6442'],['GNU+systemd','1.5300','1.5777'],['hyperfine适配','1.5300','1.6072']],170,280);
  text(s,'同批54次：每种工具三档，各1预热+5测量；逐份SQLite正确性与清理通过\nhyperfine外部时间包含适配器、服务创建、快照、退出及清理\n其内部wall/CPU仍由GNU time记录，不能当成hyperfine原生逐次指标',64,485,1150,125,25,ink);
  text(s,'hyperfine在前36次后分批执行，存在时间顺序混杂；其他配额数值见技术报告',64,620,1150,40,21,muted);
  s=page('阈值矩阵只描述固定样本','evidence/comparison/threshold-matrix-20261117.json；原始48次记录；每格7条基线/7条当前；默认15%不变');
  table(s,[['额外工作量','阈值10%','阈值15%','阈值25%'],['0%健康1/2','未触发','未触发','未触发'],['5%','未触发','未触发','未触发'],['15%','需复核','需复核','未触发'],['25%','需复核','需复核','需复核']],165,330);
  text(s,'每格7对7，健康两组各自比较；工作量百分比不保证相同wall增幅\n事后阈值敏感性分析不调整既定规则，也不是普遍准确率\nno_threshold_signal不代表无退化；前提不足则unable_to_compare',64,530,1150,115,26,muted);
  s=page('观察范围保留阈值与原始数值','evidence/improvement/p1-visual/healthy-1.png；真实48次场景中的baseline对healthy-1；范围不是置信区间');
  const bytes=await fs.readFile(path.join(ROOT,'evidence/improvement/p1-visual/healthy-1.png'));
  s.images.add({dataUrl:'data:image/png;base64,'+bytes.toString('base64'),contentType:'image/png',alt:'真实健康复测的已观察范围0.9997至1.0320与1.15阈值参考线',position:{left:64,top:155,width:870,height:452},fit:'contain'});
  text(s,'已观察范围\n不是置信区间\n\n本批真实场景\n未跨过1.15\n\n跨阈值分支\n由单测夹具验证',960,200,260,360,27,ink);
  s=page('采样记录干扰 指纹约束兼容','docs/contracts/data-contract.md；host-load linux-load-v1；src-py-v2；源码0be73a7及bb288cb');
  text(s,'Linux负载证据',64,175,530,55,32,teal,true);text(s,'开始、结束及期间约每5秒采样\n读取失败留null与原因\n仅是执行Linux来宾的loadavg\n不冒充Windows物理宿主机\n不进入阈值判定',64,260,540,285,28,ink);
  text(s,'src-py-v2源码指纹',690,175,530,55,32,teal,true);text(s,'覆盖src全部.py\n相对路径与内容长度分帧\n报告代码改变也会改变摘要\n新旧指纹不同则拒绝历史比较\n原始记录不回写新哈希',690,260,530,285,28,ink);
  text(s,'run1.1 / config1.0字段形状不变；算法与附加证据格式在数据协议中分别说明',64,600,1152,55,24,muted);
  s=page('一条完整流程 保留全部原始证据','docs/implementation/pipeline.md；docs/validation/peer-reproduction.md；原始CSV可按参数及哈希复建');
  text(s,"python3 -m pip install -e '.[report]'\nPYTHONPATH=src python3 -m runner doctor\npython3 experiments/run_pipeline.py --output results/first",64,190,1150,170,27,ink);
  text(s,'固定CSV与参考结果 → 三档运行 → 独立校验 → summary与离线HTML\n每个run_id保留stdout、测量、控制与清理记录\n预热、失败、缺指标与无法比较均保留原因，不填补为成功',64,420,1152,165,28,ink);
  text(s,'输出目录必须不存在；固定源码、输入和资源环境，不能将跨机器或不同指纹样本混作基线',64,610,1152,45,22,muted);
  s=page('贡献与仍需完成的验收','docs/project/submission-checklist.md；docs/records/ai-usage.md；docs/validation/improvement-p2-progress.md');
  text(s,'已形成的可复验流程',64,175,570,55,32,teal,true);text(s,'受限执行与异常清理证据\n输入身份与SQLite正确性绑定\n保守比较门槛和离线追溯\n教学实验与版本化材料清单',64,260,560,250,29,ink);
  text(s,'仍需真实人员与平台事实',690,175,540,55,32,ink,true);text(s,'非实现者交叉验收\n正式视频与成员贡献说明\n导师、报名及官方GitLab\n最终提交版本与接收凭据',690,260,540,250,29,ink);
  text(s,'底层CPU控制、计时、SQL与schema来自既有系统和库。代理实测不代替人工验收\n尚未证实统计准确率、跨机器泛化、根因诊断或生产可靠性',64,565,1152,85,23,muted);
  return {slides:presentation.slides.items.length};
}
