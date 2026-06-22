# WebUI 自动化测试设计

## 背景

当前项目是 Django 服务端渲染的医院管理系统，已有测试主要集中在 `hospital/tests/` 下的 Django/DRF 测试。最近 Web 审查修复了多类容易回归的问题，包括医生预约删除权限、预约列表患者错配、无效表单回显、可选头像和空负责人展示。

接下来需要接入一套可重复运行的 WebUI 自动化测试流程，用于提交前快速发现核心交互回归。第一版范围限定为 P0 + P1，不覆盖所有页面细节。

## 目标

第一版自动化测试需要做到：

- 能通过一个稳定命令重复运行。
- 能真实驱动浏览器访问 Django 页面。
- 覆盖首页、三类登录、审批状态跳转、医生预约列表、无头像、空表单回显等核心 WebUI 风险点。
- 继续保留 Django `TestCase` 对权限和数据库状态的强验证。
- 为后续 11 个 WebUI 模块巡检提供扩展路径。

## 非目标

第一版不做：

- 视觉截图对比。
- CSS 样式断言。
- 全字段、全路径 CRUD 覆盖。
- 全量点击每个按钮。
- Cypress、Selenium、pytest 迁移。
- 依赖真实 `db.sqlite3` 或手工准备账号。

## 推荐方案

采用 **Django 原生测试 + Playwright Python** 的双层结构：

- Django `TestCase`：负责服务端行为、权限、POST 限制、数据库状态。
- Django `StaticLiveServerTestCase`：为 E2E 测试启动测试服务器和测试数据库。
- Playwright Python：驱动 headless Chromium 真实访问页面、填写表单、点击按钮、验证 DOM。
- Shell 脚本：提供一键运行入口。

这个方案与当前 Django 模板项目匹配，不需要引入 Node 测试栈，也能复用现有测试数据 helper。

## 架构分层

### Django TestCase 层

继续使用现有 `hospital/tests/` 测试方式。该层负责：

- 权限判断。
- GET 不能执行删除/审批。
- POST 后数据库状态变化。
- 医生不能删除其他医生预约。
- 表单非法提交后响应模板正确。

跨医生删除预约这类安全规则优先放在 Django `TestCase` 层，因为它是服务端权限约束，不依赖可见 UI 点击路径。

### Playwright E2E 层

新增 `hospital/tests/e2e/`。该层负责：

- 页面真实打开。
- 登录表单真实填写和提交。
- 登录后跳转到 dashboard 或等待审批页。
- 列表内容真实渲染。
- 表单空提交仍停留原页。
- 删除按钮真实以 POST form 存在。
- 无头像等模板边界能正常显示。

E2E 层只验证关键交互，不承载所有业务规则。

## 目录结构

新增结构：

```text
hospital/tests/e2e/
  __init__.py
  base.py
  test_public_ui.py
  test_auth_ui.py
  test_doctor_ui.py
  test_admin_ui.py
  test_patient_ui.py

scripts/
  check_webui.sh

docs/
  webui-testing.md
```

同时更新：

```text
requirement.txt
.gitignore
```

## E2E 基础类设计

在 `hospital/tests/e2e/base.py` 中新增 `WebUITestCase`。

职责：

- 继承 `StaticLiveServerTestCase`。
- 在 `setUpClass` 启动 Playwright 和 Chromium。
- 在 `tearDownClass` 关闭 browser 和 Playwright。
- 在 `setUp` 创建独立 page。
- 在 `tearDown` 关闭 page。
- 失败时保存截图。

建议辅助方法：

```text
goto(path)
login(login_path, username, password)
assert_page_contains(text)
screenshot_on_failure()
```

`login` 显式接收登录路径：

```text
login("/adminlogin", username, password)
login("/doctorlogin", username, password)
login("/patientlogin", username, password)
```

原因是项目当前有三个独立登录入口，但字段结构一致：

```text
input[name="username"]
input[name="password"]
button[type="submit"]
```

登录成功后依赖当前配置 `LOGIN_REDIRECT_URL='/afterlogin'`，再由 `afterlogin_view` 分发到对应 dashboard 或等待审批页。

## 测试数据策略

复用现有 `hospital/tests/helpers.py`：

- `create_grouped_user`
- `create_doctor`
- `create_patient`
- `create_activity`
- `create_record`

第一版可以直接在测试里创建 `models.Appointment`。如果预约创建逻辑重复，再新增：

```text
create_appointment(patient, doctor, description, status=True)
```

数据准备规则：

- 每条测试自己创建需要的数据。
- 不依赖真实数据库。
- 不依赖手工创建账号。
- `e2e/base.py` 不负责创建业务数据，避免基础类混入业务职责。

## P0 用例设计

### 首页可打开

文件：`test_public_ui.py`

步骤：

- 访问 `/`。
- 等待页面加载。
- 断言页面包含关键入口或首页关键文本。

### 管理员登录后进入 dashboard

文件：`test_auth_ui.py`

步骤：

- 使用 `create_grouped_user(username, "ADMIN")` 创建管理员。
- 访问 `/adminlogin`。
- 填写用户名和密码。
- 提交表单。
- 断言 URL 或页面内容显示管理员 dashboard。

### 已审核医生登录后进入 dashboard

文件：`test_auth_ui.py`

步骤：

- 使用 `create_doctor(status=True)` 创建医生。
- 访问 `/doctorlogin`。
- 填写并提交登录表单。
- 断言进入 `/doctor-dashboard` 或显示医生 dashboard 关键内容。

### 已审核患者登录后进入 dashboard

文件：`test_auth_ui.py`

步骤：

- 使用 `create_patient(status=True)` 创建患者。
- 访问 `/patientlogin`。
- 填写并提交登录表单。
- 断言进入 `/patient-dashboard` 或显示患者 dashboard 关键内容。

### 医生预约列表显示同一患者多条预约

文件：`test_doctor_ui.py`

步骤：

- 创建医生。
- 创建患者。
- 为同一患者创建两条已审核预约。
- 医生登录。
- 访问 `/doctor-view-appointment`。
- 断言两条预约描述都显示。

### 医生不能删除其他医生预约

主验证文件：现有 `hospital/tests/test_web_review_fixes.py` 中的 Django Web 测试。

步骤：

- 创建医生 A、医生 B。
- 为医生 B 创建预约。
- 用医生 A 登录。
- POST `/delete-appointment/<医生B预约ID>`。
- 断言返回失败，且预约仍存在。

可选 E2E 补充：

- 医生 A 登录访问 `/doctor-delete-appointment`。
- 断言页面不显示医生 B 的预约描述。

第一阶段不需要重复实现一条浏览器构造跨医生 POST 的 E2E；服务端权限由 Django `TestCase` 保持覆盖即可。

## P1 用例设计

### 未审核医生进入等待审批页

文件：`test_auth_ui.py`

步骤：

- 创建 `status=False` 医生。
- 登录 `/doctorlogin`。
- 断言显示 `doctor_wait_for_approval` 页面关键内容。

### 未审核患者进入等待审批页

文件：`test_auth_ui.py`

步骤：

- 创建 `status=False` 患者。
- 登录 `/patientlogin`。
- 断言显示 `patient_wait_for_approval` 页面关键内容。

### 无头像患者在医生预约列表不崩

文件：`test_doctor_ui.py`

步骤：

- 创建无头像患者。
- 创建该患者预约。
- 医生登录并访问 `/doctor-view-appointment`。
- 断言页面显示预约内容，并显示默认头像 alt 文本或默认头像元素。

### 管理员新增医生空表单不跳转

文件：`test_admin_ui.py`

步骤：

- 创建管理员并登录。
- 访问 `/admin-add-doctor`。
- 直接提交空表单。
- 断言仍在新增医生页，并且没有新增医生。

### 管理员新增患者空表单不跳转

文件：`test_admin_ui.py`

步骤：

- 创建管理员并登录。
- 访问 `/admin-add-patient`。
- 直接提交空表单。
- 断言仍在新增患者页，并且没有新增患者。

### 患者预约空表单不跳转

文件：`test_patient_ui.py`

步骤：

- 创建患者并登录。
- 访问 `/patient-book-appointment`。
- 直接提交空表单。
- 断言仍在预约表单页，并且没有新增预约。

## 选择器策略

优先级从高到低：

1. 表单字段 `name`

```text
input[name="username"]
input[name="password"]
```

2. placeholder

```text
get_by_placeholder("Username")
get_by_placeholder("Password")
```

3. 业务文本

```text
get_by_text("Admin Login Page")
get_by_text("Your Appointments")
```

4. 有明确名称的 role

```text
get_by_role("button", name="Login")
```

5. 稳定 CSS selector

图标按钮没有可访问名称时使用，例如：

```text
form[action*="/delete-appointment/"] button[type="submit"]
```

6. 必要时增加 `data-testid`

只在现有 DOM 无法稳定定位时添加，不提前铺满所有模板。

## 断言策略

优先断言：

- URL 路径。
- 页面稳定模块标题。
- 业务数据文本，例如预约描述。
- 表单是否仍存在。
- 数据库对象是否存在或被删除。

避免断言：

- 装饰性文案。
- CSS 样式。
- 精确布局。
- 截图像素。

## 依赖与运行

新增依赖：

```text
playwright
```

首次安装浏览器运行时：

```bash
.venv/bin/python -m playwright install chromium
```

新增一键脚本：

```text
scripts/check_webui.sh
```

第一版内容：

```bash
#!/usr/bin/env bash
set -euo pipefail

.venv/bin/python manage.py test hospital.tests
```

只跑 E2E：

```bash
.venv/bin/python manage.py test hospital.tests.e2e
```

只跑普通 Web 回归：

```bash
.venv/bin/python manage.py test hospital.tests.test_web_review_fixes
```

## 失败截图

失败截图保存到：

```text
test-artifacts/screenshots/
```

命名建议：

```text
<test-class>.<test-method>.png
```

`.gitignore` 增加：

```text
test-artifacts/
```

截图保存失败时不能覆盖原始测试失败原因。

## 后续扩展路线

### 第二阶段：P2 扩展

增加：

- 活动负责人为空显示 `未指定`。
- 站点负责人为空显示 `—`。
- 管理员病历列表医生名展示正确。
- 患者预约成功后能在预约列表看到记录。

### 第三阶段：11 模块巡检沉淀

逐步覆盖：

1. 公共入口。
2. 登录注册与审批状态。
3. 管理员医生管理。
4. 管理员患者管理。
5. 管理员预约与账单。
6. 义诊活动。
7. 志愿者。
8. 站点。
9. 病历管理。
10. 医生端。
11. 患者端。

每个模块选最关键的 1-3 条交互，不做穷举。

### 第四阶段：稳定性增强

在 E2E 用例增多后再考虑：

- 拆分 `check_unit.sh` 和 `check_e2e.sh`。
- 给复杂页面补 `data-testid`。
- 失败时输出当前 URL、页面标题、截图路径。
- 标记慢测试。
- 可选接入 CI。

## 完成标准

第一阶段完成时应满足：

- `playwright` 已加入项目依赖。
- `hospital/tests/e2e/` 基础结构已建立。
- P0 + P1 用例已实现或明确归属到 Django `TestCase`。
- `test-artifacts/` 已加入 `.gitignore`。
- `scripts/check_webui.sh` 可一键运行。
- `docs/webui-testing.md` 已写明使用方式。
- 全量测试通过：

```bash
.venv/bin/python manage.py test hospital.tests
```

## 实施顺序

1. 接入 Playwright 依赖。
2. 创建 `hospital/tests/e2e/`。
3. 创建 `WebUITestCase`。
4. 实现首页 smoke 测试。
5. 实现三类登录和未审核等待页测试。
6. 实现医生预约列表相关测试。
7. 实现管理员空表单测试。
8. 实现患者空预约表单测试。
9. 增加一键运行脚本。
10. 增加使用文档。
11. 运行全量测试并修复暴露问题。
