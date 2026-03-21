# 新模型管理界面开发计划

> 创建时间：2026-03-21
> 状态：Phase 1-6 已完成（2026-03-21）

---

## 背景

为口腔筛查小程序后端新增的数据模型（Activity、MedicalRecord、Station、Volunteer、MedicalHistory、ToothFinding）开发 Web 管理界面，供管理员/医生在后台操作数据，小程序端通过 REST API 消费数据。

---

## 页面清单

### 管理员侧（Admin Dashboard 扩展）

| 模块 | 页面 | URL | 状态 |
|------|------|-----|------|
| 义诊活动 | 列表 | `/admin-activity` | ✅ 已完成 |
| | 新增 | `/admin-add-activity` | ✅ 已完成 |
| | 编辑 | `/update-activity/<pk>` | ✅ 已完成 |
| | 详情（含参与者列表） | `/admin-view-activity/<pk>` | ✅ 已完成 |
| 志愿者 | 列表 + 待审批 | `/admin-volunteer` | ✅ 已完成 |
| | 新增 | `/admin-add-volunteer` | ✅ 已完成 |
| | 审批 | `/approve-volunteer/<pk>` | ✅ 已完成 |
| | 拒绝 | `/reject-volunteer/<pk>` | ✅ 已完成 |
| 站点 | 列表 | `/admin-station` | ✅ 已完成 |
| | 新增 | `/admin-add-station` | ✅ 已完成 |
| | 编辑 | `/update-station/<pk>` | ✅ 已完成 |
| 病历 | 列表（只读） | `/admin-medical-records` | ✅ 已完成 |
| | 详情（只读） | `/admin-view-record/<pk>` | ✅ 已完成 |

### 医生侧（Doctor Dashboard 扩展）

| 模块 | 页面 | URL | 状态 |
|------|------|-----|------|
| 病历 | 我的病历列表 | `/doctor-records` | ✅ 已完成 |
| | 新建病历（含牙位内联） | `/doctor-create-record` | ✅ 已完成 |
| | 编辑 / 确认病历 | `/doctor-update-record/<pk>` | ✅ 已完成 |

> **说明**
> - `ToothFinding` 作为 formset 内联在病历编辑页，不单独做页面
> - `MedicalHistory` 内联在现有患者详情页（`/admin-view-patient` 扩展）

---

## 入口位置

```
admin-dashboard
  ├── 现有：医生管理 / 患者管理 / 预约管理
  └── 新增卡片：
      ├── 义诊活动管理  →  /admin-activity
      ├── 志愿者管理    →  /admin-volunteer
      ├── 站点管理      →  /admin-station
      └── 病历查看      →  /admin-medical-records

doctor-dashboard
  └── 新增卡片：
      └── 我的病历      →  /doctor-records
```

---

## 实现阶段

| 阶段 | 内容 | 状态 |
|------|------|------|
| Phase 1 | 义诊活动管理（Activity + ActivityParticipant） | ✅ 已完成 |
| Phase 2 | 志愿者管理（Volunteer） | ✅ 已完成 |
| Phase 3 | 站点管理（Station） | ✅ 已完成 |
| Phase 4 | 病历管理（MedicalRecord + ToothFinding formset） | ✅ 已完成 |
| Phase 5 | 患者病史内联（MedicalHistory，扩展现有患者详情页） | ✅ 已完成 |
| Phase 6 | Dashboard 入口卡片更新 | ✅ 已完成 |

---

## 技术约定

- 模板继承现有 Bootstrap 风格，放在 `templates/hospital/` 下
- 视图函数写在 `hospital/views.py`，按角色分区注释
- URL 追加到 `hospitalmanagement/urls.py` 对应区块
- 表单写在 `hospital/forms.py`
- 牙位图（FDI 32颗牙）使用自定义 HTML + JS 渲染，formset 提交

---

## 风险

| 级别 | 描述 |
|------|------|
| MEDIUM | 病历页牙位图（FDI 32颗牙）需自定义 UI，formset 较复杂 |
| LOW | 现有模板风格需保持一致（Bootstrap） |
