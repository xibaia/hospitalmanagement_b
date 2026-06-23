# WebUI 11 模块交互巡检报告

日期：2026-06-23
分支：chore/modernize-stack
范围：传统 Django WebUI，不包含 REST API、微信小程序真实端、视觉截图 diff、性能压测。

## Summary

- 11 个 WebUI 模块已完成自动化巡检。
- 本轮未发现阻断级交互问题。
- 最终完整回归 `./scripts/check_webui.sh` 通过，Ran 78 tests，OK。
- 后续如果继续增强，建议单独开计划处理 Deferred Coverage。

## 验证命令

| 命令 | 结果 |
| --- | --- |
| `./scripts/check_webui_e2e.sh` | 通过，Ran 34 tests，OK |
| `./scripts/check_webui.sh` | 通过，基线和最终验证均 Ran 78 tests，OK |
| `git diff --check` | 通过，无输出 |

## 模块结果

| # | 模块 | 状态 | 覆盖方式 | 备注 |
| --- | --- | --- | --- | --- |
| 1 | 公共入口 | 通过 | E2E | `hospital.tests.e2e.test_public_ui`，Ran 2 tests，OK；覆盖首页、关于、联系、三类入口 |
| 2 | 登录注册与审批状态 | 通过 | E2E | `hospital.tests.e2e.test_auth_ui`，Ran 5 tests，OK；覆盖三类登录、医生/患者待审批 |
| 3 | 管理员医生管理 | 通过 | E2E + TestCase | `test_admin_ui` 覆盖新增空表单、医生审批/拒绝；`test_web_method_permissions` 覆盖 GET 不修改 |
| 4 | 管理员患者管理 | 通过 | E2E + TestCase | `test_admin_ui` 覆盖新增空表单、患者审批/拒绝；`test_web_method_permissions` 覆盖 GET 不修改 |
| 5 | 管理员预约与账单 | 通过 | E2E + TestCase | `test_admin_ui` 覆盖创建/审批/拒绝预约、生成出院账单；权限回归覆盖 GET 不修改 |
| 6 | 义诊活动 | 通过 | E2E + TestCase | `test_admin_ui` 覆盖列表空负责人显示 `未指定`、新增活动；权限回归覆盖删除 GET 不修改 |
| 7 | 志愿者 | 通过 | E2E + TestCase | `test_admin_ui` 覆盖列表和新增；`test_web_method_permissions` 覆盖审批/拒绝 GET 不修改 |
| 8 | 站点 | 通过 | E2E + TestCase | `test_admin_ui` 覆盖列表空负责人显示 `—`、新增站点；权限回归覆盖删除 GET 不修改 |
| 9 | 病历管理 | 通过 | E2E | 医生创建确认、患者只看自己的病历、管理员病历详情均通过；管理员单点详情 Ran 1 test，OK |
| 10 | 医生端 | 通过 | E2E + TestCase | `test_doctor_ui` Ran 7 tests，OK；覆盖仪表盘、患者搜索、预约归属、删除自己的预约、病历确认 |
| 11 | 患者端 | 通过 | E2E | `test_patient_ui` Ran 6 tests，OK；覆盖预约、医生列表/搜索、病历归属、出院账单 |

## Findings

当前无。

## Deferred Coverage

- 视觉截图 diff、可访问性扫描、性能压测、多浏览器矩阵暂不纳入本轮。
- 微信小程序真实端到端测试不在传统 Django WebUI 巡检范围内。
