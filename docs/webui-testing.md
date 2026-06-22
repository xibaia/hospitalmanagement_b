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
.venv/bin/python manage.py test hospital.tests.e2e
```

只运行某个 E2E 文件：

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_doctor_ui
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
