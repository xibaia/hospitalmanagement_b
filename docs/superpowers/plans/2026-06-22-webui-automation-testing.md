# WebUI Automation Testing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 接入 Django `StaticLiveServerTestCase` + Playwright Python 的 WebUI 自动化测试流程，覆盖 P0/P1 核心交互回归，并提供一键运行脚本和使用文档。

**Architecture:** 保留现有 Django `TestCase` 负责权限和数据库状态验证，新增 `hospital/tests/e2e/` 负责真实浏览器交互。E2E 通过 `StaticLiveServerTestCase` 启动测试服务器，通过 Playwright Chromium 访问页面、登录、提交表单并断言稳定业务文本。

**Tech Stack:** Django 5.2, Django `StaticLiveServerTestCase`, Playwright Python, shell script, existing `hospital/tests/helpers.py`.

---

## File Structure

- Modify: `requirement.txt`
  - Add `playwright`.
- Modify: `.gitignore`
  - Ignore `test-artifacts/`.
- Create: `hospital/tests/e2e/__init__.py`
  - Marks E2E tests as an importable Django test package.
- Create: `hospital/tests/e2e/base.py`
  - Shared Playwright browser lifecycle and helper methods.
- Create: `hospital/tests/e2e/test_public_ui.py`
  - Public homepage smoke test.
- Create: `hospital/tests/e2e/test_auth_ui.py`
  - Admin, doctor, patient login and pending approval flows.
- Create: `hospital/tests/e2e/test_doctor_ui.py`
  - Doctor appointment list rendering and ownership visibility flows.
- Create: `hospital/tests/e2e/test_admin_ui.py`
  - Admin empty form WebUI behavior.
- Create: `hospital/tests/e2e/test_patient_ui.py`
  - Patient appointment empty form WebUI behavior.
- Create: `scripts/check_webui.sh`
  - One command to run the full test suite.
- Create: `docs/webui-testing.md`
  - Usage documentation.

---

### Task 1: Add Dependency And Ignore Test Artifacts

**Files:**
- Modify: `requirement.txt`
- Modify: `.gitignore`

- [ ] **Step 1: Confirm current Playwright import fails or is absent**

Run:

```bash
.venv/bin/python - <<'PY'
try:
    import playwright
except ModuleNotFoundError:
    print("playwright missing")
else:
    print("playwright installed")
PY
```

Expected before dependency install may be either:

```text
playwright missing
```

or:

```text
playwright installed
```

The dependency still needs to be recorded in `requirement.txt`.

- [ ] **Step 2: Add Playwright to requirements**

Append this line to `requirement.txt`:

```text
playwright==1.56.0
```

Use this exact version unless local installation proves a different installed Playwright version is already present and compatible. If a different installed version is used, record that exact version instead.

- [ ] **Step 3: Ignore Playwright failure artifacts**

Add this block near the test/coverage section in `.gitignore`:

```gitignore
# Test artifacts
test-artifacts/
```

- [ ] **Step 4: Install Python dependency if missing**

Run:

```bash
.venv/bin/python -m pip install -r requirement.txt
```

Expected:

```text
Successfully installed playwright
```

or output showing all requirements are already satisfied.

- [ ] **Step 5: Install Chromium runtime if missing**

Run:

```bash
.venv/bin/python -m playwright install chromium
```

Expected:

```text
Downloading Chromium
```

or no download if Chromium is already installed.

---

### Task 2: Create Shared Playwright E2E Base

**Files:**
- Create: `hospital/tests/e2e/__init__.py`
- Create: `hospital/tests/e2e/base.py`

- [ ] **Step 1: Create E2E package marker**

Create `hospital/tests/e2e/__init__.py` as an empty file:

```python
```

- [ ] **Step 2: Create `WebUITestCase`**

Create `hospital/tests/e2e/base.py` with:

```python
import os
from pathlib import Path

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright


os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


class WebUITestCase(StaticLiveServerTestCase):
    browser = None
    playwright = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        if cls.browser:
            cls.browser.close()
            cls.browser = None
        if cls.playwright:
            cls.playwright.stop()
            cls.playwright = None
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.page = self.browser.new_page()

    def tearDown(self):
        failed = self._test_has_failed()
        if failed:
            self._save_failure_screenshot()
        if getattr(self, "page", None):
            self.page.close()
            self.page = None
        super().tearDown()

    def goto(self, path):
        self.page.goto(f"{self.live_server_url}{path}")
        self.page.wait_for_load_state("networkidle")

    def login(self, login_path, username, password):
        self.goto(login_path)
        self.page.locator('input[name="username"]').fill(username)
        self.page.locator('input[name="password"]').fill(password)
        self.page.locator('button[type="submit"]').click()
        self.page.wait_for_load_state("networkidle")

    def assert_page_contains(self, text):
        self.assertIn(text, self.page.content())

    def _test_has_failed(self):
        outcome = getattr(self, "_outcome", None)
        if not outcome:
            return False
        result = getattr(outcome, "result", None)
        if not result:
            return False
        test_id = self.id()
        return any(test.id() == test_id for test, _ in result.failures + result.errors)

    def _save_failure_screenshot(self):
        if not getattr(self, "page", None):
            return
        screenshot_dir = Path("test-artifacts/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = screenshot_dir / f"{self.id().replace('.', '_')}.png"
        try:
            self.page.screenshot(path=str(screenshot_path), full_page=True)
        except Exception:
            pass
```

- [ ] **Step 3: Run package discovery**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e
```

Expected:

```text
Found 0 test(s).
System check identified no issues
```

If Django reports import errors, fix `base.py` before continuing.

---

### Task 3: Add Public Homepage Smoke Test

**Files:**
- Create: `hospital/tests/e2e/test_public_ui.py`

- [ ] **Step 1: Write homepage smoke test**

Create `hospital/tests/e2e/test_public_ui.py` with:

```python
from hospital.tests.e2e.base import WebUITestCase


class PublicWebUITests(WebUITestCase):
    def test_home_page_loads(self):
        self.goto("/")

        self.assert_page_contains("You’ll Love the Way We Care for You")
```

- [ ] **Step 2: Run public E2E test**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_public_ui
```

Expected:

```text
Ran 1 test
OK
```

If the text assertion fails, inspect the rendered home page content and switch to a stable text that exists on `templates/hospital/index.html`.

---

### Task 4: Add Authentication And Approval E2E Tests

**Files:**
- Create: `hospital/tests/e2e/test_auth_ui.py`

- [ ] **Step 1: Write auth tests**

Create `hospital/tests/e2e/test_auth_ui.py` with:

```python
from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import (
    DEFAULT_PASSWORD,
    create_doctor,
    create_grouped_user,
    create_patient,
)


class AuthWebUITests(WebUITestCase):
    def test_admin_login_reaches_dashboard(self):
        admin = create_grouped_user("e2e_admin", "ADMIN")

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)

        self.assertIn("/admin-dashboard", self.page.url)

    def test_approved_doctor_login_reaches_dashboard(self):
        doctor_user, _ = create_doctor(username="e2e_approved_doctor", status=True)

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)

        self.assertIn("/doctor-dashboard", self.page.url)

    def test_approved_patient_login_reaches_dashboard(self):
        patient_user, _ = create_patient(username="e2e_approved_patient", status=True)

        self.login("/patientlogin", patient_user.username, DEFAULT_PASSWORD)

        self.assertIn("/patient-dashboard", self.page.url)

    def test_pending_doctor_login_reaches_waiting_page(self):
        doctor_user, _ = create_doctor(username="e2e_pending_doctor", status=False)

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)

        self.assert_page_contains("Your Account is not approved till now")

    def test_pending_patient_login_reaches_waiting_page(self):
        patient_user, _ = create_patient(username="e2e_pending_patient", status=False)

        self.login("/patientlogin", patient_user.username, DEFAULT_PASSWORD)

        self.assert_page_contains("Your Account is not approved till now")
```

- [ ] **Step 2: Run auth E2E tests**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_auth_ui
```

Expected:

```text
Ran 5 tests
OK
```

If waiting page text differs, inspect `templates/hospital/doctor_wait_for_approval.html` and `templates/hospital/patient_wait_for_approval.html`, then use the actual stable text.

---

### Task 5: Add Doctor Appointment E2E Tests

**Files:**
- Create: `hospital/tests/e2e/test_doctor_ui.py`

- [ ] **Step 1: Write doctor appointment tests**

Create `hospital/tests/e2e/test_doctor_ui.py` with:

```python
from hospital import models
from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import DEFAULT_PASSWORD, create_doctor, create_patient


class DoctorWebUITests(WebUITestCase):
    def test_doctor_appointment_list_shows_duplicate_patient_appointments(self):
        doctor_user, doctor = create_doctor(username="e2e_duplicate_doctor")
        _, patient = create_patient(username="e2e_duplicate_patient", assigned_doctor=doctor)
        for description in ("E2E first follow up", "E2E second follow up"):
            models.Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                patientName=patient.get_name,
                doctorName=doctor.get_name,
                description=description,
                status=True,
            )

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)
        self.goto("/doctor-view-appointment")

        self.assert_page_contains("E2E first follow up")
        self.assert_page_contains("E2E second follow up")

    def test_doctor_appointment_list_renders_default_avatar_for_patient_without_picture(self):
        doctor_user, doctor = create_doctor(username="e2e_avatar_doctor")
        _, patient = create_patient(username="e2e_avatar_patient", assigned_doctor=doctor)
        models.Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            patientName=patient.get_name,
            doctorName=doctor.get_name,
            description="E2E avatar appointment",
            status=True,
        )

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)
        self.goto("/doctor-view-appointment")

        self.assert_page_contains("E2E avatar appointment")
        self.assert_page_contains("Default Profile Pic")

    def test_doctor_delete_page_only_shows_current_doctor_appointments(self):
        doctor_user, doctor = create_doctor(username="e2e_visible_doctor")
        _, other_doctor = create_doctor(username="e2e_hidden_doctor")
        _, visible_patient = create_patient(username="e2e_visible_patient", assigned_doctor=doctor)
        _, hidden_patient = create_patient(username="e2e_hidden_patient", assigned_doctor=other_doctor)
        models.Appointment.objects.create(
            patient=visible_patient,
            doctor=doctor,
            patientName=visible_patient.get_name,
            doctorName=doctor.get_name,
            description="E2E visible appointment",
            status=True,
        )
        models.Appointment.objects.create(
            patient=hidden_patient,
            doctor=other_doctor,
            patientName=hidden_patient.get_name,
            doctorName=other_doctor.get_name,
            description="E2E hidden appointment",
            status=True,
        )

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)
        self.goto("/doctor-delete-appointment")

        self.assert_page_contains("E2E visible appointment")
        self.assertNotIn("E2E hidden appointment", self.page.content())
        self.assertGreater(
            self.page.locator('form[action*="/delete-appointment/"] button[type="submit"]').count(),
            0,
        )
```

- [ ] **Step 2: Run doctor E2E tests**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_doctor_ui
```

Expected:

```text
Ran 3 tests
OK
```

---

### Task 6: Add Admin Empty Form E2E Tests

**Files:**
- Create: `hospital/tests/e2e/test_admin_ui.py`

- [ ] **Step 1: Write admin empty form tests**

Create `hospital/tests/e2e/test_admin_ui.py` with:

```python
from hospital import models
from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import DEFAULT_PASSWORD, create_grouped_user


class AdminWebUITests(WebUITestCase):
    def test_admin_add_doctor_empty_form_stays_on_page(self):
        admin = create_grouped_user("e2e_add_doctor_admin", "ADMIN")

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-add-doctor")
        self.page.locator('button[type="submit"]').click()
        self.page.wait_for_load_state("networkidle")

        self.assertIn("/admin-add-doctor", self.page.url)
        self.assertEqual(models.Doctor.objects.count(), 0)

    def test_admin_add_patient_empty_form_stays_on_page(self):
        admin = create_grouped_user("e2e_add_patient_admin", "ADMIN")

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-add-patient")
        self.page.locator('button[type="submit"]').click()
        self.page.wait_for_load_state("networkidle")

        self.assertIn("/admin-add-patient", self.page.url)
        self.assertEqual(models.Patient.objects.count(), 0)
```

- [ ] **Step 2: Run admin E2E tests**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_admin_ui
```

Expected:

```text
Ran 2 tests
OK
```

---

### Task 7: Add Patient Empty Appointment E2E Test

**Files:**
- Create: `hospital/tests/e2e/test_patient_ui.py`

- [ ] **Step 1: Write patient appointment empty form test**

Create `hospital/tests/e2e/test_patient_ui.py` with:

```python
from hospital import models
from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import DEFAULT_PASSWORD, create_patient


class PatientWebUITests(WebUITestCase):
    def test_patient_book_appointment_empty_form_stays_on_page(self):
        patient_user, _ = create_patient(username="e2e_empty_booking_patient")

        self.login("/patientlogin", patient_user.username, DEFAULT_PASSWORD)
        self.goto("/patient-book-appointment")
        self.page.locator('button[type="submit"]').click()
        self.page.wait_for_load_state("networkidle")

        self.assertIn("/patient-book-appointment", self.page.url)
        self.assertEqual(models.Appointment.objects.count(), 0)
```

- [ ] **Step 2: Run patient E2E test**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_patient_ui
```

Expected:

```text
Ran 1 test
OK
```

---

### Task 8: Add Run Script And Usage Documentation

**Files:**
- Create: `scripts/check_webui.sh`
- Create: `docs/webui-testing.md`

- [ ] **Step 1: Create run script**

Create `scripts/check_webui.sh` with:

```bash
#!/usr/bin/env bash
set -euo pipefail

.venv/bin/python manage.py test hospital.tests
```

- [ ] **Step 2: Make run script executable**

Run:

```bash
chmod +x scripts/check_webui.sh
```

- [ ] **Step 3: Create usage documentation**

Create `docs/webui-testing.md` with:

```markdown
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
```

---

### Task 9: Run Verification And Fix Failures

**Files:**
- Any files touched by failing tests.

- [ ] **Step 1: Run existing Web review tests**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.test_web_review_fixes
```

Expected:

```text
OK
```

- [ ] **Step 2: Run all E2E tests**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e
```

Expected:

```text
Ran 12 tests
OK
```

If the count differs because tests were added or consolidated, ensure all E2E test files ran and passed.

- [ ] **Step 3: Run full test suite**

Run:

```bash
.venv/bin/python manage.py test hospital.tests
```

Expected:

```text
OK
```

- [ ] **Step 4: Run shell entrypoint**

Run:

```bash
./scripts/check_webui.sh
```

Expected:

```text
OK
```

- [ ] **Step 5: Check git diff**

Run:

```bash
git status --short
git diff --check
```

Expected:

```text
git diff --check
```

prints no output.

---

### Task 10: Final Review Before Commit

**Files:**
- Review all files changed in this plan.

- [ ] **Step 1: Review changed file list**

Run:

```bash
git status --short
```

Expected changed files include:

```text
.gitignore
requirement.txt
docs/superpowers/plans/2026-06-22-webui-automation-testing.md
docs/superpowers/specs/2026-06-22-webui-automation-testing-design.md
docs/webui-automation-test-plan.md
docs/webui-testing.md
hospital/tests/e2e/__init__.py
hospital/tests/e2e/base.py
hospital/tests/e2e/test_admin_ui.py
hospital/tests/e2e/test_auth_ui.py
hospital/tests/e2e/test_doctor_ui.py
hospital/tests/e2e/test_patient_ui.py
hospital/tests/e2e/test_public_ui.py
scripts/check_webui.sh
```

- [ ] **Step 2: Review E2E implementation**

Check:

- `base.py` closes page, browser, and Playwright.
- failure screenshots are best-effort and do not hide original failures.
- E2E tests do not depend on real `db.sqlite3`.
- Cross-doctor delete permission remains covered by Django `TestCase`.

- [ ] **Step 3: Stop before committing unless user approves**

Do not commit automatically. Report changed files and verification results to the user, then wait for approval.
