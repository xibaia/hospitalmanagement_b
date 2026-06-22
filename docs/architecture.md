# 项目架构说明

> 更新时间：2026-06-22
> 适用版本：Python 3.12 / Django 5.2 LTS / DRF 3.17

## 总体形态

本项目是一个 Django 单体应用，同时提供 Django 模板页面和 Django REST Framework API。

| 层级 | 目录/文件 | 职责 |
|------|-----------|------|
| 项目配置 | `hospitalmanagement/` | settings、根路由、WSGI |
| 业务应用 | `hospital/` | 模型、表单、序列化器、页面视图、API |
| 页面视图 | `hospital/views/` | 管理员、医生、患者和公共页面 |
| API 视图 | `hospital/api/` | 患者端、医生端、活动、病历、目录、站点接口 |
| 查询封装 | `hospital/selectors/` | 可复用查询和可见范围筛选 |
| 业务操作 | `hospital/services/` | 有副作用的业务动作 |
| 文档 | `docs/` | 架构、权限、部署、升级计划 |

## 请求入口

页面请求：

```text
hospitalmanagement/urls.py
  -> from hospital import views
  -> hospital/views/__init__.py
  -> hospital/views/*.py
```

API 请求：

```text
hospitalmanagement/urls.py
  -> include('hospital.api_urls')
  -> hospital/api_urls.py
  -> hospital/api_views.py
  -> hospital/api/*.py
```

`hospital/api_views.py` 现在是兼容导出层，用于保持 `hospital/api_urls.py` 的导入方式不变。后续如果愿意继续清理，可以让 `api_urls.py` 直接从 `hospital.api` 或具体模块导入。

## API 模块边界

| 模块 | 主要接口 |
|------|----------|
| `hospital/api/patient.py` | 患者注册、登录、登出、个人信息、绑定医生、既往病史 |
| `hospital/api/doctor.py` | 医生登录、登出、患者列表、患者详情 |
| `hospital/api/medical_record.py` | 患者病历、医生病历、创建/更新/确认病历 |
| `hospital/api/activity.py` | 活动列表、详情、报名、取消、我的活动 |
| `hospital/api/directory.py` | 医生目录 |
| `hospital/api/station.py` | 义诊站点 |
| `hospital/api/permissions.py` | `IsPatient`、`IsDoctor`、`IsRecordOwnerOrDoctor` |
| `hospital/api/common.py` | 分页响应、角色辅助、活动 annotate、医生装饰器 |

## 页面模块边界

| 模块 | 主要职责 |
|------|----------|
| `hospital/views/public.py` | 首页、说明页、注册、登录后分流 |
| `hospital/views/admin.py` | 管理员仪表盘、审核、活动、站点、PDF、病历管理 |
| `hospital/views/doctor.py` | 医生仪表盘、患者、预约、二维码、病历 |
| `hospital/views/patient.py` | 患者仪表盘、预约、医生搜索、出院/病历查看 |
| `hospital/views/common.py` | 页面端角色判断辅助 |

`hospital/views/__init__.py` 继续导出原函数名，所以根路由不需要大范围重写。

## 查询与业务操作

新增的查询封装集中在：

- `hospital/selectors/patient.py`
- `hospital/selectors/medical_record.py`

新增的业务操作封装集中在：

- `hospital/services/activity.py`

当前原则是：API 层负责认证、权限、HTTP 状态码和响应结构；selectors 负责查询边界；services 负责会修改数据的业务动作。

## 部署结构

生产容器由 `docker-compose.yml` 编排：

```text
web: Django + Gunicorn
db: PostgreSQL 16
volumes:
  postgres_data
  static_volume
  media_volume
```

Web 容器启动时执行：

```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn hospitalmanagement.wsgi:application --bind 0.0.0.0:8000
```

## 测试保护网

当前测试位于 `hospital/tests/`，覆盖：

- 患者/医生登录与角色隔离
- 患者与医生病历可见范围
- 医生目录分页
- 活动列表、活动详情、报名、重复报名、取消报名
- 医生病历创建、更新和牙位校验

维护建议：后续每新增一个角色边界或病历相关接口，都优先补一条权限测试。
