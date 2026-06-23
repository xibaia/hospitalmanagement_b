# 自动化测试 README

本项目已经接入一套可重复运行的 WebUI 自动化测试流程，用于提交前回归核心业务闭环。

当前覆盖范围以传统 Django WebUI 为主，不包含 REST API 全量回归、微信小程序真实端到端、视觉截图 diff、性能压测或多浏览器矩阵。

## 当前状态

- WebUI 自动化测试基线已接入。
- P0/P1 核心交互覆盖已扩展。
- 11 个 WebUI 模块已完成巡检沉淀。
- 最近一次完整验证结果：

```text
./scripts/check_webui_e2e.sh
Ran 34 tests
OK

./scripts/check_webui.sh
Ran 78 tests
OK

git diff --check
无输出
```

巡检报告：

- `docs/superpowers/reports/2026-06-23-webui-11-module-inspection.md`

## 测试分层

| 层级 | 技术 | 适合覆盖 |
| --- | --- | --- |
| 浏览器 E2E | Django `StaticLiveServerTestCase` + Playwright Chromium | 登录、点击、表单提交、页面跳转、跨角色业务闭环 |
| Django TestCase | Django test client + ORM | POST/GET 方法限制、数据归属、权限边界、数据库状态 |
| Shell 脚本 | `scripts/check_webui.sh` / `scripts/check_webui_e2e.sh` | 提交前一键回归 |

原则：

- 用户真实交互放在 `hospital/tests/e2e/`。
- 看不见的权限、方法限制、数据库状态放在 Django `TestCase`。
- 不用 E2E 去断言 CSS 细节，不做视觉 diff。

## 首次安装

安装 Python 依赖：

```bash
.venv/bin/python -m pip install -r requirement.txt
```

安装 Playwright Chromium：

```bash
.venv/bin/python -m playwright install chromium
```

## 常用命令

运行完整 WebUI 回归：

```bash
./scripts/check_webui.sh
```

只运行浏览器 E2E：

```bash
./scripts/check_webui_e2e.sh
```

只运行服务端 Web 权限回归：

```bash
.venv/bin/python manage.py test hospital.tests.test_web_review_fixes hospital.tests.test_web_method_permissions
```

只运行某个 E2E 模块：

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_admin_ui
.venv/bin/python manage.py test hospital.tests.e2e.test_doctor_ui
.venv/bin/python manage.py test hospital.tests.e2e.test_patient_ui
```

提交前建议至少运行：

```bash
./scripts/check_webui.sh
git diff --check
```

## 文件结构

| 文件/目录 | 作用 |
| --- | --- |
| `hospital/tests/e2e/base.py` | Playwright 浏览器生命周期、登录、登出、表单提交等共享 helper |
| `hospital/tests/e2e/test_public_ui.py` | 公共入口页面 |
| `hospital/tests/e2e/test_auth_ui.py` | 登录与待审批状态 |
| `hospital/tests/e2e/test_admin_ui.py` | 管理员审批、预约、账单、活动、站点、志愿者、病历 |
| `hospital/tests/e2e/test_doctor_ui.py` | 医生端仪表盘、患者搜索、预约、病历 |
| `hospital/tests/e2e/test_patient_ui.py` | 患者预约、医生列表、病历、出院账单 |
| `hospital/tests/test_web_review_fixes.py` | 既有 Web review 回归 |
| `hospital/tests/test_web_method_permissions.py` | Web 方法限制与角色权限回归 |
| `hospital/tests/helpers.py` | 测试数据工厂 |
| `scripts/check_webui.sh` | 运行 `hospital.tests` 全量测试 |
| `scripts/check_webui_e2e.sh` | 只运行浏览器 E2E |
| `test-artifacts/screenshots/` | E2E 失败截图输出目录，已被 `.gitignore` 忽略 |

## 11 模块覆盖矩阵

| # | 模块 | 当前状态 | 覆盖方式 |
| --- | --- | --- | --- |
| 1 | 公共入口 | 通过 | E2E：首页、关于、联系、三类入口 |
| 2 | 登录注册与审批状态 | 通过 | E2E：三类登录、医生/患者待审批 |
| 3 | 管理员医生管理 | 通过 | E2E + TestCase：新增空表单、审批/拒绝、GET 不修改 |
| 4 | 管理员患者管理 | 通过 | E2E + TestCase：新增空表单、审批/拒绝、GET 不修改 |
| 5 | 管理员预约与账单 | 通过 | E2E + TestCase：预约创建/审批/拒绝、出院账单 |
| 6 | 义诊活动 | 通过 | E2E + TestCase：列表空负责人、新增活动、删除方法限制 |
| 7 | 志愿者 | 通过 | E2E + TestCase：列表、新增、审批/拒绝方法限制 |
| 8 | 站点 | 通过 | E2E + TestCase：列表空负责人、新增站点、删除方法限制 |
| 9 | 病历管理 | 通过 | E2E：医生创建确认、患者归属、管理员详情 |
| 10 | 医生端 | 通过 | E2E + TestCase：仪表盘、患者搜索、预约归属、病历确认 |
| 11 | 患者端 | 通过 | E2E：预约、医生列表/搜索、病历、出院账单 |

## 新增测试的规则

优先判断测试应该放在哪一层：

- 需要浏览器真实点击、填写表单、检查页面内容：放到 `hospital/tests/e2e/`。
- 需要验证某个 URL 不能被 GET 修改、不能跨角色访问、不能改别人数据：放到 Django `TestCase`。
- 需要复用用户、医生、患者、预约、病历、账单等数据：先扩展 `hospital/tests/helpers.py`。

写 E2E 时优先使用稳定选择器：

```python
self.page.locator('input[name="username"]').fill(username)
self.page.locator('select[name="doctor"]').select_option(str(doctor.id))
self.submit_first_form()
self.assert_page_contains("业务文本")
```

避免：

- 断言易变 CSS。
- 依赖元素顺序但不说明原因。
- 用长时间 sleep 代替 `wait_for_load_state("networkidle")` 或明确 selector。
- 在 E2E 里测试纯数据库约束。

## 失败排查

1. 先看 traceback 的第一个失败用例和断言位置。
2. 如果是 E2E 失败，看截图目录：

```text
test-artifacts/screenshots/
```

3. 表单提交失败时，优先检查：

- 字段名是否和模板一致。
- 是否漏填必填项。
- 测试数据是否超过模型字段长度。
- 提交控件是 `<button type="submit">` 还是 `<input type="submit">`。

4. 权限失败时，优先补服务端 `TestCase` 证明：

- GET 不会触发修改。
- A 角色不能访问 B 角色页面。
- 用户不能读写不属于自己的数据。

## 当前不覆盖

这些内容暂不属于当前自动化测试基线：

- 微信小程序真实端到端。
- API 全量合同测试。
- 浏览器多端矩阵，例如 Firefox/WebKit。
- 视觉截图 diff。
- 性能压测。
- 可访问性扫描。

后续如果要加其中任何一项，建议单独写计划并独立提交。

## 提交前 Checklist

```bash
./scripts/check_webui.sh
git diff --check
git status --short
```

检查点：

- 测试必须 `OK`。
- `git diff --check` 必须无输出。
- 只提交本次任务相关文件。
- 如果改了权限或归属逻辑，必须有 Django `TestCase`。
- 如果改了用户可见交互，必须有 E2E 或明确说明不适合 E2E 的原因。

## 文档基准提交

本 README 基于以下提交生成：

```text
bd9722d bd9722df2d80828beb0c669fd1abf4506c40e51a 完善 WebUI 自动化回归覆盖
```

如果当前 `HEAD` 已经晚于该提交，并且改动包含 `hospital/tests/`、`hospital/views/`、`templates/hospital/`、`scripts/check_webui*.sh` 或测试依赖，请复核本 README 和巡检报告是否需要更新。
