# WebUI 自动化测试

## 测试栈

本项目使用 Django `TestCase` 覆盖服务端权限和数据状态，使用 Django `StaticLiveServerTestCase` + Playwright Python 覆盖真实 WebUI 交互。

## 首次安装

安装 Python 依赖：

```bash
.venv/bin/python -m pip install -r requirement.txt
```

安装 Chromium 运行时：

```bash
.venv/bin/python -m playwright install chromium
```

## 运行测试

运行全部测试：

```bash
./scripts/check_webui.sh
```

只运行 E2E：

```bash
./scripts/check_webui_e2e.sh
```

只运行某个 E2E 文件：

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_doctor_ui
```

只运行服务端 Web 权限回归：

```bash
.venv/bin/python manage.py test hospital.tests.test_web_review_fixes hospital.tests.test_web_method_permissions
```

## 覆盖矩阵

| 模块 | 浏览器 E2E | Django TestCase |
| --- | --- | --- |
| 公共入口 | 首页、关于、联系、三类入口 | 不需要 |
| 登录审批 | 三类登录、待审批跳转 | 角色分组和认证 API |
| 管理员 | 审批、预约、出院、活动、站点、志愿者 | GET 拒绝修改、跨角色访问 |
| 医生 | 患者列表、搜索、预约列表、删除自己的预约、病历创建确认 | 不能删除他人预约 |
| 患者 | 预约申请、预约列表、医生列表、病历、出院账单 | 服务端数据归属 |

## 常用命令

运行完整 WebUI 回归：

```bash
./scripts/check_webui.sh
```

只运行浏览器 E2E：

```bash
./scripts/check_webui_e2e.sh
```

## 失败截图

E2E 失败时会尝试保存截图到：

```text
test-artifacts/screenshots/
```

该目录已被 `.gitignore` 忽略，只用于本地调试。

## 写测试的原则

- 权限、POST 限制、数据库状态优先写 Django `TestCase`。
- 登录、点击、表单提交、页面渲染写 Playwright E2E。
- 优先使用 `input[name="username"]`、`input[name="password"]`、`get_by_text()`、`get_by_placeholder()` 等稳定选择器。
- 图标按钮没有可访问名称时，可以使用稳定 CSS selector。
- 不做视觉截图 diff，不断言 CSS 细节。

## 失败排查

- 先看终端 traceback 的第一个失败用例和断言位置。
- E2E 失败时查看 `test-artifacts/screenshots/` 下的截图。
- 如果是表单未提交，优先检查字段名、必填项、长度限制和提交控件类型。
- 如果是权限或数据归属问题，优先补 Django `TestCase` 复现服务端约束。
