# 升级与兼容性记录

> 更新时间：2026-06-22

## 版本变化

| 项目 | 升级前 | 升级后 |
|------|--------|--------|
| Python | Docker `3.9-slim` / 本地未统一 | `3.12` |
| Django | `4.2.11` | `5.2.15` |
| DRF | `3.14.0` | `3.17.1` |
| django-widget-tweaks | `1.4.12` | `1.5.1` |
| 生产服务 | `runserver` 风格 | `gunicorn` |
| 容器数据库 | 未编排 | PostgreSQL 16 alpine |

## 主要改造

1. 建立 Python 3.12 虚拟环境和 `.python-version`。
2. 新增 API 测试保护网，当前 18 个测试通过。
3. 升级 Django 到 5.2 LTS，DRF 到 3.17.1。
4. 修复分页、病历所有权、牙位校验、PDF UTF-8、N+1 查询等问题。
5. 拆分 `hospital/api_views.py` 到 `hospital/api/`。
6. 拆分 `hospital/views.py` 到 `hospital/views/`。
7. 新增 `hospital/selectors/` 和 `hospital/services/`，承接查询与副作用操作。
8. 新增 `IsPatient`、`IsDoctor`、`IsRecordOwnerOrDoctor` 权限类。
9. Docker 改为 Python 3.12 + Gunicorn。
10. Compose 增加 PostgreSQL、静态/媒体 volume 和健康检查。

## 兼容性处理

| 问题 | 处理 |
|------|------|
| 本机缺 Python 3.12 | 使用 `uv` 安装项目内 Python，并固定 `.python-version` |
| `django-widget-tweaks==1.4.12` 依赖旧 `pkg_resources` | 升级到 `1.5.1`，移除临时 `setuptools` 固定 |
| DRF authtoken 新迁移 | 执行 `authtoken.0004_alter_tokenproxy_options` |
| DRF 分页配置没有统一响应 | 新增 `paginated_response`，列表接口返回 `count/next/previous` |
| PDF 中文乱码 | `xhtml2pdf` 输入编码改为 UTF-8 |
| Compose 中密钥/数据库密码含 `$` 的插值警告 | `env_file` 使用 raw 模式，文档补充检查方式 |

## 验证记录

最终验证命令：

```bash
python manage.py check
python manage.py migrate --check
python manage.py test
python -m pip check
python manage.py collectstatic --noinput --dry-run
COMPOSE_DISABLE_ENV_FILE=1 docker compose config
```

当前结果：

- Django system check 通过。
- 迁移检查通过。
- `18 tests` 全部通过。
- `pip check` 无 broken requirements。
- Compose 配置可解析。

## 后续建议

- 继续把历史页面视图中的复杂查询逐步迁移到 selectors。
- 如果 API 规模继续扩大，优先把 function-based view 迁移到 class-based view 或 ViewSet，再接入对象级权限类。
- 生产部署前补 Nginx、HTTPS、日志轮转和备份策略。
