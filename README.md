# AI Health Manager - 后端 API 接口文档

> 版本: v1.0 | 状态: 草稿 | 最后更新: 2026-05-16

---

## 认证模块 `/api/v1/auth`

### 1.1 用户注册
```
POST /api/v1/auth/register
```

**Request Body:**
```json
{
  "username": "zhangsan",
  "password": "123456",
  "email": "zhangsan@example.com"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "created_at": "2026-05-16T10:00:00Z"
}
```

---

### 1.2 用户登录
```
POST /api/v1/auth/login
```

**Request (OAuth2 Form):**
```
username: zhangsan
password: 123456
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

### 1.3 刷新Token
```
POST /api/v1/auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):** 同登录

---

### 1.4 获取当前用户信息
```
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "created_at": "2026-05-16T10:00:00Z"
}
```

---

## 健康数据模块 `/api/v1/health`

### 2.1 创建/更新健康画像
```
POST /api/v1/health/profile
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "gender": "male",
  "birth_date": "1990-01-15",
  "height_cm": 175.5,
  "weight_kg": 70.0,
  "chronic_diseases": ["hypertension"],
  "family_history": ["father:heart_disease"],
  "allergies": ["penicillin"]
}
```

---

### 2.2 获取健康画像
```
GET /api/v1/health/profile
Authorization: Bearer <access_token>
```

---

### 2.3 手动录入健康数据
```
POST /api/v1/health/record/manual
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "blood_pressure_sys": 135,
  "blood_pressure_dia": 85,
  "fasting_glucose": 5.8,
  "uric_acid": 380,
  "cholesterol_total": 4.5,
  "heart_rate": 72
}
```

---

### 2.4 OCR识别体检报告
```
POST /api/v1/health/record/ocr
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Form Data:**
- file: (binary) 体检报告图片

---

### 2.5 同步可穿戴设备数据
```
POST /api/v1/health/record/wearable
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "device_type": "smartwatch",
  "metrics": {
    "heart_rate_bpm": 72,
    "step_count": 8432,
    "sleep_duration_min": 420,
    "sleep_deep_min": 120,
    "sleep_light_min": 260,
    "sleep_rem_min": 40,
    "spo2": 97,
    "calories_kcal": 2100
  },
  "recorded_at": "2026-05-16T08:00:00Z"
}
```

---

### 2.6 获取健康记录列表
```
GET /api/v1/health/records
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip`: int (default: 0)
- `limit`: int (default: 20)
- `source`: string (manual/ocr/wearable)

---

## 监测告警模块 `/api/v1/monitoring`

### 3.1 WebSocket实时告警
```
WS /api/v1/monitoring/ws/alerts/{user_id}?token=<access_token>
```

**推送消息格式:**
```json
{
  "type": "anomaly_alert",
  "data": {
    "id": "uuid",
    "alert_type": "blood_pressure",
    "severity": "warning",
    "title": "血压异常",
    "description": "您的收缩压为145mmHg，超过安全阈值140mmHg",
    "created_at": "2026-05-16T10:00:00Z"
  }
}
```

---

### 3.2 获取告警历史
```
GET /api/v1/monitoring/alerts/history
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip`: int
- `limit`: int
- `is_read`: boolean

---

### 3.3 标记告警为已读
```
POST /api/v1/monitoring/alerts/{alert_id}/read
Authorization: Bearer <access_token>
```

---

### 3.4 标记全部告警为已读
```
POST /api/v1/monitoring/alerts/read-all
Authorization: Bearer <access_token>
```

---

### 3.5 获取未读告警数量
```
GET /api/v1/monitoring/alerts/unread-count
Authorization: Bearer <access_token>
```

---

## Mock数据 (演示用)

当DeepSeek API未配置时，系统自动返回Mock数据：

### 风险评估Mock响应
```json
{
  "risk_level": "medium",
  "risk_score": 0.55,
  "summary": "当前健康状况处于中等风险水平，建议加强日常监测。"
}
```

---

## 错误码

| 状态码 | 说明 |
|-------|------|
| 400 | 请求参数错误 |
| 401 | 未授权/Token无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 快速开始

1. **安装依赖:**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量 (.env):**
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/health_db
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=your-secret-key
   DEEPSEEK_API_KEY=your-api-key
   ```

3. **初始化数据库:**
   ```bash
   # 创建数据库
   psql -U postgres -c "CREATE DATABASE health_db;"
   
   # 执行迁移
   alembic upgrade head
   ```

4. **启动服务:**
   ```bash
   python main.py
   # 或
   uvicorn main:app --reload --port 8000
   ```
