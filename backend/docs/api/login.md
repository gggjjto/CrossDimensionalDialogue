# 登录认证 API 文档

## 概述

登录认证模块提供了完整的用户认证和密码管理功能，包括用户登录、令牌验证、密码恢复和重置等功能。该模块基于 OAuth2 标准实现，支持 JWT 令牌认证，为整个大黄鸭系统提供安全可靠的用户认证服务。

## 核心功能

### 🔐 用户认证系统
- **OAuth2 兼容登录**: 支持标准的 OAuth2 密码流认证
- **JWT 令牌管理**: 基于 JWT 的无状态认证机制
- **令牌验证**: 实时验证访问令牌的有效性
- **安全会话管理**: 支持令牌过期和自动刷新

### 🔑 密码管理系统
- **密码恢复**: 通过邮箱发送密码重置链接
- **安全重置**: 基于令牌的安全密码重置机制
- **密码验证**: 登录时验证用户密码和账户状态
- **邮件模板**: 支持自定义密码重置邮件模板

### 🛡️ 安全特性
- **bcrypt 加密**: 使用 bcrypt 算法安全存储密码
- **令牌过期**: 可配置的访问令牌过期时间
- **账户状态检查**: 登录时验证用户账户激活状态
- **错误处理**: 完善的错误处理和用户反馈机制

## API 接口列表

### 1. 用户登录认证
- **端点**: `POST /login/access-token`
- **功能**: 用户通过邮箱和密码登录，获取访问令牌
- **认证方式**: OAuth2 兼容的密码流

### 2. 令牌验证
- **端点**: `POST /login/test-token`
- **功能**: 验证当前访问令牌的有效性
- **权限要求**: 需要有效的访问令牌

### 3. 密码恢复
- **端点**: `POST /password-recovery/{email}`
- **功能**: 向指定邮箱发送密码重置邮件
- **权限要求**: 无需认证

### 4. 密码重置
- **端点**: `POST /reset-password/`
- **功能**: 使用重置令牌更新用户密码
- **权限要求**: 需要有效的重置令牌

### 5. 密码恢复邮件预览
- **端点**: `POST /password-recovery-html-content/{email}`
- **功能**: 管理员预览密码重置邮件的 HTML 内容
- **权限要求**: 需要超级用户权限

## API 详细说明

### 1. 用户登录

#### 请求
```http
POST /login/access-token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=your_password
```

#### 请求参数
- `username` (string, required): 用户邮箱地址
- `password` (string, required): 用户密码

#### 响应
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 错误响应
- `400 Bad Request`: 邮箱或密码错误，或用户账户未激活

#### 使用示例
```bash
curl -X POST "http://localhost:8000/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=your_password"
```

### 2. 令牌验证

#### 请求
```http
POST /login/test-token
Authorization: Bearer <access_token>
```

#### 响应
```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "John Doe"
}
```

#### 使用示例
```bash
curl -X POST "http://localhost:8000/login/test-token" \
  -H "Authorization: Bearer your_access_token"
```

### 3. 密码恢复

#### 请求
```http
POST /password-recovery/user@example.com
```

#### 响应
```json
{
  "message": "密码恢复邮件已发送"
}
```

#### 错误响应
- `404 Not Found`: 该邮箱不存在于系统中

#### 使用示例
```bash
curl -X POST "http://localhost:8000/password-recovery/user@example.com"
```

### 4. 密码重置

#### 请求
```http
POST /reset-password/
Content-Type: application/json

{
  "token": "reset_token_from_email",
  "new_password": "new_secure_password"
}
```

#### 请求参数
- `token` (string, required): 从密码恢复邮件中获取的重置令牌
- `new_password` (string, required): 新密码，长度 8-40 字符

#### 响应
```json
{
  "message": "密码更新成功"
}
```

#### 错误响应
- `400 Bad Request`: 无效的令牌或用户账户未激活
- `404 Not Found`: 该邮箱不存在于系统中

#### 使用示例
```bash
curl -X POST "http://localhost:8000/reset-password/" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "new_password": "new_secure_password"
  }'
```

### 5. 密码恢复邮件预览

#### 请求
```http
POST /password-recovery-html-content/user@example.com
Authorization: Bearer <superuser_access_token>
```

#### 响应
```html
<!DOCTYPE html>
<html>
<head>
    <title>Password Recovery</title>
</head>
<body>
    <!-- 密码重置邮件 HTML 内容 -->
</body>
</html>
```

#### 使用示例
```bash
curl -X POST "http://localhost:8000/password-recovery-html-content/user@example.com" \
  -H "Authorization: Bearer superuser_access_token"
```

## 可以实现的功能

### 🔐 用户认证功能

#### 1. 安全登录系统
- **OAuth2 兼容**: 支持标准的 OAuth2 密码流认证
- **JWT 令牌**: 基于 JWT 的无状态认证机制
- **令牌验证**: 实时验证访问令牌的有效性
- **会话管理**: 支持令牌过期和自动刷新

#### 2. 密码管理功能
- **密码恢复**: 用户忘记密码时通过邮箱重置
- **安全重置**: 基于令牌的安全密码重置机制
- **密码验证**: 登录时验证用户密码和账户状态
- **邮件通知**: 密码重置时发送安全通知邮件

#### 3. 安全防护功能
- **bcrypt 加密**: 使用 bcrypt 算法安全存储密码
- **令牌过期**: 可配置的访问令牌过期时间
- **账户状态检查**: 登录时验证用户账户激活状态
- **错误处理**: 完善的错误处理和用户反馈机制

### 🛠️ 管理员功能

#### 1. 邮件管理
- **邮件预览**: 管理员可以预览密码重置邮件内容
- **模板管理**: 支持自定义邮件模板
- **发送监控**: 监控邮件发送状态和结果

#### 2. 系统监控
- **登录统计**: 查看用户登录情况和频率
- **安全审计**: 监控异常登录和密码重置活动
- **令牌管理**: 管理系统中活跃的访问令牌

### 🔧 开发者功能

#### 1. API 集成
- **RESTful 接口**: 标准的 REST API 接口
- **OAuth2 兼容**: 支持 OAuth2 客户端集成
- **错误处理**: 完善的错误码和错误信息
- **文档支持**: 自动生成的 API 文档

#### 2. 安全配置
- **环境变量**: 灵活的安全配置选项
- **令牌配置**: 可配置的令牌过期时间
- **邮件配置**: 支持多种邮件服务提供商

## 安全特性

### 1. 令牌安全
- 使用 JWT 标准进行令牌生成和验证
- 访问令牌具有可配置的过期时间
- 密码重置令牌具有独立的过期时间（默认 24 小时）

### 2. 密码安全
- 密码使用 bcrypt 进行哈希存储
- 新密码长度限制为 8-40 字符
- 密码重置需要有效的令牌验证

### 3. 账户状态检查
- 登录时检查用户账户是否激活
- 密码重置时验证用户账户状态

## 配置要求

### 环境变量
确保以下环境变量已正确配置：

```env
# JWT 配置
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 邮件配置
EMAILS_ENABLED=true
EMAILS_FROM_NAME=Your App Name
EMAILS_FROM_EMAIL=noreply@yourapp.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# 前端配置
FRONTEND_HOST=http://localhost:3000

# 令牌过期时间
EMAIL_RESET_TOKEN_EXPIRE_HOURS=24
```

## 错误处理

### 常见错误码
- `400 Bad Request`: 请求参数错误或业务逻辑错误
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 请求数据验证失败

### 错误响应格式
```json
{
  "detail": "错误描述信息"
}
```

## 最佳实践

### 1. 令牌管理
- 客户端应安全存储访问令牌
- 在令牌过期前及时刷新
- 不要将令牌暴露在 URL 参数中

### 2. 密码安全
- 使用强密码策略
- 定期更新密码
- 不要在客户端存储明文密码

### 3. 错误处理
- 客户端应妥善处理各种错误情况
- 对于认证失败，应引导用户重新登录
- 对于令牌过期，应自动刷新或重新登录
