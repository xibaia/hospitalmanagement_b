# Graph Report - .  (2026-04-09)

## Corpus Check
- 56 files · ~112,966 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 566 nodes · 1659 edges · 39 communities detected
- Extraction: 31% EXTRACTED · 69% INFERRED · 0% AMBIGUOUS · INFERRED: 1149 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `Doctor` - 60 edges
2. `Patient` - 60 edges
3. `MedicalRecord` - 57 edges
4. `MedicalHistory` - 56 edges
5. `Activity` - 56 edges
6. `ActivityParticipant` - 56 edges
7. `Station` - 56 edges
8. `ActivityDetailSerializer` - 41 edges
9. `PatientRegistrationSerializer` - 39 edges
10. `MedicalRecordListSerializer` - 39 edges

## Surprising Connections (you probably didn't know these)
- `Patient 模型` --semantically_similar_to--> `Patient 患者模型`  [INFERRED] [semantically similar]
  CLAUDE.md → 需求文档.md
- `病历内容结构` --semantically_similar_to--> `MedicalRecord 病历模型`  [INFERRED] [semantically similar]
  需求草稿.md → 需求文档.md
- `MedicalRecord 模型` --semantically_similar_to--> `MedicalRecord 病历模型`  [INFERRED] [semantically similar]
  CLAUDE.md → 需求文档.md
- `API 安全认证` --semantically_similar_to--> `Token Authentication`  [INFERRED] [semantically similar]
  CLAUDE.md → API_Documentation.md
- `API 限流策略` --semantically_similar_to--> `登录接口限流修复`  [INFERRED] [semantically similar]
  API_Documentation.md → PROGRESS.md

## Hyperedges (group relationships)
- **医院管理系统** — readme_hospital_system, claude_architecture, api_docs_rest_api, reqdoc_patient_model, reqdoc_doctor_model, reqdoc_medical_record [INFERRED 0.90]
- **REST API 架构** — api_docs_rest_api, api_docs_token_auth, api_docs_patient_login, api_docs_doctor_login, requirements_drf, claude_security [INFERRED 0.90]
- **病历系统** — reqdoc_medical_record, reqdoc_tooth_finding, reqdoc_fdi_tooth_number, admin_ui_plan_medical_record, admin_ui_plan_doctor_record, admin_ui_plan_fdi_tooth [INFERRED 0.90]
- **安全修复集合** — progress_security_fixes, progress_secret_key_fix, progress_rate_limit_fix, progress_doctor_privilege_fix, claude_security [INFERRED 0.85]
- **部署问题集合** — troubleshooting_pip_timeout, troubleshooting_pkg_resources, troubleshooting_freetype, troubleshooting_pdf_generation, requirements_pdf [INFERRED 0.85]
- **HL7 标准合规** — reqdoc_hl7_standard, reqdraft_hl7_segments, reqdoc_patient_model, reqdoc_medical_record [INFERRED 0.80]

## Communities

### Community 0 - "API接口文档"
Cohesion: 0.19
Nodes (63): 获取当前登录患者信息API          需要在请求头中包含: Authorization: Token 9944b09199c62bcf9418ad846, 获取可用医生列表API          返回:     {         "success": true,         "message": "获取成功, 患者登出API          需要在请求头中包含: Authorization: Token 9944b09199c62bcf9418ad846dd0e4b, 更新患者信息API          请求参数:     {         "mobile": "13800138001",         "address, 患者绑定医生API（通过扫码）          请求参数:     {         "doctor_id": 1  // 医生的user_id     }, 患者注册API          请求参数:     {         "first_name": "张",         "last_name": "三", 医生登录API      请求参数:     {         "username": "doctor1",         "password": "123, 获取当前患者的病历列表API      需要在请求头中包含: Authorization: Token xxx      返回:     {         " (+55 more)

### Community 1 - "Web视图层"
Cohesion: 0.03
Nodes (6): afterlogin_view(), download_pdf_view(), is_admin(), is_doctor(), is_patient(), render_to_pdf()

### Community 2 - "jQuery v3.3.1"
Cohesion: 0.07
Nodes (45): a(), ae(), be(), C(), ce(), ct(), de(), Ee() (+37 more)

### Community 3 - "jQuery v3.5.1"
Cohesion: 0.08
Nodes (35): A(), Ae(), b(), be(), Bt(), ce(), D(), Dt() (+27 more)

### Community 4 - "jQuery v1.10.2"
Cohesion: 0.07
Nodes (34): an(), at(), bt(), ct(), er(), gn(), ht(), I() (+26 more)

### Community 5 - "UI界面设计"
Cohesion: 0.07
Nodes (33): 医生病历工作台, FDI 牙位图界面, 病历管理界面, 义诊活动接口, 医生登录接口, 病历管理接口, 患者登录接口, 患者注册接口 (+25 more)

### Community 6 - "API视图层"
Cohesion: 0.08
Nodes (27): activities_list_api(), _activity_annotate(), activity_detail_api(), activity_join_api(), activity_leave_api(), bind_doctor_api(), doctor_confirm_record_api(), doctor_login_api() (+19 more)

### Community 7 - "Popper.js"
Cohesion: 0.27
Nodes (25): a(), b(), c(), d(), e(), f(), g(), h() (+17 more)

### Community 8 - "Django表单"
Cohesion: 0.11
Nodes (17): ActivityForm, AdminSigupForm, AppointmentForm, ContactusForm, DoctorForm, DoctorUserForm, DoctorUserUpdateForm, MedicalRecordForm (+9 more)

### Community 9 - "Django管理后台"
Cohesion: 0.16
Nodes (9): AppointmentAdmin, DoctorAdmin, PatientAdmin, PatientDischargeDetailsAdmin, Appointment, DoctorSpecialty, Meta, PatientDischargeDetails (+1 more)

### Community 10 - "API测试"
Cohesion: 0.25
Nodes (2): APITester, main()

### Community 11 - "系统架构"
Cohesion: 0.15
Nodes (13): Django 双界面架构, 双 URL 架构 Web/API, 角色权限系统, 单 App 结构, 数据库策略 SQLite/PostgreSQL, Django 框架, Docker 支持, 环境变量配置 (+5 more)

### Community 12 - "Bootstrap 4"
Cohesion: 0.24
Nodes (3): i(), s(), Se()

### Community 13 - "Bootstrap 3"
Cohesion: 0.54
Nodes (7): e(), i(), l(), n(), r(), s(), u()

### Community 14 - "业务模型设计"
Cohesion: 0.33
Nodes (6): 义诊活动管理界面, Doctor 模型, Activity 义诊活动模型, Doctor 医生模型, 医生字段定义, 口腔专业分类

### Community 15 - "患者激活脚本"
Cohesion: 0.83
Nodes (3): activate_all_patients(), activate_latest_patient(), main()

### Community 16 - "模型方法"
Cohesion: 0.5
Nodes (0): 

### Community 17 - "UI截图"
Cohesion: 0.5
Nodes (4): Admin Dashboard UI, Admin Doctor List View, Admin Doctor Management UI Screenshot, Doctor Model

### Community 18 - "序列化器"
Cohesion: 0.67
Nodes (0): 

### Community 19 - "App配置"
Cohesion: 0.67
Nodes (2): AppConfig, HospitalConfig

### Community 20 - "模板过滤器"
Cohesion: 0.67
Nodes (0): 

### Community 21 - "PDF生成"
Cohesion: 0.67
Nodes (3): xhtml2pdf PDF生成, Freetype 库缺失问题, PDF 生成功能受限

### Community 22 - "Django管理"
Cohesion: 1.0
Nodes (0): 

### Community 23 - "医生组修复"
Cohesion: 1.0
Nodes (0): 

### Community 24 - "ASGI配置"
Cohesion: 1.0
Nodes (1): ASGI config for hospitalmanagement project.  It exposes the ASGI callable as a m

### Community 25 - "Django设置"
Cohesion: 1.0
Nodes (1): Django settings for hospitalmanagement project.  Generated by 'django-admin star

### Community 26 - "URL路由"
Cohesion: 1.0
Nodes (1): Developed By : sumit kumar facebook : fb.com/sumit.luv

### Community 27 - "WSGI配置"
Cohesion: 1.0
Nodes (1): WSGI config for hospitalmanagement project.  It exposes the WSGI callable as a m

### Community 28 - "数据库迁移0002"
Cohesion: 1.0
Nodes (1): Migration

### Community 29 - "数据库迁移0004"
Cohesion: 1.0
Nodes (1): Migration

### Community 30 - "数据库迁移0003"
Cohesion: 1.0
Nodes (1): Migration

### Community 31 - "数据库迁移0001"
Cohesion: 1.0
Nodes (1): Migration

### Community 32 - "Python包"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "API路由"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "部署问题"
Cohesion: 1.0
Nodes (1): pip 安装超时问题

### Community 35 - "站点模型"
Cohesion: 1.0
Nodes (1): Station 筛查站点模型

### Community 36 - "志愿者管理"
Cohesion: 1.0
Nodes (1): 志愿者管理界面

### Community 37 - "站点管理"
Cohesion: 1.0
Nodes (1): 站点管理界面

### Community 38 - "FontAwesome"
Cohesion: 1.0
Nodes (1): FontAwesome Webfont

## Knowledge Gaps
- **67 isolated node(s):** `ASGI config for hospitalmanagement project.  It exposes the ASGI callable as a m`, `Django settings for hospitalmanagement project.  Generated by 'django-admin star`, `Developed By : sumit kumar facebook : fb.com/sumit.luv`, `WSGI config for hospitalmanagement project.  It exposes the WSGI callable as a m`, `Meta` (+62 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Django管理`** (2 nodes): `manage.py`, `main()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `医生组修复`** (2 nodes): `fix_doctor_groups.py`, `fix_doctor_groups()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `ASGI配置`** (2 nodes): `asgi.py`, `ASGI config for hospitalmanagement project.  It exposes the ASGI callable as a m`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Django设置`** (2 nodes): `settings.py`, `Django settings for hospitalmanagement project.  Generated by 'django-admin star`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `URL路由`** (2 nodes): `urls.py`, `Developed By : sumit kumar facebook : fb.com/sumit.luv`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `WSGI配置`** (2 nodes): `wsgi.py`, `WSGI config for hospitalmanagement project.  It exposes the WSGI callable as a m`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `数据库迁移0002`** (2 nodes): `0002_remove_doctor_specialties_alter_medicalrecord_doctor.py`, `Migration`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `数据库迁移0004`** (2 nodes): `0004_alter_patient_assigneddoctorid_and_more.py`, `Migration`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `数据库迁移0003`** (2 nodes): `0003_remove_appointment_doctorid_and_more.py`, `Migration`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `数据库迁移0001`** (2 nodes): `0001_initial.py`, `Migration`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Python包`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `API路由`** (1 nodes): `api_urls.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `部署问题`** (1 nodes): `pip 安装超时问题`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `站点模型`** (1 nodes): `Station 筛查站点模型`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `志愿者管理`** (1 nodes): `志愿者管理界面`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `站点管理`** (1 nodes): `站点管理界面`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `FontAwesome`** (1 nodes): `FontAwesome Webfont`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Doctor` connect `API接口文档` to `Django管理后台`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **Why does `Patient` connect `API接口文档` to `Django管理后台`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **Are the 58 inferred relationships involving `Doctor` (e.g. with `PatientRegistrationSerializer` and `Meta`) actually correct?**
  _`Doctor` has 58 INFERRED edges - model-reasoned connections that need verification._
- **Are the 58 inferred relationships involving `Patient` (e.g. with `PatientRegistrationSerializer` and `Meta`) actually correct?**
  _`Patient` has 58 INFERRED edges - model-reasoned connections that need verification._
- **Are the 54 inferred relationships involving `MedicalRecord` (e.g. with `PatientRegistrationSerializer` and `Meta`) actually correct?**
  _`MedicalRecord` has 54 INFERRED edges - model-reasoned connections that need verification._
- **Are the 54 inferred relationships involving `MedicalHistory` (e.g. with `PatientRegistrationSerializer` and `Meta`) actually correct?**
  _`MedicalHistory` has 54 INFERRED edges - model-reasoned connections that need verification._
- **Are the 54 inferred relationships involving `Activity` (e.g. with `PatientRegistrationSerializer` and `Meta`) actually correct?**
  _`Activity` has 54 INFERRED edges - model-reasoned connections that need verification._