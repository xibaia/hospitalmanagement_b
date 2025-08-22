# 医院管理系统 API 接口文档

## 基础信息
- 服务器地址: `http://127.0.0.1:8000`
- API 基础路径: `/api/`
- 认证方式: Token Authentication

## 患者相关接口

### 1. 患者注册
**接口地址:** `POST /api/patient/register/`

**请求参数:**
```json
{
    "first_name": "张",
    "last_name": "三",
    "username": "zhangsan",
    "password": "password123",
    "address": "北京市朝阳区",
    "mobile": "13800138000",
    "symptoms": "头痛",
    "assignedDoctorId": 1
}
```

**响应示例:**
```json
{
    "message": "患者注册成功",
    "patient_id": 1,
    "username": "zhangsan"
}
```

### 2. 患者登录
**接口地址:** `POST /api/patient/login/`

**请求参数:**
```json
{
    "username": "zhangsan",
    "password": "password123"
}
```

**响应示例:**
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "patient_id": 1,
    "message": "登录成功"
}
```

### 3. 获取患者信息
**接口地址:** `GET /api/patient/info/`

**请求头:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**响应示例:**
```json
{
    "id": 1,
    "user": {
        "first_name": "张",
        "last_name": "三",
        "username": "zhangsan"
    },
    "address": "北京市朝阳区",
    "mobile": "13800138000",
    "symptoms": "头痛",
    "assigned_doctor_name": "李医生",
    "admit_date": "2025-07-20",
    "status": true
}
```

### 4. 更新患者信息
**接口地址:** `PUT /api/patient/update/`

**请求头:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**请求参数:**
```json
{
    "address": "上海市浦东新区",
    "mobile": "13900139000",
    "symptoms": "发烧"
}
```

**响应示例:**
```json
{
    "message": "患者信息更新成功"
}
```

### 5. 患者登出
**接口地址:** `POST /api/patient/logout/`

**请求头:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**响应示例:**
```json
{
    "message": "登出成功"
}
```

### 6. 获取医生列表
**接口地址:** `GET /api/doctors/`

**响应示例:**
```json
[
    {
        "id": 1,
        "user": {
            "first_name": "李",
            "last_name": "医生"
        },
        "department": "内科",
        "mobile": "13700137000"
    }
]
```

## 小程序集成示例

### 微信小程序示例代码

#### 患者注册
```javascript
wx.request({
  url: 'http://127.0.0.1:8000/api/patient/register/',
  method: 'POST',
  header: {
    'content-type': 'application/json'
  },
  data: {
    first_name: '张',
    last_name: '三',
    username: 'zhangsan',
    password: 'password123',
    address: '北京市朝阳区',
    mobile: '13800138000',
    symptoms: '头痛',
    assignedDoctorId: 1
  },
  success: function(res) {
    console.log('注册成功:', res.data);
  },
  fail: function(err) {
    console.error('注册失败:', err);
  }
});
```

#### 患者登录
```javascript
wx.request({
  url: 'http://127.0.0.1:8000/api/patient/login/',
  method: 'POST',
  header: {
    'content-type': 'application/json'
  },
  data: {
    username: 'zhangsan',
    password: 'password123'
  },
  success: function(res) {
    // 保存token到本地存储
    wx.setStorageSync('token', res.data.token);
    console.log('登录成功:', res.data);
  },
  fail: function(err) {
    console.error('登录失败:', err);
  }
});
```

#### 获取患者信息
```javascript
const token = wx.getStorageSync('token');
wx.request({
  url: 'http://127.0.0.1:8000/api/patient/info/',
  method: 'GET',
  header: {
    'Authorization': 'Token ' + token
  },
  success: function(res) {
    console.log('患者信息:', res.data);
  },
  fail: function(err) {
    console.error('获取信息失败:', err);
  }
});
```

## 错误码说明

- `400`: 请求参数错误
- `401`: 未授权（Token无效或过期）
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误

## 注意事项

1. 所有需要认证的接口都需要在请求头中携带Token
2. Token格式: `Authorization: Token <token_value>`
3. 患者注册时需要指定分配的医生ID
4. 密码长度至少8位
5. 手机号格式需要正确
6. 用户名必须唯一

## 部署说明

在生产环境中，需要将 `http://127.0.0.1:8000` 替换为实际的服务器地址。