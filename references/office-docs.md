# Word / Excel 在线文档模块（office-docs.md）

> M365 文档操作通过两种方式实现：
> 1. **内容读取/简单编辑**：Graph API（适合结构化数据提取）
> 2. **复杂格式编辑**：下载 → 本地用 python-docx/openpyxl 修改 → 上传回 OneDrive

## Word 文档

### 读取 Word 文档文本内容
```python
# 方法1：直接转换为 HTML（保留基本格式）
resp = requests.get(
    f"{MS_GRAPH}/me/drive/items/{item_id}/content",
    headers={**headers, "Accept": "text/html"},
    allow_redirects=True
)
html_content = resp.text

# 方法2：下载 docx 后用 python-docx 解析
import requests, tempfile
from docx import Document  # pip install python-docx --break-system-packages

resp = requests.get(f"{MS_GRAPH}/me/drive/items/{item_id}/content",
                    headers=headers, allow_redirects=True)
with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
    f.write(resp.content)
    tmp_path = f.name

doc = Document(tmp_path)
full_text = "\n".join(p.text for p in doc.paragraphs)
```

### 编辑并回传 Word 文档
```python
from docx import Document
import requests, io

# 1. 下载
resp = requests.get(f"{MS_GRAPH}/me/drive/items/{item_id}/content",
                    headers=headers, allow_redirects=True)
doc = Document(io.BytesIO(resp.content))

# 2. 修改（示例：追加段落）
doc.add_paragraph("新增内容：" + new_content)

# 3. 上传回原路径
buf = io.BytesIO()
doc.save(buf)
buf.seek(0)
requests.put(
    f"{MS_GRAPH}/me/drive/items/{item_id}/content",
    headers={**headers, "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    data=buf.read()
)
```

## Excel 文档

### 读取工作表数据（Graph API 直接操作，无需下载）
```python
# 列出工作表
sheets = requests.get(
    f"{MS_GRAPH}/me/drive/items/{item_id}/workbook/worksheets",
    headers=headers
).json().get("value", [])

# 读取指定范围
resp = requests.get(
    f"{MS_GRAPH}/me/drive/items/{item_id}/workbook/worksheets/{sheet_name}/range(address='A1:D10')",
    headers=headers
)
data = resp.json()
values = data["values"]  # 二维数组
```

### 写入单元格
```python
requests.patch(
    f"{MS_GRAPH}/me/drive/items/{item_id}/workbook/worksheets/{sheet_name}/range(address='A1:B2')",
    headers=headers,
    json={"values": [["姓名", "分数"], ["张三", 95]]}
)
```

### 创建表格并追加数据
```python
# 创建 Table
table_resp = requests.post(
    f"{MS_GRAPH}/me/drive/items/{item_id}/workbook/worksheets/{sheet_name}/tables/add",
    headers=headers,
    json={"address": "A1:C1", "hasHeaders": True}
)
table_id = table_resp.json()["id"]

# 追加行
requests.post(
    f"{MS_GRAPH}/me/drive/items/{item_id}/workbook/worksheets/{sheet_name}/tables/{table_id}/rows/add",
    headers=headers,
    json={"values": [["李四", "工程部", 88000]]}
)
```

### 用 openpyxl 进行复杂编辑（图表、公式、样式）
```python
import openpyxl, io  # pip install openpyxl --break-system-packages

resp = requests.get(f"{MS_GRAPH}/me/drive/items/{item_id}/content",
                    headers=headers, allow_redirects=True)
wb = openpyxl.load_workbook(io.BytesIO(resp.content))
ws = wb.active

# 修改...
ws["A1"] = "更新值"

# 回传
buf = io.BytesIO()
wb.save(buf)
buf.seek(0)
requests.put(
    f"{MS_GRAPH}/me/drive/items/{item_id}/content",
    headers={**headers, "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    data=buf.read()
)
```

## 输出格式建议
- 读取文档：展示结构化摘要（标题层级/表格数据前10行）
- 编辑完成：✅ 已更新文档，在线查看：[webUrl]
- 大文档（>100页/10000行）：提示用户可能需要较长处理时间
