# 用户管理 API 文档

## 概述

用户管理模块提供了完整的用户生命周期管理功能，包括用户注册、信息更新、密码管理、权限控制等功能。该模块与登录认证模块紧密配合，为整个大黄鸭系统提供完整的用户管理解决方案。

## 核心功能

### 👤 用户生命周期管理
- **用户注册**: 支持新用户注册和账户创建
- **信息管理**: 用户可以更新自己的基本信息
- **密码管理**: 安全的密码修改和重置功能
- **账户删除**: 用户可以选择删除自己的账户

### 🔐 权限控制系统
- **角色管理**: 支持普通用户和超级用户两种角色
- **权限验证**: 基于角色的访问控制
- **安全隔离**: 用户只能访问和修改自己的数据

### 🛠️ 管理员功能
- **用户列表**: 超级用户可以查看所有用户
- **用户管理**: 创建、更新、删除其他用户
- **权限分配**: 管理用户角色和权限
- **系统监控**: 查看用户统计和活动情况

### 📧 邮件通知系统
- **注册通知**: 新用户注册时发送欢迎邮件
- **密码重置**: 密码修改时的安全通知
- **账户变更**: 重要信息修改时的通知

## 认证方式

### JWT令牌认证
所有API请求都需要在请求头中包含有效的JWT令牌：

```http
Authorization: Bearer <your_jwt_token>
```

### 权限级别
- **普通用户**: 可以管理自己的信息
- **超级用户**: 可以管理所有用户信息

## 可以实现的功能

### 🎯 用户端功能

#### 1. 账户注册与登录
- **新用户注册**: 用户可以通过邮箱和密码创建新账户
- **账户激活**: 注册后自动激活账户，可立即使用
- **安全登录**: 使用邮箱和密码进行安全登录
- **令牌管理**: 登录后获得JWT令牌用于后续API调用

#### 2. 个人信息管理
- **查看个人信息**: 用户可以查看自己的完整信息
- **更新基本信息**: 修改姓名、邮箱等个人信息
- **密码修改**: 用户可以安全地修改自己的密码
- **账户删除**: 用户可以删除自己的账户（超级用户除外）

#### 3. 密码安全
- **密码修改**: 需要提供当前密码才能修改
- **密码重置**: 通过邮箱接收重置链接
- **安全验证**: 所有密码操作都有安全验证

### 🛠️ 管理员功能

#### 1. 用户管理
- **用户列表**: 查看系统中所有注册用户
- **用户详情**: 查看任意用户的详细信息
- **创建用户**: 管理员可以创建新用户账户
- **更新用户**: 修改其他用户的信息和权限
- **删除用户**: 删除不需要的用户账户

#### 2. 权限管理
- **角色分配**: 将用户设置为超级用户或普通用户
- **权限控制**: 基于角色的访问控制
- **安全隔离**: 确保用户只能访问授权的内容

#### 3. 系统监控
- **用户统计**: 查看注册用户总数和活跃情况
- **邮件管理**: 预览和管理系统邮件模板
- **安全审计**: 监控用户操作和系统安全

### 🔧 开发者功能

#### 1. API集成
- **RESTful API**: 标准的REST API接口
- **JWT认证**: 基于JWT的无状态认证
- **错误处理**: 完善的错误码和错误信息
- **数据验证**: 自动的数据格式验证

#### 2. 扩展性
- **模块化设计**: 易于扩展和定制
- **配置灵活**: 支持多种配置选项
- **邮件模板**: 可自定义的邮件模板系统

## API端点

### 1. 用户注册

#### 用户注册（无需登录）
```http
POST /users/signup
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password",
    "full_name": "张三"
}
```

**响应示例：**
```json
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "full_name": "张三",
    "is_active": true,
    "is_superuser": false,
    "is_verified": false
}
```

**功能说明：**
- 创建新用户账户
- 自动发送验证邮件（如果启用）
- 密码会自动加密存储
- 新用户默认为非超级用户

### 2. 用户认证

#### 登录获取令牌
```http
POST /api/v1/login/access-token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=secure_password
```

**响应示例：**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

**功能说明：**
- 使用邮箱和密码登录
- 返回JWT访问令牌
- 令牌有效期由配置决定（默认30分钟）

#### 测试令牌有效性
```http
GET /api/v1/login/test-token
Authorization: Bearer <your_jwt_token>
```

**响应示例：**
```json
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "full_name": "张三",
    "is_active": true,
    "is_superuser": false,
    "is_verified": true
}
```

### 3. 用户信息管理

#### 获取当前用户信息
```http
GET /api/v1/users/me
Authorization: Bearer <your_jwt_token>
```

**响应示例：**
```json
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "full_name": "张三",
    "is_active": true,
    "is_superuser": false,
    "is_verified": true
}
```

#### 更新当前用户信息
```http
PATCH /api/v1/users/me
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
    "full_name": "张三（更新）",
    "email": "newemail@example.com"
}
```

**功能说明：**
- 只能更新自己的信息
- 如果更新邮箱，系统会检查邮箱是否已被使用
- 返回更新后的用户信息

#### 更新当前用户密码
```http
PATCH /api/v1/users/me/password
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
    "current_password": "old_password",
    "new_password": "new_secure_password"
}
```

**响应示例：**
```json
{
    "message": "Password updated successfully"
}
```

#### 删除当前用户
```http
DELETE /api/v1/users/me
Authorization: Bearer <your_jwt_token>
```

**响应示例：**
```json
{
    "message": "User deleted successfully"
}
```

### 4. 密码管理

#### 密码恢复
```http
POST /api/v1/password-recovery/user@example.com
```

**响应示例：**
```json
{
    "message": "Password recovery email sent"
}
```

**功能说明：**
- 向指定邮箱发送密码重置邮件
- 如果邮箱不存在，返回404错误
- 邮件包含密码重置链接

#### 重置密码
```http
POST /api/v1/reset-password/
Content-Type: application/json

{
    "token": "reset_token_from_email",
    "new_password": "new_secure_password"
}
```

**响应示例：**
```json
{
    "message": "Password updated successfully"
}
```

### 5. 超级用户管理功能

#### 获取用户列表
```http
GET /api/v1/users/?skip=0&limit=100
Authorization: Bearer <superuser_jwt_token>
```

**响应示例：**
```json
{
    "data": [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user@example.com",
            "full_name": "张三",
            "is_active": true,
            "is_superuser": false,
            "is_verified": true
        }
    ],
    "count": 1
}
```

**查询参数：**
- `skip`: 跳过的记录数（默认0）
- `limit`: 返回的记录数（默认100，最大100）

#### 创建用户（超级用户）
```http
POST /api/v1/users/
Authorization: Bearer <superuser_jwt_token>
Content-Type: application/json

{
    "email": "admin@example.com",
    "password": "admin_password",
    "full_name": "管理员",
    "is_superuser": true,
    "is_verified": true
}
```

#### 根据ID获取用户信息
```http
GET /api/v1/users/{user_id}
Authorization: Bearer <jwt_token>
```

**功能说明：**
- 普通用户只能查看自己的信息
- 超级用户可以查看任何用户信息

#### 更新用户信息（超级用户）
```http
PATCH /api/v1/users/{user_id}
Authorization: Bearer <superuser_jwt_token>
Content-Type: application/json

{
    "full_name": "更新后的姓名",
    "is_active": true,
    "is_superuser": false
}
```

#### 删除用户（超级用户）
```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer <superuser_jwt_token>
```

**响应示例：**
```json
{
    "message": "User deleted successfully"
}
```

**功能说明：**
- 超级用户不能删除自己
- 删除操作不可逆

## 数据模型

### 用户创建模型 (UserCreate)
```json
{
    "email": "string",           // 必填，邮箱地址
    "password": "string",        // 必填，密码
    "full_name": "string",       // 必填，全名
    "is_superuser": false,       // 可选，是否超级用户
    "is_verified": false         // 可选，是否已验证
}
```

### 用户注册模型 (UserRegister)
```json
{
    "email": "string",           // 必填，邮箱地址
    "password": "string",        // 必填，密码
    "full_name": "string"        // 必填，全名
}
```

### 用户更新模型 (UserUpdate)
```json
{
    "email": "string",           // 可选，邮箱地址
    "full_name": "string",       // 可选，全名
    "is_active": true,           // 可选，是否激活
    "is_superuser": false,       // 可选，是否超级用户
    "is_verified": false         // 可选，是否已验证
}
```

### 用户更新自己模型 (UserUpdateMe)
```json
{
    "email": "string",           // 可选，邮箱地址
    "full_name": "string"        // 可选，全名
}
```

### 密码更新模型 (UpdatePassword)
```json
{
    "current_password": "string", // 必填，当前密码
    "new_password": "string"      // 必填，新密码
}
```

### 新密码模型 (NewPassword)
```json
{
    "token": "string",           // 必填，重置令牌
    "new_password": "string"     // 必填，新密码
}
```

## 错误处理

### 常见错误码

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 认证失败或令牌无效 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 用户不存在 |
| 409 | Conflict | 邮箱已存在 |
| 422 | Unprocessable Entity | 数据验证失败 |

### 错误响应格式
```json
{
    "detail": "错误描述信息"
}
```

### 常见错误示例

#### 认证失败
```json
{
    "detail": "Incorrect email or password"
}
```

#### 权限不足
```json
{
    "detail": "The user doesn't have enough privileges"
}
```

#### 邮箱已存在
```json
{
    "detail": "The user with this email already exists in the system."
}
```

#### 用户不存在
```json
{
    "detail": "User not found"
}
```

## 使用示例

### Python示例

#### 1. 用户注册和登录
```python
import httpx
import asyncio

async def register_and_login():
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # 1. 用户注册
        register_data = {
            "email": "test@example.com",
            "password": "secure_password",
            "full_name": "测试用户"
        }
        
        register_response = await client.post(
            f"{base_url}/api/v1/users/register",
            json=register_data
        )
        
        if register_response.status_code == 200:
            print("用户注册成功")
            user = register_response.json()
            print(f"用户ID: {user['id']}")
        
        # 2. 用户登录
        login_data = {
            "username": "test@example.com",
            "password": "secure_password"
        }
        
        login_response = await client.post(
            f"{base_url}/api/v1/login/access-token",
            data=login_data
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data["access_token"]
            print(f"登录成功，令牌: {access_token}")
            
            # 3. 使用令牌获取用户信息
            headers = {"Authorization": f"Bearer {access_token}"}
            user_response = await client.get(
                f"{base_url}/api/v1/users/me",
                headers=headers
            )
            
            if user_response.status_code == 200:
                user_info = user_response.json()
                print(f"当前用户: {user_info['full_name']}")

# 运行示例
asyncio.run(register_and_login())
```

#### 2. 更新用户信息
```python
async def update_user_info():
    base_url = "http://localhost:8000"
    access_token = "your_jwt_token_here"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        # 更新用户信息
        update_data = {
            "full_name": "更新后的姓名",
            "email": "newemail@example.com"
        }
        
        response = await client.patch(
            f"{base_url}/api/v1/users/me",
            json=update_data,
            headers=headers
        )
        
        if response.status_code == 200:
            updated_user = response.json()
            print(f"用户信息更新成功: {updated_user['full_name']}")
        else:
            print(f"更新失败: {response.text}")

asyncio.run(update_user_info())
```

#### 3. 密码管理
```python
async def change_password():
    base_url = "http://localhost:8000"
    access_token = "your_jwt_token_here"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        # 更新密码
        password_data = {
            "current_password": "old_password",
            "new_password": "new_secure_password"
        }
        
        response = await client.patch(
            f"{base_url}/api/v1/users/me/password",
            json=password_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print("密码更新成功")
        else:
            print(f"密码更新失败: {response.text}")

asyncio.run(change_password())
```

### JavaScript示例

#### 1. 用户注册
```javascript
async function registerUser() {
    const response = await fetch('http://localhost:8000/api/v1/users/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            email: 'user@example.com',
            password: 'secure_password',
            full_name: '张三'
        })
    });
    
    if (response.ok) {
        const user = await response.json();
        console.log('用户注册成功:', user);
    } else {
        const error = await response.json();
        console.error('注册失败:', error.detail);
    }
}
```

#### 2. 用户登录
```javascript
async function loginUser() {
    const formData = new FormData();
    formData.append('username', 'user@example.com');
    formData.append('password', 'secure_password');
    
    const response = await fetch('http://localhost:8000/api/v1/login/access-token', {
        method: 'POST',
        body: formData
    });
    
    if (response.ok) {
        const tokenData = await response.json();
        localStorage.setItem('access_token', tokenData.access_token);
        console.log('登录成功');
    } else {
        console.error('登录失败');
    }
}
```

#### 3. 获取用户信息
```javascript
async function getUserInfo() {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch('http://localhost:8000/api/v1/users/me', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    if (response.ok) {
        const user = await response.json();
        console.log('用户信息:', user);
    } else {
        console.error('获取用户信息失败');
    }
}
```

## 安全建议

### 1. 密码安全
- 使用强密码（至少8位，包含大小写字母、数字和特殊字符）
- 定期更换密码
- 不要在多个服务中使用相同密码

### 2. 令牌管理
- 安全存储JWT令牌
- 定期刷新令牌
- 在HTTPS环境下使用API

### 3. 权限控制
- 合理分配用户权限
- 定期审查超级用户权限
- 及时删除不需要的用户账户

## 配置说明

### 环境变量
```bash
# JWT配置
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 邮件配置
SMTP_HOST=smtp.example.com
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_email_password
SMTP_TLS=true
SMTP_SSL=false
SMTP_PORT=587

# 超级用户配置
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=admin_password
```

### 数据库配置
确保数据库已正确配置并运行迁移：
```bash
alembic upgrade head
```

## 故障排除

### 常见问题

1. **登录失败**
   - 检查邮箱和密码是否正确
   - 确认用户账户是否激活
   - 检查令牌是否过期

2. **权限不足**
   - 确认用户是否有相应权限
   - 检查令牌是否有效
   - 确认API端点是否需要超级用户权限

3. **邮箱验证问题**
   - 检查邮件服务器配置
   - 确认邮箱地址格式正确
   - 检查垃圾邮件文件夹

**大黄鸭团队** - 让用户管理更加简单和安全！ 🦆✨
