# WebUI 自动化测试接入计划

## 目标

为当前 Django WebUI 接入一套可重复运行、维护成本可控的自动化测试流程，用于提交前快速发现核心交互回归。

第一版不追求覆盖所有页面细节，重点覆盖：

- 登录与角色跳转是否正常
- 权限型操作是否只能通过 POST 执行
- 医生、患者、管理员核心页面是否能正常打开
- 表单非法提交是否留在原页面
- 空头像、空负责人、重复预约等已知脆弱点是否不再崩溃
- 医生不能删除其他医生的预约

## 技术选型

- Django `TestCase`：继续覆盖权限、表单、数据库状态等服务端行为。
- Django `StaticLiveServerTestCase`：启动临时测试服务器，使用测试数据库。
- Playwright Python：驱动真实 Chromium 浏览器执行 WebUI 交互。
- Shell 脚本：提供一键运行入口。

暂不引入 Cypress、Selenium、pytest-django。先保持当前 Django 测试体系，降低接入成本。

## 预期目录结构

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

## 阶段 1：依赖与环境检查

- [ ] 检查 `.venv` 是否已安装 Playwright。
- [ ] 如未安装，在 `requirement.txt` 中增加 `playwright`。
- [ ] 确认 `django.contrib.staticfiles` 已启用，便于使用 `StaticLiveServerTestCase`。
- [ ] 执行一次浏览器运行时安装：

```bash
.venv/bin/python -m playwright install chromium
```

- [ ] 确认现有测试仍可运行：

```bash
.venv/bin/python manage.py test hospital.tests
```

验收标准：

- [ ] `manage.py test hospital.tests` 通过。
- [ ] Playwright 可以导入并启动 Chromium。
- [ ] `StaticLiveServerTestCase` 可以正常服务静态资源。

## 阶段 2：E2E 基础类

新增 `hospital/tests/e2e/base.py`。

计划能力：

- [ ] 继承 `StaticLiveServerTestCase`。
- [ ] 在 `setUpClass` 中启动 Playwright。
- [ ] 在 `tearDownClass` 中关闭浏览器和 Playwright。
- [ ] 每个测试创建独立 page。
- [ ] 提供 `goto(path)` 辅助方法。
- [ ] 提供 `login(login_path, username, password)` 辅助方法，显式传入 `adminlogin`、`doctorlogin`、`patientlogin` 对应路径。
- [ ] 提供 `assert_page_contains(text)` 辅助方法。
- [ ] 测试失败时保存截图到 `test-artifacts/screenshots/`。
- [ ] 将 `test-artifacts/` 加入 `.gitignore`，避免误提交调试截图。

注意：

- Chromium 默认使用 headless 模式。
- 页面跳转后等待 `networkidle` 或关键 selector 出现。
- 登录成功依赖当前项目的 `LOGIN_REDIRECT_URL='/afterlogin'`，再由 `afterlogin_view` 分发到角色 dashboard 或等待审批页。
- 登录表单优先使用 `input[name="username"]`、`input[name="password"]` 或 placeholder selector。
- 不依赖真实 `db.sqlite3`，全部数据由测试自己创建。

验收标准：

- [ ] 一个最小页面打开测试可以通过。
- [ ] 浏览器资源在测试结束后能正常释放。

## 阶段 3：测试数据复用

复用现有 `hospital/tests/helpers.py`。

第一版优先使用：

- [ ] `create_grouped_user`
- [ ] `create_doctor`
- [ ] `create_patient`
- [ ] `create_activity`
- [ ] `create_record`

如发现 E2E 数据准备重复，再考虑增加：

- [ ] `create_appointment`
- [ ] `create_admin`
- [ ] `create_station`

验收标准：

- [ ] E2E 测试不依赖手工创建账号。
- [ ] 每条测试能独立运行。

## 阶段 4：公共页面 Smoke 测试

新增 `hospital/tests/e2e/test_public_ui.py`。

覆盖：

- [ ] 首页 `/` 可打开。
- [ ] 管理员入口页面可打开。
- [ ] 医生入口页面可打开。
- [ ] 患者入口页面可打开。
- [ ] 关于页面可打开。
- [ ] 联系我们页面可打开。

验收标准：

- [ ] 页面响应为成功状态。
- [ ] 页面包含关键文本或关键入口链接。

## 阶段 5：登录与角色跳转测试

新增 `hospital/tests/e2e/test_auth_ui.py`。

覆盖：

- [ ] 管理员登录后进入管理员 dashboard。
- [ ] 已审核医生登录后进入医生 dashboard。
- [ ] 未审核医生登录后进入等待审批页。
- [ ] 已审核患者登录后进入患者 dashboard。
- [ ] 未审核患者登录后进入等待审批页。

验收标准：

- [ ] 登录表单可以通过浏览器真实填写和提交。
- [ ] 登录后的 URL 或页面关键文本正确。
- [ ] 未审核角色不能进入正式 dashboard。

## 阶段 6：医生端核心回归测试

新增 `hospital/tests/e2e/test_doctor_ui.py`。

覆盖：

- [ ] 医生 dashboard 可以打开。
- [ ] 医生预约列表可以打开。
- [ ] 同一患者的多条预约都显示，不被漏掉。
- [ ] 无头像患者在预约列表显示默认头像，不触发模板错误。
- [ ] 删除预约页面的删除按钮使用 POST 表单。
- [ ] 医生可以删除自己的预约。
- [ ] 医生不能删除其他医生的预约。该场景不是可见 UI 点击路径，应使用已登录浏览器上下文构造 POST，或保留在 Django `TestCase` 中验证服务端权限。

验收标准：

- [ ] 页面真实点击流程通过。
- [ ] 数据库中对应预约状态符合预期。
- [ ] 跨医生删除返回失败结果，目标预约仍存在。

## 阶段 7：管理员端核心回归测试

新增 `hospital/tests/e2e/test_admin_ui.py`。

覆盖：

- [ ] 管理员 dashboard 可以打开。
- [ ] 医生管理列表可以打开。
- [ ] 患者管理列表可以打开。
- [ ] 新增医生提交空表单后仍停留在新增医生页。
- [ ] 新增患者提交空表单后仍停留在新增患者页。
- [ ] 新增预约提交空表单后仍停留在新增预约页。
- [ ] 活动负责人为空时页面显示 `未指定`。
- [ ] 站点负责人为空时页面显示 `—`。
- [ ] 病历列表能展示医生模型姓名。

验收标准：

- [ ] 无效表单不会误跳转到列表页。
- [ ] 空值展示不触发模板错误。
- [ ] 管理员核心菜单链路可访问。

## 阶段 8：患者端核心回归测试

新增 `hospital/tests/e2e/test_patient_ui.py`。

覆盖：

- [ ] 患者 dashboard 可以打开。
- [ ] 患者医生列表可以打开。
- [ ] 患者预约页面可以打开。
- [ ] 患者提交空预约表单后仍停留在预约表单页。
- [ ] 患者预约成功后可以在预约列表看到记录。
- [ ] 患者病历入口可以打开。

验收标准：

- [ ] 患者核心页面无模板错误。
- [ ] 预约申请流程真实浏览器可走通。

## 阶段 9：一键运行脚本

新增 `scripts/check_webui.sh`。

第一版内容：

```bash
#!/usr/bin/env bash
set -euo pipefail

.venv/bin/python manage.py test hospital.tests
```

后续如 E2E 变慢，可拆分：

```text
scripts/check_unit.sh
scripts/check_e2e.sh
scripts/check_webui.sh
```

验收标准：

- [ ] `./scripts/check_webui.sh` 可执行。
- [ ] 脚本失败时返回非 0 exit code。
- [ ] 脚本通过时代表 Django 单元测试和 E2E 测试全部通过。
- [ ] `scripts/` 目录不存在时一并创建。

## 阶段 10：使用文档

新增 `docs/webui-testing.md`。

内容包括：

- [ ] 如何安装依赖。
- [ ] 如何安装 Playwright Chromium。
- [ ] 如何运行所有 WebUI 测试。
- [ ] 如何只运行 E2E 测试。
- [ ] 失败截图保存在哪里。
- [ ] 如何新增一个页面交互测试。
- [ ] 哪些内容适合写 E2E，哪些更适合写 Django TestCase。

验收标准：

- [ ] 新开发者按文档能独立跑通测试。
- [ ] 文档不依赖当前对话上下文。

## 阶段 11：稳定性与维护规则

第一版必须遵守：

- [ ] 优先使用稳定 selector：`get_by_role`、`get_by_text`、`get_by_placeholder`、表单 `name`。
- [ ] 图标按钮没有可访问名称时，使用稳定 CSS selector，例如 `form[action$="/delete-appointment/1"] button[type="submit"]`。
- [ ] 不做视觉截图 diff。
- [ ] 不测 CSS 细节。
- [ ] 不依赖真实数据库数据。
- [ ] 不依赖页面动画时间。
- [ ] 每条 E2E 测试只验证一个主要业务行为。
- [ ] 失败截图只作为调试材料，不纳入断言。

## 第一批落地用例清单

优先级 P0：

- [ ] 首页可打开。
- [ ] 管理员登录后进入 dashboard。
- [ ] 医生登录后进入 dashboard。
- [ ] 患者登录后进入 dashboard。
- [ ] 医生预约列表显示重复患者预约。
- [ ] 医生不能删除其他医生预约。

优先级 P1：

- [ ] 未审核医生进入等待页。
- [ ] 未审核患者进入等待页。
- [ ] 无头像患者在医生预约列表不崩。
- [ ] 管理员新增医生空表单不跳转。
- [ ] 管理员新增患者空表单不跳转。
- [ ] 患者预约空表单不跳转。

优先级 P2：

- [ ] 活动负责人为空显示 `未指定`。
- [ ] 站点负责人为空显示 `—`。
- [ ] 管理员病历列表医生名展示正确。
- [ ] 患者预约成功后能查看预约。

## 完成标准

本轮接入完成时，需要满足：

- [ ] Playwright 依赖已纳入项目依赖。
- [ ] `hospital/tests/e2e/` 基础架构已建立。
- [ ] `test-artifacts/` 已加入 `.gitignore`。
- [ ] 至少 6 条 P0 E2E 用例通过。
- [ ] `./scripts/check_webui.sh` 可一键运行。
- [ ] `docs/webui-testing.md` 已写明使用方法。
- [ ] 全量测试通过：

```bash
.venv/bin/python manage.py test hospital.tests
```

## 暂不做

- [ ] 不做截图视觉回归。
- [ ] 不引入 Cypress。
- [ ] 不引入 Selenium。
- [ ] 不迁移到 pytest。
- [ ] 不覆盖所有字段级 CRUD。
- [ ] 不把当前数据库当测试前置条件。

## 风险与应对

### Playwright 浏览器运行时缺失

应对：

```bash
.venv/bin/python -m playwright install chromium
```

### 选择器不稳定

应对：

- 优先使用表单字段 `name`。
- 优先使用按钮文本和链接文本。
- 必要时再给模板添加稳定 `data-testid`。

### E2E 运行速度变慢

应对：

- 单元测试和 E2E 脚本拆分。
- 提交前默认跑核心 smoke。
- 合并前再跑完整 WebUI 测试。

### 模板文案变动导致测试失败

应对：

- 断言业务关键文字，不断言装饰性文案。
- 优先断言 URL、表单存在、数据库状态。

## 执行顺序建议

1. 接入依赖。
2. 创建 E2E base。
3. 写首页 smoke 测试。
4. 写三类角色登录测试。
5. 写医生预约回归测试。
6. 写管理员空表单回归测试。
7. 写一键脚本。
8. 写使用文档。
9. 跑全量测试。
10. 修复测试暴露的问题。
11. 提交。
