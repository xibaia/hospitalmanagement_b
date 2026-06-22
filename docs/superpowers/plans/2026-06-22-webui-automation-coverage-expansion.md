# WebUI Automation Coverage Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有 Playwright/Django E2E 基线之上，按模块扩展 WebUI 自动化覆盖，形成提交前可重复运行的核心业务闭环回归套件。

**Architecture:** 保持现有分层：浏览器真实交互放在 `hospital/tests/e2e/`，不可见的 HTTP 方法、跨角色权限和服务端状态约束放在 Django `TestCase`。每个模块独立增加少量高价值路径，优先覆盖 P0/P1 业务闭环，不做视觉 diff、性能、多浏览器矩阵。

**Tech Stack:** Django `TestCase`, Django `StaticLiveServerTestCase`, Playwright Python, existing `hospital/tests/helpers.py`, shell scripts.

---

## Scope

本计划覆盖下一阶段 P0/P1 自动化：

- 公共入口页面补齐。
- 管理员审批、预约、出院账单、活动、站点、志愿者管理。
- 患者预约闭环、医生列表、病历、出院账单。
- 医生患者列表、搜索、预约删除、病历创建与确认。
- 不可见安全路径的 Django `TestCase` 回归。

本计划暂不覆盖：

- 视觉截图 diff。
- Firefox/WebKit 多浏览器矩阵。
- 性能测试、压测、可访问性扫描。
- 微信小程序真实端到端测试。

当前要求：不要自动提交。每个任务完成后只运行验证并保留未提交改动，等待用户确认。

---

## File Structure

- Modify: `hospital/tests/helpers.py`
  - Add reusable factories for appointments, discharge bills, stations, volunteers, tooth findings.
- Modify: `hospital/tests/e2e/base.py`
  - Add small Playwright helpers for URL assertions, logout, select filling, form submission.
- Modify: `hospital/tests/e2e/test_public_ui.py`
  - Expand public navigation smoke coverage.
- Modify: `hospital/tests/e2e/test_admin_ui.py`
  - Add admin approval, appointment, discharge, activity, station, volunteer E2E tests.
- Modify: `hospital/tests/e2e/test_patient_ui.py`
  - Add patient appointment, doctor list, records, discharge E2E tests.
- Modify: `hospital/tests/e2e/test_doctor_ui.py`
  - Add doctor dashboard, patient list/search, own appointment delete, medical record E2E tests.
- Create: `hospital/tests/test_web_method_permissions.py`
  - Add server-side method and role permission regression tests.
- Create: `scripts/check_webui_e2e.sh`
  - One command for browser-only E2E tests.
- Modify: `scripts/check_webui.sh`
  - Keep full test suite entrypoint and document relation to E2E-only script.
- Modify: `docs/webui-testing.md`
  - Add coverage matrix, module commands, and failure triage notes.

---

### Task 1: Strengthen Shared Test Helpers

**Files:**
- Modify: `hospital/tests/helpers.py`
- Modify: `hospital/tests/e2e/base.py`

- [ ] **Step 1: Add missing model imports**

In `hospital/tests/helpers.py`, replace the existing model import:

```python
from hospital.models import Activity, Doctor, MedicalRecord, Patient
```

with:

```python
from hospital.models import (
    Activity,
    Appointment,
    Doctor,
    MedicalRecord,
    Patient,
    PatientDischargeDetails,
    Station,
    ToothFinding,
    Volunteer,
)
```

- [ ] **Step 2: Add reusable data factories**

Append these helpers to `hospital/tests/helpers.py`:

```python
def create_appointment(
    patient,
    doctor,
    description="Follow-up appointment",
    status=True,
):
    return Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        patientName=patient.get_name,
        doctorName=doctor.get_name,
        description=description,
        status=status,
    )


def create_discharge(patient, assigned_doctor_name="未指定", total=460):
    return PatientDischargeDetails.objects.create(
        patient=patient,
        patientName=patient.get_name,
        assignedDoctorName=assigned_doctor_name,
        address=patient.address,
        mobile=patient.mobile,
        symptoms=patient.symptoms,
        admitDate=patient.admitDate,
        releaseDate=timezone.now().date(),
        daySpent=1,
        medicineCost=120,
        roomCharge=200,
        doctorFee=100,
        OtherCharge=40,
        total=total,
    )


def create_station(name="E2E Station", supervisor=None, is_active=True):
    return Station.objects.create(
        name=name,
        address="E2E Station Address",
        latitude=31.2304,
        longitude=121.4737,
        supervisor=supervisor,
        phone="02100000000",
        is_active=is_active,
    )


def create_volunteer(
    username="volunteer",
    password=DEFAULT_PASSWORD,
    status=True,
    **kwargs,
):
    user = create_grouped_user(
        username=username,
        group_name="VOLUNTEER",
        password=password,
        first_name=kwargs.pop("first_name", "Vol"),
        last_name=kwargs.pop("last_name", "Unteer"),
    )
    volunteer = Volunteer.objects.create(
        user=user,
        real_name=kwargs.pop("real_name", f"Volunteer {username}"),
        mobile=kwargs.pop("mobile", "13700137000"),
        status=status,
        **kwargs,
    )
    return user, volunteer


def create_tooth_finding(
    record,
    tooth_number=11,
    finding_type="caries",
    note="E2E finding",
):
    return ToothFinding.objects.create(
        record=record,
        tooth_number=tooth_number,
        finding_type=finding_type,
        note=note,
    )
```

- [ ] **Step 3: Add browser helper methods**

Append these methods inside `WebUITestCase` in `hospital/tests/e2e/base.py`:

```python
    def logout(self):
        response = self.page.request.post(
            f"{self.live_server_url}/logout",
            headers={"X-CSRFToken": self._csrf_token()},
        )
        self.assertEqual(response.status, 200)

    def assert_url_contains(self, path):
        self.assertIn(path, self.page.url)

    def submit_first_form(self):
        self.page.locator('form button[type="submit"]').first.click()
        self.page.wait_for_load_state("networkidle")

    def select_first_real_option(self, selector):
        select = self.page.locator(selector)
        values = select.locator("option").evaluate_all(
            "(options) => options.map((option) => option.value).filter(Boolean)"
        )
        self.assertGreater(len(values), 0)
        select.select_option(values[0])
        return values[0]

    def click_form_action(self, action_fragment):
        button = self.page.locator(
            f'form[action*="{action_fragment}"] button[type="submit"]'
        )
        self.assertEqual(button.count(), 1)
        button.click()
        self.page.wait_for_load_state("networkidle")

    def _csrf_token(self):
        for cookie in self.page.context.cookies(self.live_server_url):
            if cookie["name"] == "csrftoken":
                return cookie["value"]
        self.fail("Missing CSRF cookie before logout")
```

- [ ] **Step 4: Run existing E2E tests**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e
```

Expected:

```text
Ran 12 tests
OK
```

If the count changes because tests already grew locally, verify all E2E files ran and output is `OK`.

---

### Task 2: Expand Public Entry Smoke Tests

**Files:**
- Modify: `hospital/tests/e2e/test_public_ui.py`

- [ ] **Step 1: Add public route coverage**

Replace `hospital/tests/e2e/test_public_ui.py` with:

```python
from hospital.tests.e2e.base import WebUITestCase


class PublicWebUITests(WebUITestCase):
    def test_home_page_loads(self):
        self.goto("/")

        self.assert_page_contains("You’ll Love the Way We Care for You")

    def test_public_entry_pages_load(self):
        pages = [
            ("/aboutus", "About"),
            ("/contactus", "Contact"),
            ("/adminclick", "Admin"),
            ("/doctorclick", "Doctor"),
            ("/patientclick", "Patient"),
        ]

        for path, expected_text in pages:
            with self.subTest(path=path):
                self.goto(path)

                self.assert_page_contains(expected_text)
```

- [ ] **Step 2: Run public E2E tests**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_public_ui
```

Expected:

```text
Ran 2 tests
OK
```

If a page uses different visible copy, inspect the rendered page and replace `expected_text` with a stable text that is actually present.

---

### Task 3: Expand Admin Approval Workflows

**Files:**
- Modify: `hospital/tests/e2e/test_admin_ui.py`

- [ ] **Step 1: Add imports**

Update the import block in `hospital/tests/e2e/test_admin_ui.py`:

```python
from hospital import models
from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import (
    DEFAULT_PASSWORD,
    create_doctor,
    create_grouped_user,
    create_patient,
)
```

- [ ] **Step 2: Add doctor approval and rejection tests**

Append to `AdminWebUITests`:

```python
    def test_admin_can_approve_pending_doctor_from_ui(self):
        admin = create_grouped_user("e2e_approve_doctor_admin", "ADMIN")
        _, doctor = create_doctor(username="e2e_pending_doctor_to_approve", status=False)

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-approve-doctor")
        self.assert_page_contains(doctor.get_name)
        self.click_form_action(f"/approve-doctor/{doctor.id}")

        doctor.refresh_from_db()
        self.assertTrue(doctor.status)

    def test_admin_can_reject_pending_doctor_from_ui(self):
        admin = create_grouped_user("e2e_reject_doctor_admin", "ADMIN")
        doctor_user, doctor = create_doctor(username="e2e_pending_doctor_to_reject", status=False)

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-approve-doctor")
        self.assert_page_contains(doctor.get_name)
        self.click_form_action(f"/reject-doctor/{doctor.id}")

        self.assertFalse(models.Doctor.objects.filter(id=doctor.id).exists())
        self.assertFalse(models.User.objects.filter(id=doctor_user.id).exists())
```

- [ ] **Step 3: Add patient approval and rejection tests**

Append to `AdminWebUITests`:

```python
    def test_admin_can_approve_pending_patient_from_ui(self):
        admin = create_grouped_user("e2e_approve_patient_admin", "ADMIN")
        _, doctor = create_doctor(username="e2e_patient_approval_doctor")
        _, patient = create_patient(
            username="e2e_pending_patient_to_approve",
            assigned_doctor=doctor,
            status=False,
        )

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-approve-patient")
        self.assert_page_contains(patient.get_name)
        self.click_form_action(f"/approve-patient/{patient.id}")

        patient.refresh_from_db()
        self.assertTrue(patient.status)

    def test_admin_can_reject_pending_patient_from_ui(self):
        admin = create_grouped_user("e2e_reject_patient_admin", "ADMIN")
        _, doctor = create_doctor(username="e2e_patient_rejection_doctor")
        patient_user, patient = create_patient(
            username="e2e_pending_patient_to_reject",
            assigned_doctor=doctor,
            status=False,
        )

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-approve-patient")
        self.assert_page_contains(patient.get_name)
        self.click_form_action(f"/reject-patient/{patient.id}")

        self.assertFalse(models.Patient.objects.filter(id=patient.id).exists())
        self.assertFalse(models.User.objects.filter(id=patient_user.id).exists())
```

- [ ] **Step 4: Run admin E2E tests**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_admin_ui
```

Expected:

```text
OK
```

If the form selector fails, inspect the approval templates and switch `click_form_action()` to the actual `form[action]` fragment.

---

### Task 4: Add Admin Appointment Workflows

**Files:**
- Modify: `hospital/tests/e2e/test_admin_ui.py`

- [ ] **Step 1: Add approved appointment creation test**

Append to `AdminWebUITests`:

```python
    def test_admin_can_create_approved_appointment_from_ui(self):
        admin = create_grouped_user("e2e_create_appointment_admin", "ADMIN")
        _, doctor = create_doctor(username="e2e_admin_appt_doctor")
        _, patient = create_patient(username="e2e_admin_appt_patient", assigned_doctor=doctor)

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-add-appointment")
        self.page.locator('select[name="doctor"]').select_option(str(doctor.id))
        self.page.locator('select[name="patient"]').select_option(str(patient.id))
        self.page.locator('textarea[name="description"]').fill("E2E admin-created appointment")
        self.submit_first_form()

        self.assert_url_contains("/admin-view-appointment")
        appointment = models.Appointment.objects.get(description="E2E admin-created appointment")
        self.assertTrue(appointment.status)
        self.assertEqual(appointment.doctor, doctor)
        self.assertEqual(appointment.patient, patient)
```

- [ ] **Step 2: Add appointment approval and rejection tests**

Append to `AdminWebUITests`:

```python
    def test_admin_can_approve_pending_appointment_from_ui(self):
        admin = create_grouped_user("e2e_approve_appointment_admin", "ADMIN")
        _, doctor = create_doctor(username="e2e_pending_appt_doctor")
        _, patient = create_patient(username="e2e_pending_appt_patient", assigned_doctor=doctor)
        appointment = models.Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            patientName=patient.get_name,
            doctorName=doctor.get_name,
            description="E2E pending appointment approval",
            status=False,
        )

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-approve-appointment")
        self.assert_page_contains("E2E pending appointment approval")
        self.click_form_action(f"/approve-appointment/{appointment.id}")

        appointment.refresh_from_db()
        self.assertTrue(appointment.status)

    def test_admin_can_reject_pending_appointment_from_ui(self):
        admin = create_grouped_user("e2e_reject_appointment_admin", "ADMIN")
        _, doctor = create_doctor(username="e2e_reject_appt_doctor")
        _, patient = create_patient(username="e2e_reject_appt_patient", assigned_doctor=doctor)
        appointment = models.Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            patientName=patient.get_name,
            doctorName=doctor.get_name,
            description="E2E pending appointment rejection",
            status=False,
        )

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-approve-appointment")
        self.assert_page_contains("E2E pending appointment rejection")
        self.click_form_action(f"/reject-appointment/{appointment.id}")

        self.assertFalse(models.Appointment.objects.filter(id=appointment.id).exists())
```

- [ ] **Step 3: Run admin E2E tests**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_admin_ui
```

Expected:

```text
OK
```

---

### Task 5: Add Patient Appointment Closed Loop

**Files:**
- Modify: `hospital/tests/e2e/test_patient_ui.py`

- [x] **Step 1: Update imports**

Use this import block:

```python
from hospital import models
from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import DEFAULT_PASSWORD, create_doctor, create_grouped_user, create_patient
```

- [ ] **Step 2: Add patient booking success test**

Append to `PatientWebUITests`:

```python
    def test_patient_can_request_appointment_and_see_pending_record(self):
        _, doctor = create_doctor(username="e2e_patient_booking_doctor")
        patient_user, patient = create_patient(
            username="e2e_booking_patient",
            assigned_doctor=doctor,
        )

        self.login("/patientlogin", patient_user.username, DEFAULT_PASSWORD)
        self.goto("/patient-book-appointment")
        self.page.locator('select[name="doctor"]').select_option(str(doctor.id))
        self.page.locator('textarea[name="description"]').fill("E2E patient booking request")
        self.submit_first_form()

        self.assert_url_contains("/patient-view-appointment")
        appointment = models.Appointment.objects.get(description="E2E patient booking request")
        self.assertEqual(appointment.patient, patient)
        self.assertEqual(appointment.doctor, doctor)
        self.assertFalse(appointment.status)
        self.assert_page_contains("E2E patient booking request")
```

- [ ] **Step 3: Add patient-to-admin-to-doctor appointment flow**

Append to `PatientWebUITests`:

```python
    def test_patient_booking_becomes_visible_to_doctor_after_admin_approval(self):
        admin = create_grouped_user("e2e_patient_flow_admin", "ADMIN")
        doctor_user, doctor = create_doctor(username="e2e_patient_flow_doctor")
        patient_user, _ = create_patient(
            username="e2e_patient_flow_patient",
            assigned_doctor=doctor,
        )

        self.login("/patientlogin", patient_user.username, DEFAULT_PASSWORD)
        self.goto("/patient-book-appointment")
        self.page.locator('select[name="doctor"]').select_option(str(doctor.id))
        self.page.locator('textarea[name="description"]').fill("E2E cross-role appointment")
        self.submit_first_form()
        appointment = models.Appointment.objects.get(description="E2E cross-role appointment")
        self.logout()

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-approve-appointment")
        self.click_form_action(f"/approve-appointment/{appointment.id}")
        appointment.refresh_from_db()
        self.assertTrue(appointment.status)
        self.logout()

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)
        self.goto("/doctor-view-appointment")
        self.assert_page_contains("E2E cross-role appointment")
```

- [ ] **Step 4: Run patient E2E tests**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_patient_ui
```

Expected:

```text
OK
```

---

### Task 6: Add Doctor Dashboard, Search, And Own Delete Flow

**Files:**
- Modify: `hospital/tests/e2e/test_doctor_ui.py`

- [ ] **Step 1: Update imports**

Use this import block:

```python
from hospital import models
from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import (
    DEFAULT_PASSWORD,
    create_appointment,
    create_doctor,
    create_patient,
)
```

- [ ] **Step 2: Add dashboard and patient list smoke tests**

Append to `DoctorWebUITests`:

```python
    def test_doctor_dashboard_and_patient_list_load(self):
        doctor_user, doctor = create_doctor(username="e2e_doctor_dashboard")
        _, patient = create_patient(
            username="e2e_doctor_dashboard_patient",
            assigned_doctor=doctor,
            symptoms="E2E dashboard symptom",
        )

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)
        self.goto("/doctor-dashboard")
        self.assert_page_contains(doctor.get_name)
        self.goto("/doctor-view-patient")
        self.assert_page_contains(patient.get_name)
        self.assert_page_contains("E2E dashboard symptom")

    def test_doctor_patient_search_filters_assigned_patients(self):
        doctor_user, doctor = create_doctor(username="e2e_doctor_search")
        _, matching = create_patient(
            username="e2e_matching_patient",
            assigned_doctor=doctor,
            symptoms="RareSearchSymptom",
        )
        _, hidden = create_patient(
            username="e2e_hidden_search_patient",
            assigned_doctor=doctor,
            symptoms="Common symptom",
        )

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)
        self.goto("/search?query=RareSearchSymptom")

        self.assert_page_contains(matching.get_name)
        self.assertNotIn(hidden.get_name, self.page.content())
```

- [ ] **Step 3: Add own appointment delete UI test**

Append to `DoctorWebUITests`:

```python
    def test_doctor_can_delete_own_appointment_from_ui(self):
        doctor_user, doctor = create_doctor(username="e2e_delete_own_doctor")
        _, patient = create_patient(username="e2e_delete_own_patient", assigned_doctor=doctor)
        appointment = create_appointment(
            patient=patient,
            doctor=doctor,
            description="E2E delete own appointment",
            status=True,
        )

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)
        self.goto("/doctor-delete-appointment")
        self.assert_page_contains("E2E delete own appointment")
        self.click_form_action(f"/delete-appointment/{appointment.id}")

        self.assert_url_contains("/doctor-delete-appointment")
        self.assertFalse(models.Appointment.objects.filter(id=appointment.id).exists())
```

- [ ] **Step 4: Run doctor E2E tests**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_doctor_ui
```

Expected:

```text
OK
```

---

### Task 7: Add Medical Record Closed Loop

**Files:**
- Modify: `hospital/tests/e2e/test_doctor_ui.py`
- Modify: `hospital/tests/e2e/test_patient_ui.py`
- Modify: `hospital/tests/e2e/test_admin_ui.py`

- [ ] **Step 1: Add doctor record create and confirm test**

Append to `DoctorWebUITests`:

```python
    def test_doctor_can_create_and_confirm_medical_record(self):
        doctor_user, doctor = create_doctor(username="e2e_record_doctor")
        _, patient = create_patient(username="e2e_record_patient", assigned_doctor=doctor)

        self.login("/doctorlogin", doctor_user.username, DEFAULT_PASSWORD)
        self.goto("/doctor-create-record")
        self.page.locator('select[name="patient"]').select_option(str(patient.id))
        self.page.locator('input[name="check_date"]').fill("2026-06-22")
        self.page.locator('textarea[name="chief_complaint"]').fill("E2E tooth pain")
        self.page.locator('textarea[name="diagnosis"]').fill("E2E caries diagnosis")
        self.submit_first_form()

        self.assert_url_contains("/doctor-records")
        record = models.MedicalRecord.objects.get(patient=patient, doctor=doctor)
        self.assertEqual(record.chief_complaint, "E2E tooth pain")
        self.assertFalse(record.doctor_confirmed)

        self.goto(f"/doctor-update-record/{record.id}")
        self.page.locator('input[name="doctor_confirmed"]').check()
        self.submit_first_form()

        record.refresh_from_db()
        self.assertTrue(record.doctor_confirmed)
        self.assertIsNotNone(record.confirmed_at)
```

- [ ] **Step 2: Add patient record visibility test**

Update imports in `hospital/tests/e2e/test_patient_ui.py`:

```python
from hospital import models
from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import DEFAULT_PASSWORD, create_doctor, create_grouped_user, create_patient, create_record
```

Append to `PatientWebUITests`:

```python
    def test_patient_can_view_own_medical_record_detail(self):
        _, doctor = create_doctor(username="e2e_patient_record_doctor")
        patient_user, patient = create_patient(
            username="e2e_patient_record_patient",
            assigned_doctor=doctor,
        )
        record = create_record(
            patient=patient,
            doctor=doctor,
            chief_complaint="E2E patient visible complaint",
            diagnosis="E2E patient visible diagnosis",
        )

        self.login("/patientlogin", patient_user.username, DEFAULT_PASSWORD)
        self.goto("/patient-records")
        self.assert_page_contains(record.visit_no)
        self.goto(f"/patient-view-record/{record.id}")

        self.assert_page_contains("E2E patient visible complaint")
        self.assert_page_contains("E2E patient visible diagnosis")
```

- [ ] **Step 3: Add admin record visibility test**

Update imports in `hospital/tests/e2e/test_admin_ui.py`:

```python
from hospital import models
from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import (
    DEFAULT_PASSWORD,
    create_doctor,
    create_grouped_user,
    create_patient,
    create_record,
)
```

Append to `AdminWebUITests`:

```python
    def test_admin_can_view_medical_record_detail(self):
        admin = create_grouped_user("e2e_admin_record_admin", "ADMIN")
        _, doctor = create_doctor(username="e2e_admin_record_doctor")
        _, patient = create_patient(username="e2e_admin_record_patient", assigned_doctor=doctor)
        record = create_record(
            patient=patient,
            doctor=doctor,
            chief_complaint="E2E admin record complaint",
            diagnosis="E2E admin record diagnosis",
        )

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-medical-records")
        self.assert_page_contains(record.visit_no)
        self.goto(f"/admin-view-record/{record.id}")

        self.assert_page_contains("E2E admin record complaint")
        self.assert_page_contains("E2E admin record diagnosis")
```

- [ ] **Step 4: Run role E2E tests**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_doctor_ui hospital.tests.e2e.test_patient_ui hospital.tests.e2e.test_admin_ui
```

Expected:

```text
OK
```

---

### Task 8: Add Discharge Billing Closed Loop

**Files:**
- Modify: `hospital/tests/e2e/test_admin_ui.py`
- Modify: `hospital/tests/e2e/test_patient_ui.py`

- [x] **Step 1: Add admin discharge bill generation test**

Append to `AdminWebUITests`:

```python
    def test_admin_can_generate_patient_discharge_bill(self):
        admin = create_grouped_user("e2e_discharge_admin", "ADMIN")
        _, doctor = create_doctor(username="e2e_discharge_doctor")
        _, patient = create_patient(
            username="e2e_discharge_patient",
            assigned_doctor=doctor,
            symptoms="E2E discharge symptoms",
        )

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto(f"/discharge-patient/{patient.id}")
        self.page.locator('input[name="roomCharge"]').fill("200")
        self.page.locator('input[name="doctorFee"]').fill("100")
        self.page.locator('input[name="medicineCost"]').fill("120")
        self.page.locator('input[name="OtherCharge"]').fill("40")
        self.submit_first_form()

        self.assert_page_contains(patient.get_name)
        bill = models.PatientDischargeDetails.objects.get(patient=patient)
        self.assertEqual(bill.total, bill.roomCharge + bill.doctorFee + bill.medicineCost + bill.OtherCharge)
        self.assertEqual(bill.assignedDoctorName, doctor.get_name)
```

- [x] **Step 2: Add patient discharge page test**

Update imports in `hospital/tests/e2e/test_patient_ui.py` to include `create_discharge`:

```python
from hospital.tests.helpers import (
    DEFAULT_PASSWORD,
    create_discharge,
    create_doctor,
    create_grouped_user,
    create_patient,
    create_record,
)
```

Append to `PatientWebUITests`:

```python
    def test_patient_can_view_latest_discharge_bill(self):
        _, doctor = create_doctor(username="e2e_patient_discharge_doctor")
        patient_user, patient = create_patient(
            username="e2e_patient_discharge_patient",
            assigned_doctor=doctor,
        )
        create_discharge(patient=patient, assigned_doctor_name=doctor.get_name, total=460)

        self.login("/patientlogin", patient_user.username, DEFAULT_PASSWORD)
        self.goto("/patient-discharge")

        self.assert_page_contains(patient.get_name)
        self.assert_page_contains(doctor.get_name)
        self.assert_page_contains("460")
```

- [x] **Step 3: Run admin and patient E2E tests**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_admin_ui hospital.tests.e2e.test_patient_ui
```

Expected:

```text
OK
```

---

### Task 9: Add Activity, Station, And Volunteer Admin Flows

**Files:**
- Modify: `hospital/tests/e2e/test_admin_ui.py`

- [ ] **Step 1: Update imports**

Ensure the admin E2E import block includes:

```python
from datetime import timedelta

from django.utils import timezone

from hospital import models
from hospital.tests.e2e.base import WebUITestCase
from hospital.tests.helpers import (
    DEFAULT_PASSWORD,
    create_activity,
    create_doctor,
    create_grouped_user,
    create_patient,
    create_record,
    create_station,
    create_volunteer,
)
```

- [x] **Step 2: Add activity list and create test**

Append to `AdminWebUITests`:

```python
    def test_admin_activity_pages_show_empty_leader_and_created_activity(self):
        admin = create_grouped_user("e2e_activity_admin", "ADMIN")
        create_activity(name="E2E existing activity", leader=None)
        start = timezone.now().replace(second=0, microsecond=0)
        end = start + timedelta(hours=2)

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-activity")
        self.assert_page_contains("E2E existing activity")
        self.assert_page_contains("未指定")

        self.goto("/admin-add-activity")
        self.page.locator('input[name="name"]').fill("E2E created activity")
        self.page.locator('input[name="location"]').fill("E2E activity location")
        self.page.locator('input[name="start_time"]').fill(start.strftime("%Y-%m-%dT%H:%M"))
        self.page.locator('input[name="end_time"]').fill(end.strftime("%Y-%m-%dT%H:%M"))
        self.page.locator('textarea[name="description"]').fill("E2E activity description")
        self.page.locator('select[name="status"]').select_option("active")
        self.submit_first_form()

        self.assert_url_contains("/admin-activity")
        self.assertTrue(models.Activity.objects.filter(name="E2E created activity").exists())
```

- [x] **Step 3: Add station list and create test**

Append to `AdminWebUITests`:

```python
    def test_admin_station_pages_show_empty_supervisor_and_created_station(self):
        admin = create_grouped_user("e2e_station_admin", "ADMIN")
        create_station(name="E2E existing station", supervisor=None)

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-station")
        self.assert_page_contains("E2E existing station")
        self.assert_page_contains("—")

        self.goto("/admin-add-station")
        self.page.locator('input[name="name"]').fill("E2E created station")
        self.page.locator('input[name="address"]').fill("E2E station address")
        self.page.locator('input[name="latitude"]').fill("31.2304")
        self.page.locator('input[name="longitude"]').fill("121.4737")
        self.page.locator('input[name="phone"]').fill("02112345678")
        self.submit_first_form()

        self.assert_url_contains("/admin-station")
        self.assertTrue(models.Station.objects.filter(name="E2E created station").exists())
```

- [x] **Step 4: Add volunteer list and create test**

Append to `AdminWebUITests`:

```python
    def test_admin_can_create_and_view_volunteer(self):
        admin = create_grouped_user("e2e_volunteer_admin", "ADMIN")
        _, existing = create_volunteer(username="e2e_existing_volunteer")

        self.login("/adminlogin", admin.username, DEFAULT_PASSWORD)
        self.goto("/admin-volunteer")
        self.assert_page_contains(existing.real_name)

        self.goto("/admin-add-volunteer")
        self.page.locator('input[name="first_name"]').fill("E2E")
        self.page.locator('input[name="last_name"]').fill("Volunteer")
        self.page.locator('input[name="username"]').fill("e2e_created_volunteer")
        self.page.locator('input[name="password"]').fill(DEFAULT_PASSWORD)
        self.page.locator('input[name="real_name"]').fill("E2E Created Volunteer")
        self.page.locator('input[name="mobile"]').fill("13700137001")
        self.submit_first_form()

        self.assert_url_contains("/admin-volunteer")
        self.assertTrue(models.Volunteer.objects.filter(real_name="E2E Created Volunteer").exists())
```

- [x] **Step 5: Run admin E2E tests**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_admin_ui
```

Expected:

```text
OK
```

---

### Task 10: Add Server-Side Method And Role Permission Regression Tests

**Files:**
- Create: `hospital/tests/test_web_method_permissions.py`

- [x] **Step 1: Create method permission test file**

Create `hospital/tests/test_web_method_permissions.py`:

```python
from django.test import TestCase
from django.urls import reverse

from hospital import models
from hospital.tests.helpers import (
    DEFAULT_PASSWORD,
    create_activity,
    create_appointment,
    create_doctor,
    create_grouped_user,
    create_patient,
    create_station,
    create_volunteer,
)


class WebMethodPermissionTests(TestCase):
    def login(self, user):
        self.client.force_login(user)

    def test_admin_mutation_routes_reject_get_requests(self):
        admin = create_grouped_user("method_admin", "ADMIN")
        doctor_user, doctor = create_doctor(username="method_doctor", status=False)
        patient_user, patient = create_patient(username="method_patient", status=False)
        _, appt_doctor = create_doctor(username="method_appt_doctor")
        _, appt_patient = create_patient(username="method_appt_patient", assigned_doctor=appt_doctor)
        appointment = create_appointment(
            patient=appt_patient,
            doctor=appt_doctor,
            description="Method appointment",
            status=False,
        )
        activity = create_activity(name="Method activity")
        station = create_station(name="Method station")
        _, volunteer = create_volunteer(username="method_volunteer", status=False)
        self.login(admin)

        routes = [
            reverse("approve-doctor", args=[doctor.id]),
            reverse("reject-doctor", args=[doctor.id]),
            reverse("delete-doctor-from-hospital", args=[doctor.id]),
            reverse("approve-patient", args=[patient.id]),
            reverse("reject-patient", args=[patient.id]),
            reverse("delete-patient-from-hospital", args=[patient.id]),
            reverse("approve-appointment", args=[appointment.id]),
            reverse("reject-appointment", args=[appointment.id]),
            reverse("delete-activity", args=[activity.id]),
            reverse("delete-station", args=[station.id]),
            reverse("approve-volunteer", args=[volunteer.id]),
            reverse("reject-volunteer", args=[volunteer.id]),
        ]

        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertIn(response.status_code, {302, 405})

        self.assertTrue(models.Doctor.objects.filter(id=doctor.id).exists())
        self.assertTrue(models.User.objects.filter(id=doctor_user.id).exists())
        self.assertTrue(models.Patient.objects.filter(id=patient.id).exists())
        self.assertTrue(models.User.objects.filter(id=patient_user.id).exists())
        self.assertTrue(models.Appointment.objects.filter(id=appointment.id).exists())
        self.assertTrue(models.Activity.objects.filter(id=activity.id).exists())
        self.assertTrue(models.Station.objects.filter(id=station.id).exists())
        self.assertTrue(models.Volunteer.objects.filter(id=volunteer.id).exists())

    def test_doctor_cannot_post_delete_other_doctor_appointment(self):
        doctor_user, doctor = create_doctor(username="method_owner_doctor")
        _, other_doctor = create_doctor(username="method_other_doctor")
        _, patient = create_patient(username="method_other_patient", assigned_doctor=other_doctor)
        appointment = create_appointment(
            patient=patient,
            doctor=other_doctor,
            description="Protected appointment",
            status=True,
        )
        self.login(doctor_user)

        response = self.client.post(reverse("delete-appointment", args=[appointment.id]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(models.Appointment.objects.filter(id=appointment.id).exists())

    def test_role_pages_redirect_when_logged_in_as_wrong_role(self):
        doctor_user, _ = create_doctor(username="method_wrong_role_doctor")
        patient_user, _ = create_patient(username="method_wrong_role_patient")
        admin = create_grouped_user("method_wrong_role_admin", "ADMIN")

        cases = [
            (doctor_user, "/admin-dashboard"),
            (patient_user, "/doctor-dashboard"),
            (admin, "/patient-dashboard"),
        ]

        for user, path in cases:
            with self.subTest(user=user.username, path=path):
                self.client.logout()
                self.login(user)
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
```

- [x] **Step 2: Run method permission tests**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.test_web_method_permissions
```

Expected:

```text
Ran 3 tests
OK
```

If a route returns a deliberate `403` instead of `302` or `405`, include `403` in the allowed set and document why in the test name or assertion message.

---

### Task 11: Update Scripts, Docs, And Run Full Verification

**Files:**
- Create: `scripts/check_webui_e2e.sh`
- Modify: `scripts/check_webui.sh`
- Modify: `docs/webui-testing.md`

- [x] **Step 1: Add E2E-only script**

Create `scripts/check_webui_e2e.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

.venv/bin/python manage.py test hospital.tests.e2e
```

- [x] **Step 2: Make E2E script executable**

Run:

```bash
chmod +x scripts/check_webui_e2e.sh
```

Expected:

```text
scripts/check_webui_e2e.sh is executable
```

Verify with:

```bash
test -x scripts/check_webui_e2e.sh && echo "scripts/check_webui_e2e.sh is executable"
```

- [x] **Step 3: Keep full suite script focused**

Ensure `scripts/check_webui.sh` remains:

```bash
#!/usr/bin/env bash
set -euo pipefail

.venv/bin/python manage.py test hospital.tests
```

- [x] **Step 4: Update WebUI testing docs**

Add this section to `docs/webui-testing.md`:

```markdown
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

只运行服务端 Web 权限回归：

```bash
.venv/bin/python manage.py test hospital.tests.test_web_review_fixes hospital.tests.test_web_method_permissions
```
```

- [x] **Step 5: Run module tests**

Run:

```bash
.venv/bin/python manage.py test hospital.tests.e2e.test_public_ui
.venv/bin/python manage.py test hospital.tests.e2e.test_auth_ui
.venv/bin/python manage.py test hospital.tests.e2e.test_admin_ui
.venv/bin/python manage.py test hospital.tests.e2e.test_doctor_ui
.venv/bin/python manage.py test hospital.tests.e2e.test_patient_ui
.venv/bin/python manage.py test hospital.tests.test_web_method_permissions
```

Expected for each command:

```text
OK
```

- [x] **Step 6: Run full verification**

Run:

```bash
./scripts/check_webui_e2e.sh
./scripts/check_webui.sh
git diff --check
git status --short
```

Expected:

```text
OK
```

for both scripts, no output from `git diff --check`, and `git status --short` showing only files touched by this plan.

- [x] **Step 7: Stop before commit**

Do not commit. Report:

- number of E2E tests after expansion,
- total `hospital.tests` count,
- all verification commands and results,
- changed files,
- any intentionally deferred coverage.

---

## Execution Order

1. Task 1 must run first because later tasks use the new helpers.
2. Tasks 2-6 can run independently after Task 1.
3. Task 7 depends on Task 1 and should run after doctor/patient/admin tests are stable.
4. Task 8 depends on Task 1 and can run after admin/patient tests are stable.
5. Task 9 depends on Task 1 and can run independently.
6. Task 10 can run after Task 1.
7. Task 11 must run last.

## Self-Review

- Spec coverage: covers P0/P1 public, auth, admin, doctor, patient, records, discharge, activity, station, volunteer, and server-side permission regressions.
- Placeholder scan: no unfinished placeholder markers or vague future-work wording remains in executable steps.
- Type consistency: helper names used by later tasks are defined in Task 1; paths match existing URL names in `hospitalmanagement/urls.py`.
- Scope check: multi-browser, visual diff, performance, accessibility, and Mini Program E2E are intentionally deferred.
