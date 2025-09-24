# 超级用户设置指南

## 概述

超级用户（Superuser）是系统中具有最高权限的用户，可以访问所有API端点和执行管理操作。

## 设置方法

### 方法1: 环境变量配置（推荐）

1. **创建环境变量文件**
   
   在项目根目录创建 `.env` 文件：
   ```bash
   # 超级用户配置
   FIRST_SUPERUSER=admin@example.com
   FIRST_SUPERUSER_PASSWORD=your_secure_password_here
   ```

2. **运行初始化脚本**
   ```bash
   cd backend
   uv run python app/initial_data.py
   ```

### 方法2: 直接修改配置文件

1. **修改配置文件**
   
   编辑 `backend/app/core/config.py`：
   ```python
   FIRST_SUPERUSER: EmailStr = "admin@example.com"
   FIRST_SUPERUSER_PASSWORD: str = "your_secure_password_here"
   ```

2. **运行初始化脚本**
   ```bash
   cd backend
   uv run python app/initial_data.py
   ```

### 方法3: 使用API创建（需要现有超级用户）

如果您已经有超级用户权限，可以通过API创建新的超级用户：

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "new_admin@example.com",
    "password": "secure_password",
    "full_name": "New Admin",
    "is_superuser": true
  }'
```

## 超级用户权限

超级用户可以：

- ✅ 访问所有API端点
- ✅ 创建、修改、删除任何用户
- ✅ 管理角色和对话
- ✅ 访问私有API端点
- ✅ 执行系统管理操作

## 安全建议

1. **强密码**: 使用包含大小写字母、数字和特殊字符的强密码
2. **定期更换**: 定期更换超级用户密码
3. **限制数量**: 只创建必要的超级用户账户
4. **监控访问**: 定期检查超级用户的活动日志

## 验证超级用户

### 登录测试
```bash
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=your_password"
```

### 权限测试
```bash
# 使用获取的token测试超级用户权限
curl -X GET "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 故障排除

### 问题1: 初始化失败
**症状**: 运行 `initial_data.py` 时出错
**解决方案**: 
1. 确保数据库连接正常
2. 检查环境变量是否正确设置
3. 确保数据库表已创建（运行迁移）

### 问题2: 无法登录
**症状**: 使用超级用户凭据无法登录
**解决方案**:
1. 检查邮箱和密码是否正确
2. 确认用户已成功创建
3. 检查用户状态是否为激活状态

### 问题3: 权限不足
**症状**: 登录成功但无法访问某些端点
**解决方案**:
1. 确认用户 `is_superuser` 字段为 `true`
2. 检查API端点是否需要超级用户权限
3. 验证JWT令牌是否有效

## 相关文件

- `app/core/config.py` - 配置文件
- `app/core/db.py` - 数据库初始化
- `app/initial_data.py` - 初始化脚本
- `app/models/user.py` - 用户模型
- `app/api/deps.py` - 权限依赖
