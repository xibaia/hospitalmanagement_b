# 项目部署问题排查指南

本文档总结了在新环境部署 Hospital Management System 时常见的问题及解决方案。

## 环境要求

- Python 3.10+
- pip 24.0+
- Windows / Linux / macOS

---

## 常见问题

### 1. pip 安装依赖缓慢或超时

**现象：**
```
ReadTimeoutError: HTTPSConnectionPool(host='files.pythonhosted.org', port=443): Read timed out.
```

**原因：** 默认 PyPI 源在国外，网络连接不稳定。

**解决方案：** 使用国内镜像源

```bash
# 清华镜像
pip install -r requirement.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# 或阿里云镜像
pip install -r requirement.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

---

### 2. ModuleNotFoundError: No module named 'pkg_resources'

**现象：**
```
File "...\widget_tweaks\__init__.py", line 1, in <module>
    from pkg_resources import get_distribution, DistributionNotFound
ModuleNotFoundError: No module named 'pkg_resources'
```

**原因：**
- Python 3.12+ 默认不自带 `setuptools`
- `django-widget-tweaks 1.4.12` 依赖 `pkg_resources`
- `setuptools` 82.0.1+ 已移除 `pkg_resources`

**解决方案：** 升级 `django-widget-tweaks` 到 1.5+

```bash
pip install "django-widget-tweaks>=1.5" -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

**长期修复：** `requirement.txt` 中应更新为：
```
django-widget-tweaks>=1.5
```

---

### 3. RuntimeError: Freetype library not found

**现象：**
```
File "...\freetype\raw.py", line 52, in <module>
    raise RuntimeError('Freetype library not found')
RuntimeError: Freetype library not found
```

**原因：**
- `xhtml2pdf` → `reportlab` → `freetype-py` 依赖链
- `freetype-py` 在 Windows 上需要 `freetype.dll`
- 从 pip 安装的 `freetype-py` 不包含 DLL 文件

**影响范围：**
- 服务器可以正常启动
- 但 **PDF 生成功能**（出院账单打印）会报错

**解决方案：**

#### 方案 A：手动下载 freetype.dll（推荐）

1. 下载 FreeType Windows 库：https://github.com/ubawurinna/freetype-windows-binaries
2. 将 `freetype.dll` 放到项目根目录或 `C:\Windows\System32`
3. 重启服务器

#### 方案 B：使用 Conda 安装（自动处理依赖）

```bash
conda install -c conda-forge freetype-py
```

#### 方案 C：修改代码延迟加载（规避方案）

将 `hospital/views.py` 第 462 行的导入移到函数内部：

```python
# 原代码（模块级别导入）
from xhtml2pdf import pisa

# 修改为（函数内导入）
def render_to_pdf(template_src, context_dict):
    from xhtml2pdf import pisa  # 延迟导入
    ...
```

这样服务器可以启动，只有在使用 PDF 功能时才需要 freetype。

---

## 标准部署流程

```bash
# 1. 创建虚拟环境
python -m venv venv

# Windows 激活
venv\Scripts\activate

# Linux/Mac 激活
source venv/bin/activate

# 2. 安装依赖（使用国内镜像）
pip install -r requirement.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# 3. 升级 widget_tweaks（解决 pkg_resources 问题）
pip install "django-widget-tweaks>=1.5" -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# 4. 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 5. 创建管理员账户
python manage.py createsuperuser

# 6. 启动服务器
python manage.py runserver 0.0.0.0:8000
```

---

## 已知限制

| 功能 | 状态 | 说明 |
|------|------|------|
| Web 界面 | ✅ 正常 | 所有页面可正常访问 |
| API 接口 | ✅ 正常 | REST API 可正常使用 |
| 数据库 | ✅ 正常 | SQLite 无需额外配置 |
| PDF 生成 | ⚠️ 受限 | 需要 freetype.dll，仅影响出院账单打印 |

---

## 相关文件

- `requirement.txt` - Python 依赖列表
- `CLAUDE.md` - 项目架构说明
- `hospital/views.py:462` - PDF 生成代码位置
