"""Escape all external text; no network assets, scripts or raw-log execution."""
import html
import json
from pathlib import Path


def render(summary, output, comparison=None):
    esc = lambda value: html.escape(str(value), quote=True)
    groups = "".join("<tr>" + "".join("<td>" + esc(group.get(key)) + "</td>" for key in
                     ("quota_percent", "n", "wall_median_seconds", "wall_min_seconds", "wall_max_seconds",
                      "cpu_median_seconds", "wall_ratio_to_unlimited", "comparable")) + "</tr>" for group in summary["groups"])
    runs = "".join("<tr><td>" + esc(row["run_id"]) + "</td><td>" + esc(row["quota_percent"]) +
                   "</td><td>" + esc(row["wall_seconds"]) + "</td><td>" + esc(row["cpu_seconds"]) +
                   "</td><td>" + esc(summary["artifacts"][row["run_id"]]["result"]) + "</td></tr>" for row in summary["eligible"])
    details = json.dumps({"issues": summary["issues"], "excluded": summary["excluded"],
                          "group_reasons": [{"quota": g["quota_percent"], "reasons": g["reasons"]} for g in summary["groups"]],
                          "history": comparison, "artifacts": summary["artifacts"]}, ensure_ascii=False, indent=2)
    document = """<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CPU 配额实验报告</title><style>
body{font:16px/1.6 system-ui,sans-serif;background:#f3f6fa;color:#192b3d;max-width:1200px;margin:32px auto;padding:0 24px}
h1{font-size:30px}section{background:white;border:1px solid #dae2eb;border-radius:12px;padding:20px;margin:20px 0;overflow:auto}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}td,th{border-bottom:1px solid #ddd;text-align:left;padding:10px}
pre{white-space:pre-wrap;word-break:break-word;font-size:13px}.badge{background:#dfe9f4;padding:8px 16px;border-radius:8px}
</style><h1>数据聚合 · CPU 配额实验报告</h1>"""
    document += '<p class="badge">实验完整：' + esc(summary["complete"]) + " · 最终记录：" + esc(summary["finalized_count"]) + " / " + esc(summary["planned_count"]) + "</p>"
    document += "<p>" + esc(summary["note"]) + "</p><p>目录：" + esc(summary["directory"]) + "</p>"
    document += "<section><h2>配置对照</h2><p>null 表示本工具未设置本地配额；100% 是一个逻辑 CPU 的上限。倍数仅在可比条件通过时展示。</p><table><tr><th>配额 %</th><th>样本数</th><th>耗时中位数 s</th><th>最小 s</th><th>最大 s</th><th>CPU 中位数 s</th><th>相对 null</th><th>可比</th></tr>" + groups + "</table></section>"
    document += "<section><h2>已校验的非预热测量</h2><table><tr><th>run_id</th><th>配额 %</th><th>耗时 s</th><th>CPU s</th><th>最终原始记录</th></tr>" + runs + "</table></section>"
    document += "<section><h2>排除、问题与追溯证据</h2><pre>" + esc(details) + "</pre></section></html>"
    Path(output).write_text(document, encoding="utf-8")
