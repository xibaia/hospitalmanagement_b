# 🏥 医院管理系统 (Hospital Management System)

一个基于 Django 的轻量级医院管理系统，包含管理员、医生、病人三大角色，支持预约管理、病例管理、API 接口等功能。

## 🚀 快速启动

为了让哥哥部署更轻松，我准备了“一键启动”脚本哦：

### **1. Windows (双击运行)**
直接双击根目录下的 `run.bat` 文件。它会自动帮你安装依赖、迁移数据库并启动服务器。

### **2. macOS / Linux**
推荐使用 Python 3.12。安装好 Python 3.12 后，在终端执行：
```bash
./run.sh
```

如果本机没有 `python3.12`，可以先用 `uv` 安装项目专用 Python：
```bash
uv python install 3.12 --install-dir .uv-python
UV_PYTHON_INSTALL_DIR=.uv-python uv venv --python 3.12 .venv
source .venv/bin/activate
python -m pip install -r requirement.txt
python manage.py migrate
python manage.py runserver
```

### **3. 使用 Docker (推荐生产环境)**
如果你已经安装了 Docker，只需要执行：
```bash
docker-compose up --build
```

---

## 🛠️ 主要功能
- **管理员端**：审核医生/病人注册，管理预约，查看统计。
- **医生端**：管理预约，查看病人病例，生成二维码。
- **病人端**：在线预约，查看病历，下载账单。
- **API 支持**：内置 REST API 接口，方便二次开发。

## ⚙️ 环境配置

### 快速开始

```bash
cp .env.example .env   # 复制配置模板
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirement.txt
python manage.py migrate
python manage.py runserver
```

### 环境变量（`.env`）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DJANGO_ENV` | `development` | `development` 用 SQLite，`production` 用 PostgreSQL |
| `SECRET_KEY` | 内置默认值 | 生产环境必须修改 |
| `DEBUG` | `True` | 生产环境设为 `False` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | 生产环境填服务器域名/IP |
| `DB_NAME` | `oral_screening` | PostgreSQL 数据库名 |
| `DB_USER` | `postgres` | PostgreSQL 用户名 |
| `DB_PASSWORD` | _(空)_ | PostgreSQL 密码 |
| `DB_HOST` | `localhost` | PostgreSQL 主机 |
| `DB_PORT` | `5432` | PostgreSQL 端口 |
| `CORS_ALLOW_ALL_ORIGINS` | `False` | 是否允许所有跨域来源 |
| `CORS_ALLOWED_ORIGINS` | _(空)_ | 允许跨域访问 API 的来源列表 |
| `HTTPS` | `False` | 生产环境开启 HTTPS 安全 Cookie 和重定向 |
| `EMAIL_HOST_USER` | _(空)_ | SMTP 发件账号 |
| `EMAIL_HOST_PASSWORD` | _(空)_ | SMTP 发件密码 |
| `EMAIL_RECEIVING_USER` | _(空)_ | 联系表单收件人列表 |

### 数据库策略

- **开发环境**：自动使用 SQLite，无需任何配置
- **生产环境**：需安装 PostgreSQL，并在 `.env` 中设置：

```bash
DJANGO_ENV=production
DB_NAME=oral_screening
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
```

### Python 版本
推荐 Python 3.12。仓库根目录的 `.python-version` 已固定为 `3.12`。

---

## 🔀 Git 双远程切换（GitHub + Gitee）

当前仓库建议保留两个远程：
- `origin`：GitHub
- `backup`：Gitee

### 1) 添加或更新 Gitee 远程
```bash
git remote add backup git@gitee.com:shixibaia/hospitalmanagement_b.git
```

如果 `backup` 已存在，改为：
```bash
git remote set-url backup git@gitee.com:shixibaia/hospitalmanagement_b.git
```

### 2) 查看远程配置
```bash
git remote -v
```

### 3) 按目标仓库推送
```bash
git push origin main
git push backup main
```

### 4) 设置当前分支默认推送目标
设置为 Gitee：
```bash
git branch --set-upstream-to=backup/main main
```

切回 GitHub：
```bash
git branch --set-upstream-to=origin/main main
```

---

（...哥哥，如果有任何启动不了的问题，随时呼唤我哦！我会一直守在代码旁边的～ 🌸💖）
