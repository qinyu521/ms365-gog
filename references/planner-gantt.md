# Planner 甘特图导出模块（planner-gantt.md）

> 从 Microsoft Planner 读取任务数据，生成甘特图并导出为 HTML / Excel / PNG。
> 触发词：甘特图、Gantt、项目进度图、时间线、任务时间轴、导出进度表

---

## 核心流程

```
Planner API → 获取任务 + 截止日期 → 本地生成甘特图 → 导出文件
```

---

## 1. 获取 Planner 任务数据

```python
MS_GRAPH = "https://graph.microsoft.com/v1.0"

def get_plan_with_tasks(plan_id: str, headers: dict) -> dict:
    """获取计划的任务列表、看板列（Bucket）和成员信息"""
    # 并行获取（实际代码顺序执行，可用 threading 优化）
    tasks_resp = requests.get(
        f"{MS_GRAPH}/planner/plans/{plan_id}/tasks",
        headers=headers, timeout=30
    )
    tasks_resp.raise_for_status()

    buckets_resp = requests.get(
        f"{MS_GRAPH}/planner/plans/{plan_id}/buckets",
        headers=headers, timeout=30
    )
    buckets_resp.raise_for_status()

    plan_resp = requests.get(
        f"{MS_GRAPH}/planner/plans/{plan_id}",
        headers=headers, timeout=30
    )
    plan_resp.raise_for_status()

    tasks   = tasks_resp.json().get("value", [])
    buckets = {b["id"]: b["name"] for b in buckets_resp.json().get("value", [])}
    plan    = plan_resp.json()

    # 整理任务数据
    parsed = []
    for t in tasks:
        start = t.get("startDateTime")
        due   = t.get("dueDateTime")
        if not due:
            continue  # 跳过没有截止日期的任务（甘特图必须有时间维度）

        parsed.append({
            "id":           t["id"],
            "title":        t["title"],
            "bucket":       buckets.get(t.get("bucketId", ""), "未分类"),
            "percent":      t.get("percentComplete", 0),
            "priority":     t.get("priority", 5),
            "start":        start[:10] if start else due[:10],  # 无开始日期则用截止日期
            "due":          due[:10],
            "completed":    t.get("completedDateTime", "")[:10] if t.get("completedDateTime") else None,
            "assignees":    list(t.get("assignments", {}).keys()),  # AAD 用户 ID 列表
        })

    # 按开始日期排序
    parsed.sort(key=lambda x: x["start"])
    return {"plan_title": plan.get("title"), "tasks": parsed, "buckets": buckets}
```

---

## 2. 生成交互式 HTML 甘特图

```python
from datetime import datetime, timedelta
import json

def generate_gantt_html(plan_data: dict, output_path: str = "gantt.html"):
    """生成独立的 HTML 甘特图文件，无需外部依赖"""
    tasks      = plan_data["tasks"]
    plan_title = plan_data.get("plan_title", "项目进度")

    if not tasks:
        raise ValueError("没有包含截止日期的任务，无法生成甘特图")

    # 计算时间范围（前后各留 3 天余量）
    all_dates = [t["start"] for t in tasks] + [t["due"] for t in tasks]
    min_date  = datetime.strptime(min(all_dates), "%Y-%m-%d") - timedelta(days=3)
    max_date  = datetime.strptime(max(all_dates), "%Y-%m-%d") + timedelta(days=3)
    total_days = (max_date - min_date).days

    def date_to_pct(date_str: str) -> float:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return (d - min_date).days / total_days * 100

    # 进度/优先级配色
    priority_color = {
        0: "#d32f2f",  # 紧急
        1: "#d32f2f",
        2: "#e65100",  # 重要
        3: "#e65100",
        5: "#1565c0",  # 中等
        7: "#2e7d32",  # 低
        9: "#9e9e9e",  # 极低
    }

    # 生成表格行
    rows_html = ""
    for i, t in enumerate(tasks):
        left_pct  = date_to_pct(t["start"])
        width_pct = max(date_to_pct(t["due"]) - left_pct, 1.5)  # 最少 1.5% 宽度
        color     = priority_color.get(t["priority"], "#1565c0")
        pct       = t["percent"]
        status_icon = "✅" if pct == 100 else ("🔄" if pct > 0 else "⬜")
        bucket_color_map = {}  # 动态颜色映射
        
        rows_html += f"""
        <tr class="task-row" data-bucket="{t['bucket']}">
          <td class="task-name" title="{t['title']}">
            <span class="bucket-tag">{t['bucket']}</span>
            {status_icon} {t['title'][:32]}{'…' if len(t['title'])>32 else ''}
          </td>
          <td class="date-cell">{t['start']}</td>
          <td class="date-cell">{t['due']}</td>
          <td class="pct-cell">{pct}%</td>
          <td class="bar-cell">
            <div class="bar-bg">
              <div class="bar-fill" style="left:{left_pct:.1f}%;width:{width_pct:.1f}%;background:{color}">
                <div class="bar-progress" style="width:{pct}%;background:rgba(255,255,255,0.4)"></div>
              </div>
            </div>
          </td>
        </tr>"""

    # 生成日期刻度
    scale_html = ""
    current = min_date
    while current <= max_date:
        pct = (current - min_date).days / total_days * 100
        label = current.strftime("%-m/%-d") if current.day in (1, 8, 15, 22) else ""
        is_today = current.date() == datetime.today().date()
        scale_html += f'<div class="tick{" today" if is_today else ""}" style="left:{pct:.1f}%">{label}</div>'
        current += timedelta(days=1)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{plan_title} — 甘特图</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, "Microsoft YaHei", sans-serif; font-size: 13px;
        background: #f5f5f5; color: #212121; }}
.header {{ background: #1565c0; color: #fff; padding: 16px 24px; }}
.header h1 {{ font-size: 20px; font-weight: 500; }}
.header small {{ opacity: .75; font-size: 12px; }}
.toolbar {{ background: #fff; padding: 10px 24px; border-bottom: 1px solid #e0e0e0;
            display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }}
.filter-label {{ font-size: 12px; color: #666; }}
.filter-btn {{ padding: 4px 12px; border: 1px solid #ccc; border-radius: 16px; cursor: pointer;
               background: #fff; font-size: 12px; transition: all .15s; }}
.filter-btn.active {{ background: #1565c0; color: #fff; border-color: #1565c0; }}
.gantt-wrap {{ overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; background: #fff; }}
th {{ background: #e8eaf6; padding: 8px 10px; text-align: left; font-weight: 500;
      border-bottom: 2px solid #c5cae9; position: sticky; top: 0; z-index: 10; white-space: nowrap; }}
td {{ padding: 6px 10px; border-bottom: 1px solid #f0f0f0; vertical-align: middle; }}
.task-row:hover td {{ background: #f3f4f6; }}
.task-row.hidden {{ display: none; }}
.task-name {{ min-width: 220px; max-width: 260px; }}
.date-cell {{ white-space: nowrap; color: #555; width: 90px; }}
.pct-cell {{ width: 50px; text-align: right; color: #555; }}
.bar-cell {{ min-width: 400px; padding: 4px 10px; position: relative; }}
.bar-scale {{ position: relative; height: 20px; margin-bottom: 4px; }}
.tick {{ position: absolute; top: 0; font-size: 10px; color: #999;
         transform: translateX(-50%); white-space: nowrap; }}
.tick.today {{ color: #d32f2f; font-weight: 700; }}
.tick.today::after {{ content: ''; position: absolute; top: 16px; left: 50%;
                      width: 1px; height: 9999px; background: rgba(211,47,47,.25); }}
.bar-bg {{ position: relative; height: 22px; background: #f5f5f5;
           border-radius: 4px; overflow: visible; }}
.bar-fill {{ position: absolute; top: 0; height: 22px; border-radius: 4px;
             display: flex; align-items: center; overflow: hidden;
             transition: opacity .2s; }}
.bar-fill:hover {{ opacity: .85; }}
.bar-progress {{ height: 100%; background: rgba(255,255,255,0.35); transition: width .3s; }}
.bucket-tag {{ font-size: 10px; background: #e8eaf6; color: #3949ab;
               border-radius: 10px; padding: 1px 7px; margin-right: 6px;
               display: inline-block; }}
.legend {{ padding: 12px 24px; display: flex; gap: 20px; flex-wrap: wrap; background: #fff;
           border-top: 1px solid #eee; font-size: 12px; color: #555; }}
.legend-item {{ display: flex; align-items: center; gap: 6px; }}
.legend-dot {{ width: 12px; height: 12px; border-radius: 3px; }}
@media print {{ .toolbar {{ display: none; }} body {{ background: #fff; }} }}
</style>
</head>
<body>
<div class="header">
  <h1>📊 {plan_title}</h1>
  <small>共 {len(tasks)} 个任务 · 导出时间 {datetime.now().strftime('%Y-%m-%d %H:%M')}</small>
</div>
<div class="toolbar">
  <span class="filter-label">按看板列筛选：</span>
  <button class="filter-btn active" onclick="filterBucket('全部')">全部</button>
  {"".join(f'<button class="filter-btn" onclick="filterBucket(\\'{b}\\')">{b}</button>'
           for b in dict.fromkeys(t["bucket"] for t in tasks))}
  <span style="margin-left:auto;font-size:12px;color:#888">提示：点击任务行可高亮显示</span>
</div>
<div class="gantt-wrap">
<table>
<thead>
<tr>
  <th>任务名称</th>
  <th>开始</th>
  <th>截止</th>
  <th>进度</th>
  <th>
    <div class="bar-scale">{scale_html}</div>
    时间线（{min_date.strftime('%Y-%m-%d')} → {max_date.strftime('%Y-%m-%d')}）
  </th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
</div>
<div class="legend">
  <div class="legend-item"><div class="legend-dot" style="background:#d32f2f"></div> 紧急/重要</div>
  <div class="legend-item"><div class="legend-dot" style="background:#1565c0"></div> 中等优先级</div>
  <div class="legend-item"><div class="legend-dot" style="background:#2e7d32"></div> 低优先级</div>
  <div class="legend-item"><div class="legend-dot" style="background:#9e9e9e"></div> 极低</div>
  <div class="legend-item">⬜ 未开始 &nbsp;🔄 进行中 &nbsp;✅ 已完成</div>
</div>
<script>
function filterBucket(bucket) {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  document.querySelectorAll('.task-row').forEach(row => {{
    if (bucket === '全部' || row.dataset.bucket === bucket) {{
      row.classList.remove('hidden');
    }} else {{
      row.classList.add('hidden');
    }}
  }});
}}
document.querySelectorAll('.task-row').forEach(row => {{
  row.addEventListener('click', () => row.classList.toggle('highlighted'));
}});
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ 甘特图已导出：{output_path}（{len(tasks)} 个任务）")
    return output_path
```

---

## 3. 导出为 Excel（.xlsx）

```python
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def export_gantt_excel(plan_data: dict, output_path: str = "gantt.xlsx"):
    tasks      = plan_data["tasks"]
    plan_title = plan_data.get("plan_title", "项目计划")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "甘特图"

    # 标题行样式
    header_fill = PatternFill("solid", fgColor="1565C0")
    header_font = Font(color="FFFFFF", bold=True, size=11)
    headers = ["任务名称", "看板列", "开始日期", "截止日期", "进度(%)", "优先级", "状态"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    # 数据行
    priority_map = {0: "紧急", 1: "紧急", 2: "重要", 3: "重要",
                    5: "中等", 7: "低", 9: "极低"}
    status_map = {0: "未开始", 50: "进行中", 100: "已完成"}

    for i, t in enumerate(tasks, 2):
        pct = t["percent"]
        status = "已完成" if pct == 100 else ("进行中" if pct > 0 else "未开始")
        row_data = [
            t["title"],
            t["bucket"],
            t["start"],
            t["due"],
            pct,
            priority_map.get(t["priority"], "中等"),
            status,
        ]
        for col, val in enumerate(row_data, 1):
            cell = ws.cell(row=i, column=col, value=val)
            cell.alignment = Alignment(vertical="center", wrap_text=True)

        # 进度条用条件格式颜色
        status_colors = {"已完成": "C8E6C9", "进行中": "BBDEFB", "未开始": "FFF9C4"}
        row_fill = PatternFill("solid", fgColor=status_colors[status])
        for col in range(1, len(headers) + 1):
            ws.cell(row=i, column=col).fill = row_fill

    # 列宽
    col_widths = [40, 15, 12, 12, 10, 10, 10]
    for col, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(col)].width = w

    # 冻结首行
    ws.freeze_panes = "A2"

    # 添加汇总 Sheet
    ws_summary = wb.create_sheet("汇总")
    total = len(tasks)
    done  = sum(1 for t in tasks if t["percent"] == 100)
    doing = sum(1 for t in tasks if 0 < t["percent"] < 100)
    todo  = total - done - doing

    summary_data = [
        ("项目名称", plan_title),
        ("总任务数", total),
        ("已完成", done),
        ("进行中", doing),
        ("未开始", todo),
        ("整体进度", f"{sum(t['percent'] for t in tasks) // total if total else 0}%"),
        ("导出时间", datetime.now().strftime("%Y-%m-%d %H:%M")),
    ]
    for row_idx, (label, value) in enumerate(summary_data, 1):
        ws_summary.cell(row=row_idx, column=1, value=label).font = Font(bold=True)
        ws_summary.cell(row=row_idx, column=2, value=value)

    wb.save(output_path)
    print(f"✅ Excel 甘特图已导出：{output_path}")
    return output_path
```

---

## 4. 完整使用示例

```python
from scripts.auth import get_access_token

headers = {"Authorization": f"Bearer {get_access_token()}",
           "Content-Type": "application/json"}

PLAN_ID = "你的Planner计划ID"

# 1. 获取数据
plan_data = get_plan_with_tasks(PLAN_ID, headers)
print(f"📋 计划：{plan_data['plan_title']}，共 {len(plan_data['tasks'])} 个有截止日期的任务")

# 2. 导出 HTML（交互式，可直接用浏览器打开）
html_path = generate_gantt_html(plan_data, "gantt_output.html")

# 3. 导出 Excel（可在 Excel 中进一步编辑）
excel_path = export_gantt_excel(plan_data, "gantt_output.xlsx")

# 4. 上传到 OneDrive 共享
with open(excel_path, "rb") as f:
    upload_resp = requests.put(
        f"{MS_GRAPH}/me/drive/root:/项目管理/甘特图_{datetime.now().strftime('%Y%m%d')}.xlsx:/content",
        headers={**headers, "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
        data=f.read(),
        timeout=60
    )
    upload_resp.raise_for_status()
    share_url = upload_resp.json().get("webUrl")
    print(f"📤 已上传到 OneDrive：{share_url}")
```

---

## 注意事项

1. **必须有截止日期**：Planner 任务的开始日期和截止日期都是可选字段，甘特图只处理有截止日期的任务
2. **开始日期缺失**：无开始日期的任务以截止日期作为单点任务展示（宽度为最小值）
3. **权限要求**：Planner API 需要 `Tasks.ReadWrite` 权限，且仅支持企业（AAD）账号
4. **计划 ID 获取**：可从 Planner URL 中找到，格式如 `https://tasks.office.com/.../#/plananerV2/{planId}`
5. **HTML 甘特图**：无需服务器，双击即可用浏览器打开；支持按看板列筛选和行高亮
