# 技术栈现代化与维护性改造计划

> 创建时间：2026-06-22  
> 当前状态：阶段 0-4 已完成，准备进入阶段 5  
> 适用项目：医院管理系统 / 口腔筛查管理后端  
> 执行原则：先跑稳，再升级，再拆分；每个阶段都要可验证、可回滚。

---

## 1. 背景

当前项目是一个 Django 医院管理系统，包含 Django 模板页面、Django REST Framework API、SQLite/PostgreSQL 数据库配置、PDF 生成、医生/患者/管理员多角色业务。

当前识别到的主要技术栈：

| 类型 | 当前情况 |
|------|----------|
| Web 框架 | Django 4.2.11 |
| API 框架 | djangorestframework 3.14.0 |
| 配置管理 | python-decouple |
| 跨域 | django-cors-headers |
| 数据库 | 开发 SQLite，生产 PostgreSQL |
| PDF | xhtml2pdf |
| 前端 | Django templates + Bootstrap 静态资源 |
| 本地 Python | 当前 shell 为 Python 3.14.4，但未安装 Django |
| Docker Python | python:3.9-slim |

项目本身的技术选型是务实的，适合 CRUD 密集、权限清晰、后台管理较多的业务。但当前存在三个维护风险：

1. 运行环境没有统一，当前本机 Python 与 Docker Python 不一致。
2. Django/DRF 版本偏旧，后续维护应升级到仍在长期支持窗口内的版本。
3. `hospital/views.py` 与 `hospital/api_views.py` 体积较大，长期继续叠功能会降低可维护性。

---

## 2. 改造目标

### 2.1 目标

- 统一开发、测试、部署运行环境。
- 将 Django/DRF 升级到可长期维护的版本。
- 建立最小测试保护网，避免升级时引入回归。
- 拆分过大的视图文件，降低后续开发成本。
- 加强权限、配置、部署和文档完整性。

### 2.2 非目标

- 不重写整个项目。
- 不把 Django 模板页面迁移到 React/Vue。
- 不在第一轮引入复杂微服务或前后端分离架构。
- 不一次性改完所有历史遗留代码。

---

## 3. 目标技术栈

建议目标：

| 类型 | 目标版本/方案 |
|------|---------------|
| Python | 3.12 |
| Django | 5.2 LTS |
| DRF | 3.17.x |
| 数据库 | 开发 SQLite，生产 PostgreSQL |
| 生产服务 | gunicorn + nginx |
| 容器 | python:3.12-slim |

选择 Python 3.12 的原因：

- 足够新，维护周期较长。
- 相比 Python 3.14，对第三方依赖更稳妥。
- 与 Django 5.2 LTS 匹配度较高。
- 更适合包含 `xhtml2pdf`、`psycopg2-binary` 等依赖的传统 Django 项目。

---

## 4. 执行规则

每个阶段执行前后都需要做以下动作：

1. 确认 `git status --short`，避免覆盖非本次改动。
2. 每个阶段尽量单独提交，方便回滚。
3. 改依赖前先确认当前项目能否在标准环境中启动。
4. 每次升级依赖后必须执行：
   ```bash
   python manage.py check
   python manage.py test
   ```
5. 涉及数据库模型时必须执行：
   ```bash
   python manage.py makemigrations --check
   python manage.py migrate
   ```
6. 涉及页面时至少手动打开关键页面验证。
7. 涉及 API 时至少验证登录、鉴权和核心接口。

---

## 5. 阶段 0：建立安全基线

目标：先确认当前项目在标准环境里能跑起来，避免升级时新旧问题混在一起。

### 5.1 执行清单

| 状态 | 任务 |
|------|------|
| [x] | 新建维护分支：`chore/modernize-stack` |
| [x] | 备份 `db.sqlite3` |
| [x] | 记录当前依赖快照 |
| [x] | 使用 Python 3.12 创建虚拟环境 |
| [x] | 安装当前 `requirement.txt` |
| [x] | 执行 Django 系统检查 |
| [x] | 执行数据库迁移检查 |
| [x] | 启动本地服务 |
| [x] | 手动验证核心页面基础连通性 |
| [x] | 手动验证核心 API 基础连通性 |

### 5.2 建议命令

```bash
git checkout -b chore/modernize-stack
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d%H%M%S)
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirement.txt
pip freeze > requirements.lock.old.txt
python manage.py check
python manage.py migrate --check
python manage.py runserver
```

### 5.3 页面验证

| 页面 | URL | 预期 |
|------|-----|------|
| 首页 | `/` | 200 |
| 管理员登录 | `/adminlogin` | 200 |
| 医生登录 | `/doctorlogin` | 200 |
| 患者登录 | `/patientlogin` | 200 |
| 管理员仪表盘 | `/admin-dashboard` | 未登录跳转登录，登录后 200 |
| 医生仪表盘 | `/doctor-dashboard` | 未登录跳转登录，登录后 200 |
| 患者仪表盘 | `/patient-dashboard` | 未登录跳转登录，登录后 200 |

### 5.4 API 验证

| API | 预期 |
|-----|------|
| `POST /api/patient/login/` | 正确账号返回 token |
| `GET /api/patient/info/` | 未登录返回 401，携带 token 返回数据 |
| `GET /api/doctors/` | 返回已审批医生列表 |
| `GET /api/activities/` | 携带 token 返回活动列表 |
| `GET /api/patient/records/` | 患者只能看到自己的病历 |

### 5.5 验收标准

- 项目能在 Python 3.12 虚拟环境中启动。
- `python manage.py check` 通过。
- 核心页面和核心 API 的当前状态被记录。
- 当前遗留问题单独登记，不和升级问题混在一起。

### 5.6 执行记录（2026-06-22）

| 项目 | 结果 |
|------|------|
| 当前分支 | `chore/modernize-stack` |
| Python | 使用 `uv` 安装项目内 Python `3.12.13` |
| 虚拟环境 | `.venv` 创建成功 |
| 数据库备份 | `db.sqlite3.backup.20260622-stage0` |
| 依赖快照 | `requirements.lock.old.txt` |
| Django 检查 | `python manage.py check` 通过 |
| 迁移检查 | `python manage.py migrate --check` 通过 |
| Django 测试 | `python manage.py test` 可运行，但当前为 `0 tests` |
| 本地服务 | `python manage.py runserver 127.0.0.1:8000 --noreload` 可启动 |

#### 发现并处理的问题

| 问题 | 处理 |
|------|------|
| 本机只有 Python `3.14.4`，没有 `python3.12` | 使用 `uv python install 3.12 --install-dir .uv-python` 安装项目内 Python |
| `.venv` 中缺少 `pkg_resources`，导致 `django-widget-tweaks==1.4.12` 无法导入 | 在 `requirement.txt` 中新增 `setuptools==80.9.0` |
| `setuptools==82.0.1` 不再提供旧依赖需要的 `pkg_resources` | 固定到 `setuptools==80.9.0` |
| `pkg_resources` 已弃用 | 暂时通过 `setuptools<81` 过渡，后续升级或替换 `django-widget-tweaks` |
| 受限环境中 `runserver` 默认文件监听失败 | 使用 `--noreload`，并在授权环境下启动本地服务 |

#### Smoke Test 结果

| URL | 结果 |
|-----|------|
| `/` | 200 |
| `/adminlogin` | 200 |
| `/doctorlogin` | 200 |
| `/patientlogin` | 200 |
| `/api/doctors/` | 200 |
| `/admin-dashboard` | 302，未登录跳转 |
| `/doctor-dashboard` | 302，未登录跳转 |
| `/patient-dashboard` | 302，未登录跳转 |
| `/api/patient/info/` | 401，未认证拒绝访问 |

#### 尚未覆盖

- 没有找到可用默认账号密码，因此未验证登录后的管理员/医生/患者完整页面流程。
- 当前项目没有 Django 自动化测试，阶段 2 需要补最小测试保护网。

---

## 6. 阶段 1：环境标准化

目标：让本地、Docker、文档里的运行环境保持一致。

### 6.1 执行清单

| 状态 | 任务 |
|------|------|
| [x] | 新增 `.python-version`，固定为 `3.12` |
| [x] | 将 Dockerfile 基础镜像改为 `python:3.12-slim` |
| [x] | 整理依赖文件命名和内容 |
| [x] | 确认 `.env.example` 字段完整 |
| [x] | 确认 `.env` 不进入 Git |
| [x] | 更新 README 启动说明 |
| [x] | 增加标准启动和检查命令 |

### 6.2 依赖文件建议

短期可以保留 `requirement.txt`，减少改动范围。中期建议拆成：

```text
requirements/
  base.txt
  dev.txt
  prod.txt
```

第一轮建议先不拆，等升级完成后再拆，避免一次改太多。

### 6.3 验收标准

- README 中的命令可以从零启动项目。
- Docker 和本地虚拟环境使用同一大版本 Python。
- 新人不需要猜 Python 版本和依赖安装方式。

### 6.4 执行记录（2026-06-22）

| 项目 | 结果 |
|------|------|
| Python 版本文件 | 新增 `.python-version`，内容为 `3.12` |
| Docker | `Dockerfile` 基础镜像从 `python:3.9-slim` 改为 `python:3.12-slim` |
| 本地环境 | README 改为推荐 `.venv` + Python 3.12 |
| run.sh | 自动创建 `.venv`，优先使用 `python3.12`，找不到时尝试项目内 `.uv-python` |
| 依赖文件 | `requirement.txt` 补充 `setuptools==80.9.0` |
| 本地忽略规则 | `.gitignore` 忽略 `.uv-python/` 和 `db.sqlite3.backup.*`，允许跟踪 `.python-version` |
| 环境变量模板 | `.env.example` 补充 CORS、HTTPS、Email 配置 |
| CORS 配置 | `settings.py` 新增 `CORS_ALLOWED_ORIGINS` 环境变量读取 |

#### 验证结果

| 命令 | 结果 |
|------|------|
| `bash -n run.sh` | 通过 |
| `python manage.py check` | 通过 |
| `python manage.py migrate --check` | 通过 |

#### 后续注意

- README 中的 `uv` 命令适合没有系统 Python 3.12 的开发机。
- `run.sh` 会启动开发服务器，自动化检查时只做 `bash -n run.sh` 语法验证。
- `pkg_resources` 弃用警告仍存在，后续通过升级或替换 `django-widget-tweaks` 处理。

---

## 7. 阶段 2：补最小测试保护网

目标：升级依赖前先有测试兜底。

### 7.1 优先测试范围

| 状态 | 测试项 |
|------|--------|
| [x] | 患者注册成功 |
| [x] | 患者登录成功 |
| [x] | 错误密码登录失败 |
| [x] | 未认证访问受保护 API 返回 401 |
| [x] | 医生账号不能访问患者专属接口 |
| [x] | 患者账号不能访问医生专属接口 |
| [x] | 医生列表接口返回已审批医生 |
| [x] | 患者只能查看自己的病历 |
| [x] | 医生只能查看自己负责或相关的患者病历 |
| [x] | 活动报名成功 |
| [x] | 重复报名返回业务错误，不返回 500 |
| [x] | 取消活动报名成功 |

### 7.2 建议文件结构

```text
hospital/tests/
  __init__.py
  test_auth_api.py
  test_patient_api.py
  test_doctor_api.py
  test_activity_api.py
  test_medical_record_api.py
```

### 7.3 验收标准

- `python manage.py test` 可以稳定运行。
- 每个核心角色至少有一组认证和权限测试。
- 升级前所有新增测试通过。

### 7.4 执行记录（2026-06-22）

新增测试文件：

```text
hospital/tests/
  __init__.py
  helpers.py
  test_auth_api.py
  test_directory_api.py
  test_activity_api.py
  test_medical_record_api.py
```

覆盖范围：

| 范围 | 覆盖点 |
|------|--------|
| 患者认证 | 注册、登录、错误密码、未认证访问患者信息 |
| 医生认证 | 医生登录、患者 token 访问医生接口被拒绝 |
| 角色隔离 | 医生 token 访问患者信息不返回患者数据 |
| 医生目录 | 只返回已审批医生 |
| 活动 | 患者报名强制 volunteer、医生可报名 doctor、重复报名返回 400、取消报名成功 |
| 病历 | 患者只能看到自己的病历，医生只能看到自己的病历 |

验证结果：

```bash
python manage.py test
```

结果：`13 tests` 全部通过。

---

## 8. 阶段 3：依赖升级

目标：逐步升级 Django/DRF，降低一次跨版本升级风险。

### 8.1 升级路径

第一步：升级到 Django 4.2 最新补丁版和较新的 DRF。

```text
Django==4.2.x
djangorestframework==3.15.x
```

第二步：升级到目标版本。

```text
Django==5.2.x
djangorestframework==3.17.x
```

### 8.2 执行清单

| 状态 | 任务 |
|------|------|
| [x] | 升级到 Django 4.2 最新补丁版 |
| [x] | 升级到 DRF 3.15.x |
| [x] | 执行 `python manage.py check` |
| [x] | 执行 `python manage.py test` |
| [x] | 手动验证页面和 API |
| [x] | 升级到 Django 5.2.x |
| [x] | 升级到 DRF 3.17.x |
| [x] | 处理兼容性错误 |
| [x] | 再次执行完整验证 |

### 8.3 重点检查点

| 检查点 | 原因 |
|--------|------|
| URL 路由 | Django 升级可能暴露旧写法问题 |
| 登录/登出 | `LoginView`、`LogoutView` 行为需要手动验证 |
| CSRF | 表单页面和 POST 操作依赖 CSRF |
| DRF Token | 小程序/API 登录依赖 token |
| 分页 | 当前已有“分页配置不生效”的待修问题 |
| 文件上传 | 医生/患者头像涉及 media |
| PDF 生成 | `xhtml2pdf` 兼容性和中文渲染需要验证 |
| CORS | 小程序跨域依赖 CORS 设置 |

### 8.4 验收标准

- 项目运行在 Python 3.12。
- Django 升级到 5.2 LTS。
- DRF 升级到 3.17.x。
- 测试通过。
- 核心页面和核心 API 验证通过。
- 发现的兼容性问题已记录或修复。

### 8.5 执行记录（2026-06-22）

#### 版本变更

| 依赖 | 旧版本 | 过渡版本 | 目标版本 |
|------|--------|----------|----------|
| Django | `4.2.11` | `4.2.30` | `5.2.15` |
| djangorestframework | `3.14.0` | `3.15.2` | `3.17.1` |
| django-widget-tweaks | `1.4.12` | `1.5.1` | `1.5.1` |
| setuptools | 临时 `80.9.0` | 已移除 | 已移除 |

#### 过渡升级验证

| 命令 | 结果 |
|------|------|
| `python manage.py check` | 通过 |
| `python manage.py test` | `13 tests` 全部通过 |
| `python manage.py migrate --check` | 首次发现 `authtoken.0004_alter_tokenproxy_options` 未应用 |
| `python manage.py migrate` | 已应用 `authtoken.0004_alter_tokenproxy_options` |
| `python manage.py migrate --check` | 通过 |

#### 目标升级验证

| 命令 | 结果 |
|------|------|
| `python manage.py check` | 通过 |
| `python manage.py migrate --check` | 通过 |
| `python manage.py test` | `13 tests` 全部通过 |
| `python -m pip check` | 通过，无 broken requirements |

#### HTTP Smoke Test

| URL | 结果 |
|-----|------|
| `/` | 200 |
| `/adminlogin` | 200 |
| `/doctorlogin` | 200 |
| `/patientlogin` | 200 |
| `/api/doctors/` | 200 |
| `/admin-dashboard` | 302，未登录跳转 |
| `/doctor-dashboard` | 302，未登录跳转 |
| `/patient-dashboard` | 302，未登录跳转 |
| `/api/patient/info/` | 401，未认证拒绝访问 |

#### 兼容性处理

- DRF 3.15+ 带来 `authtoken.0004_alter_tokenproxy_options`，已应用迁移。
- `django-widget-tweaks` 升到 `1.5.1` 后不再触发 `pkg_resources` 警告。
- 阶段 0 临时加入的 `setuptools==80.9.0` 已从 `requirement.txt` 移除，并从当前虚拟环境卸载后验证通过。

---

## 9. 阶段 4：处理已知待修问题

目标：在升级稳定后，处理当前进度文档中仍标记为待修的问题。

来自 `PROGRESS.md` 的待修项：

| 状态 | 编号 | 问题 |
|------|------|------|
| [x] | M1 | `PatientInfoSerializer` N+1 查询 |
| [x] | M3 | `doctor_update_record_api` 缺所有权校验 |
| [x] | M4 | 多处 `get()` 缺 404 保护 |
| [x] | M5 | `MedicalRecordCreateSerializer` patient 无所有权校验 |
| [x] | M6 | 分页配置不生效 |
| [x] | L1 | PDF 中文乱码 |
| [x] | L2 | `symptoms/address required=False` 未设 |
| [x] | L4 | `ToothFinding.tooth_number` 无范围校验 |

### 9.1 验收标准

- 每个待修问题都有对应代码修复。
- 中危问题优先补测试。
- `PROGRESS.md` 状态同步更新。

### 9.2 执行记录（2026-06-22）

代码修复：

| 问题 | 处理 |
|------|------|
| `PatientInfoSerializer` 查询分配医生名 | 增加 `assigned_doctor_map` context，调用方使用 `select_related('user')` 并预取医生映射 |
| 医生病历创建/更新所有权 | `MedicalRecordCreateSerializer` 接收当前医生 context，只允许给分配给自己的患者或已有自己病历记录的患者创建；更新时禁止修改病历所属患者 |
| API `get()` 404 风险 | 复核 API 中 `get()` 调用，现有路径均有 404/权限响应；新增所有权测试覆盖医生病历路径 |
| 分页配置不生效 | 新增 `_paginated_response`，接入医生列表、患者病历、活动列表、我的活动、医生患者列表、医生病历列表、站点列表 |
| PDF 中文乱码 | `render_to_pdf` 编码从 `ISO-8859-1` 改为 `UTF-8`，并传入 `encoding='UTF-8'` |
| `symptoms/address required=False` | `PatientUpdateSerializer` 已确认设置 `required=False` |
| 牙位范围校验 | `ToothFindingWriteSerializer.validate_tooth_number` 限制合法 FDI 编码：11-18、21-28、31-38、41-48 |

新增/扩展测试：

| 测试 | 覆盖 |
|------|------|
| `test_doctors_list_uses_page_size` | 验证分页返回 `count` 且默认每页 20 条 |
| `test_doctor_can_create_record_for_assigned_patient` | 医生可为分配给自己的患者创建病历 |
| `test_doctor_cannot_create_record_for_unrelated_patient` | 医生不能为无关患者创建病历 |
| `test_doctor_cannot_change_record_patient_on_update` | 医生更新病历时不能修改所属患者 |
| `test_doctor_record_rejects_invalid_tooth_number` | 非法牙位编码返回 400 |

验证结果：

```bash
python manage.py check
python manage.py migrate --check
python manage.py test
python -m pip check
```

结果：`18 tests` 全部通过，无 broken requirements。

---

## 10. 阶段 5：代码结构拆分

目标：拆分超大视图文件，让后续维护更轻。

### 10.1 建议结构

```text
hospital/
  views/
    __init__.py
    public.py
    admin.py
    doctor.py
    patient.py
    activity.py
    medical_record.py
  api/
    __init__.py
    patient.py
    doctor.py
    activity.py
    medical_record.py
    station.py
  services/
    patient_service.py
    doctor_service.py
    activity_service.py
    medical_record_service.py
  selectors/
    patient_selector.py
    doctor_selector.py
    activity_selector.py
```

### 10.2 拆分顺序

| 状态 | 任务 |
|------|------|
| [ ] | 先拆 `api_views.py` 中的患者 API |
| [ ] | 拆医生 API |
| [ ] | 拆活动 API |
| [ ] | 拆病历 API |
| [ ] | 拆站点 API |
| [ ] | 再拆 `views.py` 中的 public/admin/doctor/patient 页面 |
| [ ] | 将重复查询逻辑放入 `selectors/` |
| [ ] | 将有副作用的业务操作放入 `services/` |

### 10.3 拆分规则

- 每次只移动一个业务域。
- 优先保持函数名和 URL 不变。
- 拆分提交中尽量不改业务逻辑。
- 每拆一块就跑测试。
- URL import 改动要小心，避免循环导入。

### 10.4 验收标准

- 原有 URL 不变化。
- 核心页面和 API 行为不变化。
- `views.py` 和 `api_views.py` 体积明显下降。
- 新模块边界能从文件名直接看懂。

---

## 11. 阶段 6：权限与安全加固

目标：让多角色系统的权限边界更清楚。

### 11.1 执行清单

| 状态 | 任务 |
|------|------|
| [ ] | 统一角色判断函数或权限类 |
| [ ] | 新增 `IsPatient` 权限 |
| [ ] | 新增 `IsDoctor` 权限 |
| [ ] | 新增 `IsRecordOwnerOrDoctor` 权限 |
| [ ] | 检查患者只能看自己的病历 |
| [ ] | 检查医生只能看自己负责/相关的病历 |
| [ ] | 检查管理员页面全部需要管理员权限 |
| [ ] | 检查敏感字段是否泄露 |
| [ ] | 检查生产安全配置 |

### 11.2 生产安全配置检查

| 配置 | 预期 |
|------|------|
| `DEBUG` | 生产为 `False` |
| `ALLOWED_HOSTS` | 生产配置明确域名/IP |
| `CSRF_TRUSTED_ORIGINS` | 生产配置可信域名 |
| `SESSION_COOKIE_SECURE` | HTTPS 下为 `True` |
| `CSRF_COOKIE_SECURE` | HTTPS 下为 `True` |
| `SECURE_SSL_REDIRECT` | HTTPS 下为 `True` |
| `CORS_ALLOW_ALL_ORIGINS` | 生产为 `False` |

### 11.3 验收标准

- 权限逻辑集中、可复用。
- 高风险接口有测试覆盖。
- 病历、手机号、身份证号等敏感数据不会越权暴露。

---

## 12. 阶段 7：部署改造

目标：让生产部署方式更接近真实环境。

### 12.1 执行清单

| 状态 | 任务 |
|------|------|
| [ ] | Dockerfile 使用 Python 3.12 |
| [ ] | 生产启动从 `runserver` 改为 `gunicorn` |
| [ ] | docker-compose 增加 PostgreSQL 服务 |
| [ ] | 增加 `collectstatic` 流程 |
| [ ] | 明确 media 文件处理方式 |
| [ ] | 增加健康检查 |
| [ ] | 增加部署文档 |

### 12.2 建议生产命令

```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn hospitalmanagement.wsgi:application --bind 0.0.0.0:8000
```

### 12.3 验收标准

- Docker 环境可以启动项目。
- PostgreSQL 环境可以迁移并运行。
- 静态文件和上传文件处理方式明确。
- README 或部署文档可以指导生产部署。

---

## 13. 阶段 8：文档收尾

目标：让项目后续能被自己或其他开发者顺利接手。

### 13.1 文档清单

| 状态 | 文档 | 说明 |
|------|------|------|
| [ ] | `README.md` | 启动、测试、部署入口 |
| [ ] | `API_Documentation.md` | API 认证、参数、响应示例 |
| [ ] | `docs/architecture.md` | 模块结构说明 |
| [ ] | `docs/permissions.md` | 角色权限表 |
| [ ] | `docs/deployment.md` | 部署步骤 |
| [ ] | `docs/upgrade-notes.md` | 升级过程和兼容性记录 |
| [ ] | `PROGRESS.md` | 已知问题修复状态同步 |

### 13.2 验收标准

- 文档与真实代码一致。
- 新人能按 README 启动项目。
- 维护者能从文档知道权限、接口、部署方式。

---

## 14. 风险与回滚

| 风险 | 级别 | 处理方式 |
|------|------|----------|
| Django 5.2 兼容性问题 | HIGH | 分两步升级，保留可回滚提交 |
| xhtml2pdf 在新 Python 下异常 | HIGH | 单独验证 PDF，必要时固定兼容版本 |
| 权限修复影响现有用户流程 | HIGH | 增加角色测试，手动验证三端流程 |
| 视图拆分引入循环导入 | MEDIUM | 每次只拆一个业务域 |
| Docker/PostgreSQL 改造影响本地开发 | MEDIUM | 保留 SQLite 开发配置 |
| 文档与代码不同步 | MEDIUM | 每阶段结束同步更新文档 |

回滚策略：

1. 每个阶段独立提交。
2. 数据库迁移前备份 `db.sqlite3`。
3. 依赖升级前保留旧依赖快照。
4. 大范围拆分前先确保测试通过。
5. 如果升级失败，优先回退依赖文件和锁定版本，不做混合状态修补。

---

## 15. 第一轮建议执行范围

第一轮只做最有性价比的部分：

| 顺序 | 阶段 | 目标 |
|------|------|------|
| 1 | 阶段 0 | 建立当前可运行基线 |
| 2 | 阶段 1 | 标准化 Python/Docker/README |
| 3 | 阶段 2 | 补最小 API 测试保护网 |
| 4 | 阶段 3 | 升级到 Django 5.2 LTS + DRF 3.17.x |

第一轮完成后再进入：

| 顺序 | 阶段 | 目标 |
|------|------|------|
| 5 | 阶段 4 | 修复现存待修问题 |
| 6 | 阶段 5 | 拆分视图结构 |
| 7 | 阶段 6 | 权限与安全加固 |
| 8 | 阶段 7 | 部署改造 |
| 9 | 阶段 8 | 文档收尾 |

---

## 16. 当前下一步

从这里开始执行：

1. 确认是否已有虚拟环境或 Python 3.12。
2. 创建 `chore/modernize-stack` 分支。
3. 备份数据库。
4. 创建 Python 3.12 虚拟环境。
5. 安装当前依赖。
6. 跑通 `python manage.py check`。
7. 记录基线结果。

执行完阶段 0 后，再决定是先补测试，还是先解决当前环境里的依赖兼容问题。
