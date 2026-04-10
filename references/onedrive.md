# OneDrive 文件模块（onedrive.md）

## 常用操作速查

### 列出根目录文件
```python
resp = requests.get(f"{MS_GRAPH}/me/drive/root/children", headers=headers,
                    params={"$select": "name,size,lastModifiedDateTime,webUrl,folder,file"})
items = resp.json().get("value", [])
```

### 按路径访问文件夹
```python
path = "Documents/项目资料"
resp = requests.get(f"{MS_GRAPH}/me/drive/root:/{path}:/children", headers=headers)
```

### 下载文件内容
```python
resp = requests.get(f"{MS_GRAPH}/me/drive/items/{item_id}/content",
                    headers=headers, allow_redirects=True)
with open("local_file.docx", "wb") as f:
    f.write(resp.content)
```

### 上传小文件（< 4MB）
```python
with open("file.pdf", "rb") as f:
    data = f.read()
resp = requests.put(
    f"{MS_GRAPH}/me/drive/root:/目标路径/file.pdf:/content",
    headers={**headers, "Content-Type": "application/octet-stream"},
    data=data
)
item = resp.json()
print(item["webUrl"])  # 分享链接
```

### 上传大文件（>= 4MB，分块上传）
```python
# Step 1: 创建上传会话
session_resp = requests.post(
    f"{MS_GRAPH}/me/drive/root:/大文件.zip:/createUploadSession",
    headers=headers,
    json={"item": {"@microsoft.graph.conflictBehavior": "rename"}}
)
upload_url = session_resp.json()["uploadUrl"]

# Step 2: 分块上传（每块 10MB）
CHUNK_SIZE = 10 * 1024 * 1024
file_size = os.path.getsize("大文件.zip")
with open("大文件.zip", "rb") as f:
    offset = 0
    while chunk := f.read(CHUNK_SIZE):
        end = min(offset + len(chunk) - 1, file_size - 1)
        requests.put(upload_url, data=chunk, headers={
            "Content-Range": f"bytes {offset}-{end}/{file_size}",
            "Content-Length": str(len(chunk))
        })
        offset += len(chunk)
```

### 创建分享链接
```python
resp = requests.post(
    f"{MS_GRAPH}/me/drive/items/{item_id}/createLink",
    headers=headers,
    json={"type": "view", "scope": "organization"}  # 或 "anonymous"
)
link = resp.json()["link"]["webUrl"]
```

### 搜索文件
```python
resp = requests.get(f"{MS_GRAPH}/me/drive/root/search(q='关键词')", headers=headers)
```

### 删除文件（需用户确认）
```python
requests.delete(f"{MS_GRAPH}/me/drive/items/{item_id}", headers=headers)
# 返回 204 表示成功
```

## 输出格式建议
- 文件列表：📄/📁 名称 | 大小 | 最后修改时间
- 上传/下载完成：显示文件大小 + 在线查看链接（webUrl）
