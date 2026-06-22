# 权限与安全说明

> 更新时间：2026-06-22

## 角色模型

系统主要有三类用户：

| 角色 | Django group | 业务模型 | 说明 |
|------|--------------|----------|------|
| 管理员 | `is_staff` / `is_superuser` | Django User | 管理后台页面、审核医生和患者 |
| 医生 | `DOCTOR` | `Doctor` | 医生端页面和医生 API |
| 患者 | `PATIENT` | `Patient` | 患者端页面和患者 API |

患者和医生都需要对应业务模型 `status=True`，才会被 API 权限类视为已审批账户。

## API 权限类

| 权限类 | 文件 | 用途 |
|--------|------|------|
| `IsPatient` | `hospital/api/permissions.py` | 只允许已登录、已审批患者访问 |
| `IsDoctor` | `hospital/api/permissions.py` | 只允许已登录、已审批医生访问 |
| `IsRecordOwnerOrDoctor` | `hospital/api/permissions.py` | 面向对象级病历权限，供后续 class-based API 复用 |

当前 API 仍以 function-based view 为主，因此病历对象级权限主要通过查询条件保证。

## 患者 API 边界

| 接口范围 | 权限 |
|----------|------|
| 注册、登录 | `AllowAny` |
| 患者信息、更新、登出 | `IsAuthenticated + IsPatient` |
| 绑定医生 | `IsAuthenticated + IsPatient` |
| 既往病史 | `IsAuthenticated + IsPatient` |
| 患者病历列表/详情 | `IsAuthenticated + IsPatient`，查询限定为当前患者 |

医生 token 访问患者专属接口时返回 403。

## 医生 API 边界

| 接口范围 | 权限 |
|----------|------|
| 医生登录 | `AllowAny` |
| 医生登出 | `IsAuthenticated + IsDoctor` |
| 医生患者列表 | `IsAuthenticated + IsDoctor`，仅返回分配给当前医生的患者 |
| 医生患者详情 | `IsAuthenticated + IsDoctor`，仅允许查看分配给自己或已有自己病历的患者 |
| 医生病历列表/详情/更新/确认 | `IsAuthenticated + IsDoctor`，查询限定为当前医生病历 |

患者 token 访问医生专属接口时返回 403。

## 活动与目录接口

| 接口 | 规则 |
|------|------|
| `GET /api/doctors/` | 公开，只返回已审批医生 |
| `GET /api/activities/` | 登录用户可访问；患者只看 active 活动，医生可看全部 |
| `POST /api/activities/<pk>/join/` | 登录用户可报名；非医生传 `doctor` 会被降级为 `volunteer` |
| `DELETE /api/activities/<pk>/leave/` | 登录用户只能取消自己的报名 |
| `GET /api/stations/` | 登录用户可访问，只返回启用站点 |

## 页面权限

页面端仍沿用 Django 登录状态和角色判断：

- 管理员页面需要管理员身份。
- 医生页面需要医生身份。
- 患者页面需要患者身份。
- 删除、审批等敏感操作已加 POST 限制，避免 GET 触发写操作。

## 生产安全配置

`.env` 中需要重点配置：

| 配置 | 生产建议 |
|------|----------|
| `SECRET_KEY` | 必须替换为强随机值 |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | 明确域名/IP |
| `CORS_ALLOW_ALL_ORIGINS` | `False` |
| `CORS_ALLOWED_ORIGINS` | 只配置可信前端来源 |
| `HTTPS` | 有 HTTPS 代理时设为 `True` |
| `CSRF_TRUSTED_ORIGINS` | 配置可信 HTTPS 域名 |
| `SECURE_HSTS_SECONDS` | HTTPS 稳定后再开启 |

## 测试覆盖

当前权限相关测试覆盖：

- 未认证访问患者信息返回 401
- 医生 token 访问患者信息返回 403
- 患者 token 访问医生接口返回 403
- 患者只能查看自己的病历
- 医生只能查看/创建/更新自己负责范围内的病历
