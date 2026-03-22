# 项目问题修复进度
> 更新时间：2026-03-22（第三轮分析修复完成，所有已知问题已全部清零）

## 高危问题（优先修复）

| # | 文件 | 行号 | 问题 | 状态 |
|---|------|------|------|------|
| 1 | settings.py:26 | SECRET_KEY 弱默认值已在仓库公开 | ✅ 已修复 |
| 2 | settings.py:127 | 时区 UTC，义诊活动时间差8小时 | ✅ 已修复 |
| 3 | settings.py:146 | 登录接口无限流，可暴力破解 | ✅ 已修复 |
| 4 | api_views.py:812 | 医生可越权查任意患者详情 | ✅ 已修复 |
| 5 | serializers.py:419 | 身份证号 id_card 对所有医生可见 | ✅ 已修复 |
| 6 | models.py:331 | visit_no 生成竞态条件，并发时报错 | ✅ 已修复 |
| 7 | serializers.py:131/404 | N+1 查询（患者医生名、病历数量） | ✅ 已修复 |
| 8 | serializers.py:238/280 | get_doctor_name 方法完全重复 | ✅ 已修复 |

## 中危问题（下一步处理）

| # | 文件 | 行号 | 问题 | 状态 |
|---|------|------|------|------|
| 9 | api_views.py:299 | 更新患者信息绕过 Serializer 校验 | ✅ 已修复 |
| 10 | api_views.py:794 | 搜索用 \| 拼 QuerySet 不稳定，应改用 Q() | ✅ 已修复 |
| 11 | api_views.py:700 | 报名并发竞态，应改用 get_or_create | ✅ 已修复 |
| 12 | settings.py:143 | MEDIA_ROOT 与 STATIC 混用 | ✅ 已修复 |
| 13 | settings.py | 缺少 CORS 配置（小程序调用需要） | ✅ 已修复 |
| 14 | models.py:94 | DoctorSpecialty M2M 关系声明错误 | ✅ 已修复 |
| 15 | views.py:689 | 用姓名字符串关联出院记录 | ✅ 已修复 |

## 第二轮分析新增问题（已修复）

| # | 文件 | 问题 | 状态 |
|---|------|------|------|
| H1 | models.py | visit_no 重试机制替换 select_for_update（SQLite 兼容）| ✅ 已修复 |
| M1 | api_views.py | doctor_patient_detail_api MultipleObjectsReturned | ✅ 已修复 |
| M2 | serializers.py | ActivityDetailSerializer is_joined 优先读 annotate | ✅ 已修复 |
| L1 | serializers.py | 注册手机号无格式校验 | ✅ 已修复 |
| L2 | settings.py | CORS 默认改为 False | ✅ 已修复 |
| L4 | settings.py | EMAIL 明文改读环境变量 | ✅ 已修复 |

## 低危问题（有空处理）

| # | 文件 | 问题 | 状态 |
|---|------|------|------|
| 16 | settings.py:28 | DEBUG 默认 True | ✅ 已修复（改 False）|
| 17 | api_urls.py | 路由命名不统一 | ✅ 已修复 |

## 第三轮分析新增问题（2026-03-22）

| # | 文件 | 问题 | 状态 |
|---|------|------|------|
| H1 | views.py | download_pdf_view 无认证 | ✅ 已修复 |
| H2 | views.py | patient_view_doctor_view / search_doctor_view 无认证 | ✅ 已修复 |
| H3 | views.py | search_doctor_view GET['query'] KeyError | ✅ 已修复 |
| H4 | views.py | assignedDoctorId 三处写入未校验合法性 | ✅ 已修复 |
| H5 | views.py | doctor_records/create_record 给 FK(Doctor) 赋值 User 对象 | ✅ 已修复 |
| M1 | views.py | print(patientDict) PII 泄露到日志 | ✅ 已修复 |
| M2 | views.py | delete_doctor/patient GET 请求 CSRF | ✅ 已修复 |
| M3 | serializers.py | PatientDetailSerializer.get_recent_records 缺 select_related | ✅ 已修复 |
| M4 | api_views.py | activity_detail_api 患者可查草稿活动 | ✅ 已修复 |
| M5 | views.py | discharge_patient_view assignedDoctor[0] IndexError | ✅ 已修复 |
| M6 | views.py | patient_view_record_view 对 Doctor FK 做额外查询 | ✅ 已修复 |
| L1 | api_views.py | _check_doctor 死代码别名 | ✅ 已修复 |
| L2 | models.py | DoctorSpecialty 缺 unique_together | ✅ 已修复（迁移 0004）|
| L3 | settings.py | 缺生产安全头 | ✅ 已修复 |
| L4 | settings.py | DEBUG 默认 True | ✅ 已修复 |
| L5 | api_urls.py | record vs records 路径不一致 | ✅ 已修复 |
| L6 | models.py | assignedDoctorId 无索引 | ✅ 已修复（迁移 0004）|
| L7 | api_urls.py | doctor/logout 无 doctor_required | ✅ 已修复 |

## 第四轮分析新增问题（2026-03-22）

| # | 文件 | 问题 | 状态 |
|---|------|------|------|
| H1 | views.py | patient_dashboard_view Doctor.get() 在 assignedDoctorId=None 时崩溃 | ✅ 已修复（改 filter().first() + None guard）|
| H2 | views.py | 10处 approve/reject/delete 操作接受 GET 请求（CSRF）| ✅ 已修复（统一加 POST guard）|
| H3 | views.py/forms.py | update_doctor/patient_view 用含 password 的 Form，save() 覆盖密码 | ✅ 已修复（新增 DoctorUserUpdateForm / PatientUserUpdateForm）|
| M1 | serializers.py | PatientInfoSerializer N+1 查询 | ⬜ 待修 |
| M3 | api_views.py | doctor_update_record_api 缺所有权校验 | ⬜ 待修 |
| M4 | api_views.py | 多处 get() 缺 404 保护 | ⬜ 待修 |
| M5 | serializers.py | MedicalRecordCreateSerializer patient 无所有权校验 | ⬜ 待修 |
| M6 | api_views.py | 分页配置不生效 | ⬜ 待修 |
| L1 | views.py | PDF 中文乱码（ISO-8859-1）| ⬜ 待修 |
| L2 | serializers.py | symptoms/address required=False 未设 | ⬜ 待修 |
| L4 | serializers.py | ToothFinding tooth_number 无范围校验 | ⬜ 待修 |

## 架构级问题（需单独评估）

| # | 文件 | 问题 | 状态 |
|---|------|------|------|
| A1 | models.py:284 | MedicalRecord.doctor FK 到 User 而非 Doctor（N+1 根源） | ✅ 已修复（迁移 0002）|
| A2 | models.py:393 | Appointment/PatientDischargeDetails 用裸整数代替外键 | ✅ 已修复（迁移 0003）|
| A3 | api_views.py:758 | 医生权限靠手动调函数，应改为装饰器 | ✅ 已修复 |
