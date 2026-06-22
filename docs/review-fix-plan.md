# Code Review 修复计划

> 创建时间：2026-06-22
> 范围：仅处理本轮 review 中的 3、4、5、6；暂不处理医生病历对象越权和预约删除越权。

## 目标

修复已确认的角色审批态绕过、活动接口旧 token 权限、管理端 POST 模板不匹配、医生确认病历控件无效问题，并补充回归测试。

## 修复项

| 序号 | 问题 | 修改策略 | 主要文件 |
|------|------|----------|----------|
| 3 | 未审批医生/患者可直接访问 Web 角色页面 | `is_doctor` / `is_patient` 改为同时校验 group 和业务模型 `status=True`；新增纯 group 判断供 `afterlogin` 显示等待审批页 | `hospital/views/common.py`, `hospital/views/public.py` |
| 4 | 未审批医生旧 token 仍获得活动医生权限 | `user_is_doctor` 改为复用已审批医生判断；活动列表/详情/报名自动按非医生权限降级 | `hospital/api/common.py`, `hospital/api/activity.py` |
| 5 | 管理端视图已要求 POST，但模板仍用 GET 链接 | 将审批、拒绝、删除类按钮改为带 CSRF 的 POST 表单，保持原按钮样式 | `templates/hospital/admin_*.html` |
| 6 | 医生确认病历控件无效 | 将 `doctor_confirmed` 加入 `MedicalRecordForm`，让 Web 表单能保存确认状态和首次确认时间 | `hospital/forms.py`, `hospital/views/doctor.py` |

## 测试计划

1. Web 权限测试：
   - 未审批医生直接访问 `/doctor-dashboard` 不应返回 200。
   - 未审批医生访问 `/afterlogin` 仍显示等待审批页。
2. 活动 API 测试：
   - 未审批医生 token 访问草稿活动详情应返回 404。
   - 未审批医生报名时传 `doctor` 应被降级为 `volunteer`。
3. 管理端模板/视图测试：
   - GET 审批医生不改变状态。
   - POST 审批医生可以改变状态。
   - 审批页包含 CSRF POST 表单。
4. 医生确认病历测试：
   - `MedicalRecordForm` 包含 `doctor_confirmed`。
   - 医生通过 Web 更新病历勾选确认后，`doctor_confirmed=True` 且 `confirmed_at` 被写入。

## 验证命令

```bash
python manage.py check
python manage.py migrate --check
python manage.py makemigrations --check --dry-run
python manage.py test
python -m pip check
git diff --check
```

## 执行记录

| 项目 | 状态 |
|------|------|
| Web 角色审批态校验 | 已完成 |
| 活动接口已审批医生判断 | 已完成 |
| 管理端 POST 表单同步 | 已完成 |
| 医生确认病历表单修复 | 已完成 |
| 回归测试 | 已补充并通过，最终测试数 `28 tests` |
