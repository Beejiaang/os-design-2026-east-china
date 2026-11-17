"""Escape all external text; no network assets, scripts or raw-log execution."""
import html
import json
from pathlib import Path


def render(summary, output, comparison=None):
    esc = lambda value: html.escape(str(value), quote=True)
    fmt = lambda value: esc(f"{value:.4f}" if type(value) is float else value)
    groups = "".join("<tr>" + "".join("<td>" + fmt(group.get(key)) + "</td>" for key in
                     ("quota_percent", "n", "wall_median_seconds", "wall_min_seconds", "wall_max_seconds",
                      "cpu_median_seconds", "wall_ratio_to_unlimited", "comparable")) + "</tr>" for group in summary["groups"])
    runs = "".join("<tr><td>" + esc(row["run_id"]) + "</td><td>" + esc(row["quota_percent"]) +
                   "</td><td>" + fmt(row["wall_seconds"]) + "</td><td>" + fmt(row["cpu_seconds"]) +
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
    if summary["eligible"]:
        maximum = max(row["wall_seconds"] for row in summary["eligible"]) * 1.1 or 1
        height = 70 + 55 * len(summary["groups"])
        plot = f'<svg role="img" aria-label="每次已校验运行的耗时，单位秒" viewBox="0 0 900 {height}" style="min-width:600px;width:100%">'
        for tick in range(5):
            x = 150 + 680 * tick / 4
            plot += f'<line x1="{x}" y1="15" x2="{x}" y2="{height - 35}" stroke="#dde4ed"/><text x="{x}" y="{height - 10}" text-anchor="middle" fill="#526478">{maximum * tick / 4:.2f} s</text>'
        for index, group in enumerate(summary["groups"]):
            y = 40 + 55 * index
            label = "null（未设本地配额）" if group["quota_percent"] is None else str(group["quota_percent"]) + "%"
            plot += f'<text x="5" y="{y + 5}" font-size="13">{esc(label)}</text>'
            for row in summary["eligible"]:
                if row["quota_percent"] == group["quota_percent"]:
                    x = 150 + 680 * row["wall_seconds"] / maximum
                    plot += f'<circle cx="{x}" cy="{y}" r="5" fill="#168a86" fill-opacity="0.55"><title>{esc(row["run_id"])}: {row["wall_seconds"]:.4f} s</title></circle>'
        document += "<section><h2>逐次耗时分布</h2><p>每个点对应一条已校验的非预热记录；重叠点可能不可分辨。原始值见下表。不完整实验中的点仅作记录展示。</p>" + plot + "</svg></section>"
    document += "<section><h2>已校验的非预热测量</h2><table><tr><th>run_id</th><th>配额 %</th><th>耗时 s</th><th>CPU s</th><th>最终原始记录</th></tr>" + runs + "</table></section>"
    document += "<section><h2>排除、问题与追溯证据</h2><pre>" + esc(details) + "</pre></section></html>"
    Path(output).write_text(document, encoding="utf-8")
