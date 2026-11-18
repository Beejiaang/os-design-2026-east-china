"""Escape all external text; no network assets, scripts or raw-log execution."""
import html
import json
import math
from pathlib import Path


def range_bar(row, threshold):
    """Observed extrema only; never draw missing/non-finite data as zero."""
    bounds = row.get("observed_range_ratio_bounds")
    if (not isinstance(bounds, (list, tuple)) or len(bounds) != 2 or
            any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in bounds) or
            bounds[0] > bounds[1] or type(threshold) not in (int, float) or
            not math.isfinite(threshold) or threshold <= 0):
        return "<p>观察范围不可用</p>"
    low, high = bounds
    reference = 1 + threshold
    minimum = min(1, low, reference) - 0.05
    maximum = max(1, high, reference) + 0.05

    def x(value):
        return 30 + 360 * (value - minimum) / (maximum - minimum)

    color = "#b46a08" if row.get("threshold_sensitive") is True else "#168a86"
    title = f"已观察比值范围 {low:.4f} 至 {high:.4f}；阈值参考线 {reference:.4f}；不是置信区间"
    return (f'<svg role="img" aria-label="{title}" viewBox="0 0 430 115" style="min-width:300px;width:100%">'
            f'<title>{title}</title><line x1="30" y1="45" x2="390" y2="45" stroke="#dae2eb"/>'
            f'<line x1="{x(1):.2f}" y1="22" x2="{x(1):.2f}" y2="62" stroke="#7d8da0"/>'
            f'<line x1="{x(reference):.2f}" y1="15" x2="{x(reference):.2f}" y2="65" stroke="#a32a40" stroke-dasharray="4 3"/>'
            f'<line x1="{x(low):.2f}" y1="45" x2="{x(high):.2f}" y2="45" stroke="{color}" stroke-width="8" stroke-linecap="round"/>'
            f'<text x="{x(1):.2f}" y="85" text-anchor="middle" font-size="12">1.00</text>'
            f'<text x="{x(reference):.2f}" y="12" text-anchor="middle" font-size="12">阈值 {reference:.2f}</text>'
            f'<text x="30" y="108" font-size="12">范围 {low:.4f}–{high:.4f}</text></svg>')


def render(summary, output, comparison=None):
    def esc(value):
        return html.escape(str(value), quote=True)

    def fmt(value):
        if value is None:
            return "—"
        return esc(f"{value:.4f}" if type(value) is float else value)
    groups = "".join("<tr>" + "".join("<td>" + ("null" if key == "quota_percent" and group[key] is None else fmt(group.get(key))) + "</td>" for key in
                     ("quota_percent", "n", "wall_median_seconds", "wall_min_seconds", "wall_max_seconds",
                      "cpu_median_seconds", "wall_ratio_to_unlimited", "comparable")) + "</tr>" for group in summary["groups"])
    def counter_cells(row):
        cells = []
        for field in ("nr_periods", "nr_throttled", "throttled_usec"):
            value = row["cpu_stat_delta"].get(field)
            cells.append("<td>" + (str(value) if type(value) is int and value >= 0 else "未提供") + "</td>")
        return "".join(cells)

    runs = "".join("<tr><td>" + esc(row["run_id"]) + "</td><td>" + esc("null" if row["quota_percent"] is None else row["quota_percent"]) +
                   "</td><td>" + fmt(row["wall_seconds"]) + "</td><td>" + fmt(row["cpu_seconds"]) + "</td>" + counter_cells(row) +
                   "<td>" + esc(summary["artifacts"][row["run_id"]]["result"]) + "</td></tr>" for row in summary["eligible"])
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
    document += "<section><h2>已校验的非预热测量</h2><p>服务 cgroup 的 cpu.stat 起止差值给出配额周期数、节流次数和累计节流时间。可用 run_id 核对原始记录。累计节流时间与进程 CPU 时间、整项任务耗时的统计范围不同。</p><table><tr><th>run_id</th><th>配额 %</th><th>耗时 s</th><th>CPU s</th><th>配额周期数</th><th>节流次数</th><th>节流时间 μs</th><th>最终原始记录</th></tr>" + runs + "</table></section>"
    if comparison is not None:
        labels = {"unable_to_compare": "无法比较", "slowdown_needs_review": "变慢信号，需复核",
                  "no_threshold_signal": "未触发阈值（不表示无退化）"}
        history_rows = "".join("<tr>" + "".join("<td>" + fmt(value) + "</td>" for value in
                               ("null" if row["quota_percent"] is None else row["quota_percent"], row["baseline_n"], row["current_n"], row["wall_ratio"],
                                labels[row["verdict"]], row.get("threshold_sensitive"), "; ".join(row["reasons"]))) + "</tr>" for row in comparison["comparisons"])
        document += "<section><h2>历史比较 · 探索性复核规则</h2><p>" + esc(comparison["note"]) + "</p><p>最少样本数：" + esc(comparison["minimum"]) + "；预设变化阈值：" + esc(comparison["threshold"]) + "</p><p>阈值敏感=true 表示两组已观察到的耗时范围可组合出阈值两侧的比值，需留意波动；这不是置信区间。精确范围见追溯数据。</p><table><tr><th>配额 %</th><th>基线 n</th><th>当前 n</th><th>耗时比</th><th>规则输出</th><th>阈值敏感</th><th>原因</th></tr>" + history_rows + "</table></section>"
        bars = "".join('<div><h3>配额 ' + esc('null' if row["quota_percent"] is None else str(row["quota_percent"]) + '%') + '</h3>' +
                       range_bar(row, comparison["threshold"]) + '</div>' for row in comparison["comparisons"])
        document += '<section><h2>历史比较的观察范围</h2><p>已观察范围敏感性，不是置信区间。虚线为 1+threshold；颜色仅提示是否跨阈值。各图按自身范围缩放，数值以标签为准。</p>' + bars + '</section>'
    document += "<section><h2>排除、问题与追溯证据</h2><pre>" + esc(details) + "</pre></section></html>"
    Path(output).write_text(document, encoding="utf-8")
