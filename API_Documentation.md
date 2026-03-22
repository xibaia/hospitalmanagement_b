# 医院管理系统 API 接口文档

> 更新时间：2026-03-22 | 版本：v2.0（含医生端、病历、活动、站点全部接口）

## 基础信息

| 项目 | 说明 |
|------|------|
| 服务器地址 | `http://127.0.0.1:8000` |
| API 基础路径 | `/api/` |
| 认证方式 | Token Authentication |
| 请求头格式 | `Authorization: Token <token>` |
| 响应格式 | JSON，统一包裹 `{"success": bool, "data": ..., "message": "..."}` |

---

## 一、患者端接口

### 1. 注册
`POST /api/patient/register/` — 无需认证

```json
// 请求
{
    "first_name": "张", "last_name": "三",
    "username": "zhangsan", "password": "pass123456", "confirm_password": "pass123456",
    "mobile": "13800138000", "address": "北京市朝阳区",
    "symptoms": "牙痛", "assigned_doctor_id": 1  // 可选
}
// 响应
{"success": true, "message": "注册成功，请等待管理员审核", "data": {"user_id": 1, "username": "zhangsan"}}
```

### 2. 登录
`POST /api/patient/login/` — 无需认证

```json
// 请求
{"username": "zhangsan", "password": "pass123456"}
// 响应
{"success": true, "data": {"token": "abc123...", "user_info": {...}, "patient_info": {...}}}
```

### 3. 登出
`POST /api/patient/logout/` — 需 Token

```json
{"success": true, "message": "登出成功"}
```

### 4. 获取患者信息
`GET /api/patient/info/` — 需 Token

### 5. 更新患者信息
`PUT /api/patient/update/` — 需 Token

```json
// 请求（字段均可选）
{"mobile": "13900139000", "address": "上海市浦东新区", "symptoms": "发烧"}
```

### 6. 绑定医生（扫码）
`POST /api/patient/bind-doctor/` — 需 Token

```json
// 请求
{"doctor_id": 1}
// 响应
{"success": true, "data": {"doctor_name": "李医生", "department": "全科"}}
```

### 7. 病历列表
`GET /api/patient/records/` — 需 Token

### 8. 病历详情
`GET /api/patient/records/<pk>/` — 需 Token

### 9. 既往病史（查看/更新）
`GET /api/patient/medical-history/` — 需 Token
`PUT /api/patient/medical-history/` — 需 Token

```json
// PUT 请求（字段均可选）
{
    "hypertension": true, "heart_disease": false,
    "medications": "阿司匹林", "allergies": "青霉素"
}
```

---

## 二、医生端接口

### 1. 登录
`POST /api/doctor/login/` — 无需认证

```json
// 请求
{"username": "doctor1", "password": "pass123456"}
// 响应
{"success": true, "data": {"token": "abc123...", "user_info": {...}, "doctor_info": {...}}}
```

### 2. 登出
`POST /api/doctor/logout/` — 需 Token（医生账户）

### 3. 患者列表
`GET /api/doctor/patients/` — 需 Token（医生）
`GET /api/doctor/patients/?search=张三` — 支持按姓名/手机号搜索

```json
// 响应
{"success": true, "data": [{"id":1, "name":"张三", "gender":"M", "mobile":"138...", "record_count":3}]}
```

### 4. 患者详情
`GET /api/doctor/patients/<pk>/` — 需 Token（医生）
> 只能查看：分配给自己的患者 OR 自己有病历的患者

```json
// 响应包含：基本信息 + 既往病史 + 最近5条病历
{"success": true, "data": {"name":"张三", "medical_history":{...}, "recent_records":[...]}}
```

### 5. 病历列表 / 创建病历
`GET /api/doctor/records/` — 查看自己负责的病历，支持 `?activity_id=` 过滤
`POST /api/doctor/records/` — 创建病历

```json
// POST 请求
{
    "patient": 1, "activity": 1, "check_date": "2026-03-22", "visit_type": "charity",
    "chief_complaint": "牙痛3天", "diagnosis": "龋齿",
    "tooth_findings": [{"tooth_number": 16, "finding_type": "caries", "note": "深龋"}]
}
```

### 6. 病历详情 / 更新
`GET /api/doctor/records/<pk>/` — 查看
`PUT /api/doctor/records/<pk>/` — 更新（已确认的不可修改）

### 7. 确认病历
`POST /api/doctor/records/<pk>/confirm/` — 需 Token（医生）

```json
{"success": true, "message": "病历确认成功", "data": {"confirmed_at": "2026-03-22T10:00:00"}}
```

---

## 三、义诊活动接口

### 1. 活动列表
`GET /api/activities/` — 需 Token
- 患者：只返回 `status=active` 的活动
- 医生：返回全部（含草稿、已结束）

### 2. 活动详情
`GET /api/activities/<pk>/` — 需 Token
- 患者：不返回参与者名单，只返回人数
- 医生：返回完整参与者名单

### 3. 报名活动
`POST /api/activities/<pk>/join/` — 需 Token

```json
// 请求
{"role": "volunteer"}  // 医生可传 "doctor"，其他账户强制 "volunteer"
```

### 4. 取消报名
`DELETE /api/activities/<pk>/leave/` — 需 Token（活动已结束不可取消）

### 5. 我的报名记录
`GET /api/activities/mine/` — 需 Token

---

## 四、公共接口

### 医生列表
`GET /api/doctors/` — 无需认证，返回已审批医生

### 义诊站点列表
`GET /api/stations/` — 需 Token，返回启用中的站点（含经纬度）

---

## 五、错误码

| 状态码 | 含义 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未提供 Token 或 Token 无效 |
| 403 | 权限不足（角色不匹配或账户未审批）|
| 404 | 资源不存在或无权访问 |
| 429 | 请求频率超限（匿名 30/min，登录用户 300/min）|
| 500 | 服务器内部错误 |

---

## 六、注意事项

1. 所有需要认证的接口请求头必须携带 `Authorization: Token <token>`
2. 患者和医生注册后需要**管理员审批**才能登录（`status=True`）
3. 手机号格式：11位纯数字
4. 密码最短 6 位
5. 病历一旦医生确认（`doctor_confirmed=true`），不允许再修改
6. 义诊活动仅 `status=active` 时才可报名
7. 生产部署时将 `127.0.0.1:8000` 替换为实际域名，并在 `.env` 配置 `CORS_ALLOWED_ORIGINS`
