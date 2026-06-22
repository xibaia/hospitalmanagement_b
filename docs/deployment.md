# 部署说明

> 更新时间：2026-06-22

## 环境要求

- Python 3.12
- Django 5.2 LTS
- PostgreSQL 16（生产推荐）
- Docker Compose v2（容器部署）

## 本地开发启动

```bash
cp .env.example .env
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirement.txt
python manage.py migrate
python manage.py runserver
```

开发环境默认 `DJANGO_ENV=development`，数据库使用 SQLite。

## Docker Compose 部署

1. 准备配置：

```bash
cp .env.example .env
```

2. 修改 `.env`：

```bash
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=replace-with-a-strong-secret
ALLOWED_HOSTS=your-domain.com,127.0.0.1
DB_NAME=oral_screening
DB_USER=postgres
DB_PASSWORD=replace-with-a-strong-password
DB_HOST=db
DB_PORT=5432
```

3. 启动：

```bash
docker compose up --build
```

Web 容器启动流程：

```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn hospitalmanagement.wsgi:application --bind 0.0.0.0:8000
```

## 静态文件和上传文件

| 类型 | Django 配置 | Compose volume | 说明 |
|------|-------------|----------------|------|
| 静态文件 | `STATIC_ROOT=staticfiles` | `static_volume` | `collectstatic` 输出 |
| 上传文件 | `MEDIA_ROOT=media` | `media_volume` | 用户头像、二维码等上传文件 |
| 数据库 | PostgreSQL data dir | `postgres_data` | 生产数据 |

生产环境建议在 Gunicorn 前增加 Nginx，由 Nginx 负责静态文件、媒体文件和 HTTPS 终止。

## 健康检查

`docker-compose.yml` 已配置：

- PostgreSQL：`pg_isready`
- Web：访问 `http://127.0.0.1:8000/`

Web 服务会等待数据库健康后再启动迁移和 Gunicorn。

## 手动 Gunicorn 启动

非 Docker 环境可使用：

```bash
source .venv/bin/activate
export DJANGO_ENV=production
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn hospitalmanagement.wsgi:application --bind 0.0.0.0:8000
```

## 验证命令

```bash
python manage.py check
python manage.py migrate --check
python manage.py test
python -m pip check
python manage.py collectstatic --noinput --dry-run
COMPOSE_DISABLE_ENV_FILE=1 docker compose config
```

## `.env` 与 `$` 字符

Docker Compose 会自动读取项目根目录 `.env` 做变量插值。如果 `SECRET_KEY` 含 `$`，`docker compose config` 可能提示未设置变量。

当前 compose 已用 raw 模式把 `.env` 传给容器，避免容器内密钥被错误展开。做配置语法检查时，推荐使用：

```bash
COMPOSE_DISABLE_ENV_FILE=1 docker compose config
```

## 生产注意事项

- `DEBUG=False`
- `ALLOWED_HOSTS` 不要使用 `*`
- `SECRET_KEY` 不要复用示例值
- `CORS_ALLOW_ALL_ORIGINS=False`
- 使用 HTTPS 后再设置 `HTTPS=True`
- 确认 `media_volume` 和数据库有备份策略
