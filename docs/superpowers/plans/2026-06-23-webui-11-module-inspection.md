# WebUI 11 Module Inspection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 使用已接入的 Django + Playwright WebUI 自动化流程，对 11 个 WebUI 模块做一次可复跑的交互巡检，并沉淀结果报告。

**Architecture:** 巡检不直接扩大功能范围，先用现有 E2E 和 Django TestCase 覆盖核心路径，再按模块记录人工/自动化观察结果。发现问题先进入报告的 Findings；只有用户确认修复时再开独立修复任务。

**Tech Stack:** Django `TestCase`, Django `StaticLiveServerTestCase`, Playwright Python, existing `scripts/check_webui.sh`, existing `scripts/check_webui_e2e.sh`, Markdown report.

---

## File Structure

- Create: `docs/superpowers/reports/2026-06-23-webui-11-module-inspection.md`
  - 记录 11 个模块的巡检路径、验证命令、结果、问题和后续建议。
- Modify: `docs/superpowers/plans/2026-06-23-webui-11-module-inspection.md`
  - 执行过程中勾选步骤，保持计划状态可信。
- No code changes by default.
  - 如果巡检发现 P1/P2 问题，先记录到报告，不在本计划内直接修复。

---

## Module Map

| # | 模块 | 核心页面/路由 | 现有自动化入口 |
| --- | --- | --- | --- |
| 1 | 公共入口 | `/`, `/aboutus`, `/contactus`, `/adminclick`, `/doctorclick`, `/patientclick` | `hospital.tests.e2e.test_public_ui` |
| 2 | 登录注册与审批状态 | `/adminlogin`, `/doctorlogin`, `/patientlogin`, pending approval pages | `hospital.tests.e2e.test_auth_ui` |
| 3 | 管理员医生管理 | `/admin-doctor`, `/admin-view-doctor`, `/admin-add-doctor`, `/admin-approve-doctor` | `hospital.tests.e2e.test_admin_ui` |
| 4 | 管理员患者管理 | `/admin-patient`, `/admin-view-patient`, `/admin-add-patient`, `/admin-approve-patient` | `hospital.tests.e2e.test_admin_ui` |
| 5 | 管理员预约与账单 | `/admin-appointment`, `/admin-add-appointment`, `/admin-approve-appointment`, `/admin-discharge-patient` | `hospital.tests.e2e.test_admin_ui` |
| 6 | 义诊活动 | `/admin-activity`, `/admin-add-activity`, `/admin-view-activity/<id>` | `hospital.tests.e2e.test_admin_ui` |
| 7 | 志愿者 | `/admin-volunteer`, `/admin-add-volunteer` | `hospital.tests.e2e.test_admin_ui`, `hospital.tests.test_web_method_permissions` |
| 8 | 站点 | `/admin-station`, `/admin-add-station` | `hospital.tests.e2e.test_admin_ui`, `hospital.tests.test_web_method_permissions` |
| 9 | 病历管理 | `/admin-medical-records`, `/doctor-records`, `/doctor-create-record`, `/patient-records` | `hospital.tests.e2e.test_admin_ui`, `hospital.tests.e2e.test_doctor_ui`, `hospital.tests.e2e.test_patient_ui` |
| 10 | 医生端 | `/doctor-dashboard`, `/doctor-view-patient`, `/doctor-view-appointment`, `/doctor-delete-appointment` | `hospital.tests.e2e.test_doctor_ui` |
| 11 | 患者端 | `/patient-dashboard`, `/patient-book-appointment`, `/patient-view-appointment`, `/patient-view-doctor`, `/patient-discharge` | `hospital.tests.e2e.test_patient_ui` |

---

### Task 1: Create Inspection Report Skeleton

**Files:**
- Create: `docs/superpowers/reports/2026-06-23-webui-11-module-inspection.md`
- Modify: `docs/superpowers/plans/2026-06-23-webui-11-module-inspection.md`

- [x] **Step 1: Create report directory**

Run:

```bash
mkdir -p docs/superpowers/reports
```

Expected:

```text
docs/superpowers/reports exists
```

Verify with:

```bash
test -d docs/superpowers/reports && echo "docs/superpowers/reports exists"
```

- [x] **Step 2: Create report skeleton**

Create `docs/superpowers/reports/2026-06-23-webui-11-module-inspection.md` with:

```markdown
# WebUI 11 模块交互巡检报告

日期：2026-06-23
分支：chore/modernize-stack
范围：传统 Django WebUI，不包含 REST API、微信小程序真实端、视觉截图 diff、性能压测。

## 验证命令

| 命令 | 结果 |
| --- | --- |
| `./scripts/check_webui_e2e.sh` | 待执行 |
| `./scripts/check_webui.sh` | 待执行 |
| `git diff --check` | 待执行 |

## 模块结果

| # | 模块 | 状态 | 覆盖方式 | 备注 |
| --- | --- | --- | --- | --- |
| 1 | 公共入口 | 待检查 | E2E | 首页、关于、联系、三类入口 |
| 2 | 登录注册与审批状态 | 待检查 | E2E | 三类登录、医生/患者待审批 |
| 3 | 管理员医生管理 | 待检查 | E2E | 新增空表单、审批/拒绝、列表相关 |
| 4 | 管理员患者管理 | 待检查 | E2E | 新增空表单、审批/拒绝、列表相关 |
| 5 | 管理员预约与账单 | 待检查 | E2E | 创建/审批/拒绝预约、出院账单 |
| 6 | 义诊活动 | 待检查 | E2E | 列表空负责人、新增活动 |
| 7 | 志愿者 | 待检查 | E2E + TestCase | 列表、新增、GET 不修改 |
| 8 | 站点 | 待检查 | E2E + TestCase | 列表空负责人、新增、GET 不修改 |
| 9 | 病历管理 | 待检查 | E2E | 医生创建确认、患者/管理员查看 |
| 10 | 医生端 | 待检查 | E2E + TestCase | 仪表盘、患者搜索、预约删除、权限归属 |
| 11 | 患者端 | 待检查 | E2E | 预约、医生列表、病历、出院账单 |

## Findings

当前无。

## Deferred Coverage

当前无。
```

- [x] **Step 3: Mark Task 1 complete**

Update this plan by changing Task 1 checkboxes to `[x]`.

---

### Task 2: Run Baseline Automated Verification

**Files:**
- Modify: `docs/superpowers/reports/2026-06-23-webui-11-module-inspection.md`
- Modify: `docs/superpowers/plans/2026-06-23-webui-11-module-inspection.md`

- [x] **Step 1: Run E2E-only suite**

Run:

```bash
./scripts/check_webui_e2e.sh
```

Expected:

```text
OK
```

Record exact test count and result in the report.

- [x] **Step 2: Run full WebUI suite**

Run:

```bash
./scripts/check_webui.sh
```

Expected:

```text
OK
```

Record exact test count and result in the report.

- [x] **Step 3: Run whitespace check**

Run:

```bash
git diff --check
```

Expected: no output.

Record result in the report.

- [x] **Step 4: Mark Task 2 complete**

Update this plan by changing Task 2 checkboxes to `[x]`.

---

### Task 3: Inspect Modules 1-2 Public And Auth

**Files:**
- Modify: `docs/superpowers/reports/2026-06-23-webui-11-module-inspection.md`
- Modify: `docs/superpowers/plans/2026-06-23-webui-11-module-inspection.md`

- [x] **Step 1: Run public module E2E**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_public_ui
```

Expected:

```text
Ran 2 tests
OK
```

- [x] **Step 2: Run auth module E2E**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_auth_ui
```

Expected:

```text
Ran 5 tests
OK
```

- [x] **Step 3: Update report rows for modules 1-2**

Set modules 1 and 2 to `通过`; note the exact commands and counts in the module remarks.

- [x] **Step 4: Mark Task 3 complete**

Update this plan by changing Task 3 checkboxes to `[x]`.

---

### Task 4: Inspect Modules 3-8 Admin Management Areas

**Files:**
- Modify: `docs/superpowers/reports/2026-06-23-webui-11-module-inspection.md`
- Modify: `docs/superpowers/plans/2026-06-23-webui-11-module-inspection.md`

- [x] **Step 1: Run admin E2E suite**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_admin_ui
```

Expected:

```text
Ran 14 tests
OK
```

- [x] **Step 2: Run server-side Web method permission suite**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.test_web_method_permissions
```

Expected:

```text
Ran 3 tests
OK
```

- [x] **Step 3: Update report rows for modules 3-8**

Set modules 3, 4, 5, 6, 7, and 8 to `通过` if both commands pass. In remarks, include that destructive GET routes are covered by `hospital.tests.test_web_method_permissions`.

- [x] **Step 4: Mark Task 4 complete**

Update this plan by changing Task 4 checkboxes to `[x]`.

---

### Task 5: Inspect Modules 9-11 Records, Doctor, And Patient Areas

**Files:**
- Modify: `docs/superpowers/reports/2026-06-23-webui-11-module-inspection.md`
- Modify: `docs/superpowers/plans/2026-06-23-webui-11-module-inspection.md`

- [x] **Step 1: Run doctor E2E suite**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_doctor_ui
```

Expected:

```text
Ran 7 tests
OK
```

- [x] **Step 2: Run patient E2E suite**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_patient_ui
```

Expected:

```text
Ran 6 tests
OK
```

- [x] **Step 3: Run admin record detail coverage**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_admin_ui.AdminWebUITests.test_admin_can_view_medical_record_detail
```

Expected:

```text
Ran 1 test
OK
```

- [x] **Step 4: Update report rows for modules 9-11**

Set modules 9, 10, and 11 to `通过` if all commands pass. In remarks, list record ownership checks and doctor appointment ownership checks.

- [x] **Step 5: Mark Task 5 complete**

Update this plan by changing Task 5 checkboxes to `[x]`.

---

### Task 6: Finalize Inspection Report

**Files:**
- Modify: `docs/superpowers/reports/2026-06-23-webui-11-module-inspection.md`
- Modify: `docs/superpowers/plans/2026-06-23-webui-11-module-inspection.md`

- [x] **Step 1: Run final full suite**

Run:

```bash
./scripts/check_webui.sh
```

Expected:

```text
Ran 78 tests
OK
```

If test count changes because new inspection-only tests were added, record the new exact count.

- [x] **Step 2: Run final status checks**

Run:

```bash
git diff --check
git status --short
```

Expected: no output from `git diff --check`; `git status --short` lists only the new plan/report files unless confirmed fixes were made.

- [x] **Step 3: Fill final report summary**

Add:

```markdown
## Summary

- 11 个 WebUI 模块已完成自动化巡检。
- 本轮未发现阻断级交互问题。
- 后续如果要继续增强，可按 Deferred Coverage 中的条目单独开计划。
```

If any finding exists, replace “未发现阻断级交互问题” with the actual severity summary.

- [x] **Step 4: Mark Task 6 complete**

Update this plan by changing Task 6 checkboxes to `[x]`.

- [x] **Step 5: Stop before commit**

Do not commit unless the user explicitly asks. Report changed files, verification commands, and findings.

---

## Self-Review

- Spec coverage: covers the third-phase 11 modules listed in `docs/superpowers/specs/2026-06-22-webui-automation-testing-design.md`.
- Scope check: this plan performs inspection and reporting only; it does not silently expand features or fix bugs.
- Verification: every module maps to an existing Django/Playwright command.
- Deferred by design: visual diff, performance, accessibility scanning, multi-browser matrix, and Mini Program real-device E2E.
