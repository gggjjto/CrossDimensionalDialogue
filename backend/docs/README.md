# 后端文档

欢迎来到 dahuanya 项目后端文档！这里包含了项目的技术文档、API接口说明和开发指南。

## 📚 文档目录

### 核心文档
- [项目架构设计](./framework.md) - 整体架构设计和技术选型
- [API统一返回格式](./api_response_format.md) - 统一响应规范和异常处理
- [角色管理API](./character_api.md) - 角色和标签管理接口文档

### 开发指南
- [开发规范](../.cursor/rules/dahuanya-backend.mdc) - 后端开发规范和最佳实践
- [Git提交规范](../.cursor/rules/dahuanya-git.mdc) - Git工作流和提交规范
- [包管理规范](../.cursor/rules/dahuanya-uv.mdc) - uv包管理工具使用指南

## 🚀 快速开始

### 环境要求
- Python 3.10+
- PostgreSQL 12+
- Redis 6+
- uv (包管理工具)

### 安装和运行

1. **克隆项目**
```bash
git clone <repository-url>
cd dahuanya/backend
```

2. **安装依赖**
```bash
uv sync
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和Redis连接信息
```

4. **运行数据库迁移**
```bash
alembic upgrade head
```

5. **启动服务**
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **访问API文档**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🏗️ 项目架构

### 技术栈
- **后端框架**: FastAPI + SQLModel + Pydantic
- **数据库**: PostgreSQL + pgvector (向量搜索)
- **缓存**: Redis
- **认证**: JWT + bcrypt
- **部署**: Docker + Docker Compose

### 目录结构
```
backend/
├── app/
│   ├── api/              # API路由
│   │   ├── routes/       # 具体路由实现
│   │   └── deps.py       # 依赖注入
│   ├── core/             # 核心配置
│   │   ├── config.py     # 配置管理
│   │   ├── db.py         # 数据库连接
│   │   └── security.py   # 安全相关
│   ├── crud/             # 数据库操作
│   ├── models/           # 数据模型
│   ├── middleware/       # 中间件
│   ├── utils/            # 工具函数
│   └── main.py           # 应用入口
├── docs/                 # 项目文档
├── tests/                # 测试文件
└── alembic/              # 数据库迁移
```

## 📖 API接口

### 统一响应格式
所有API接口都遵循统一的响应格式：

```json
{
  "code": 0,           // 状态码：0=成功，>0=错误
  "msg": "ok",         // 消息描述
  "data": {...}        // 响应数据
}
```

### 主要接口模块

#### 1. 角色管理 (`/api/v1/characters/`)
- `POST /` - 创建角色
- `GET /` - 获取角色列表
- `GET /{id}` - 获取角色详情
- `PUT /{id}` - 更新角色
- `DELETE /{id}` - 删除角色
- `GET /search` - 搜索角色

#### 2. 标签管理 (`/api/v1/characters/tags/`)
- `POST /` - 创建标签
- `GET /` - 获取标签列表
- `GET /{id}` - 获取标签详情
- `PUT /{id}` - 更新标签
- `DELETE /{id}` - 删除标签

#### 3. 用户管理 (`/api/v1/users/`)
- `GET /me` - 获取当前用户信息
- `PUT /me` - 更新用户信息
- `POST /me/password` - 修改密码

#### 4. 认证 (`/api/v1/login/`)
- `POST /access-token` - 用户登录
- `POST /test-token` - 验证token

## 🔧 开发指南

### 代码规范
- 使用类型提示 (Type Hints)
- 遵循PEP 8代码风格
- 使用Ruff进行代码检查
- 使用MyPy进行类型检查

### 数据库操作
- 使用SQLModel进行ORM操作
- 所有数据库操作都在`crud/`目录下
- 使用Alembic进行数据库迁移

### 测试
- 使用pytest进行单元测试
- 测试文件位于`tests/`目录
- 运行测试：`uv run pytest`

### 异常处理
- 使用全局异常处理器统一处理异常
- 所有异常都转换为统一的响应格式
- 详细的错误日志记录

## 🚀 部署

### Docker部署
```bash
# 构建镜像
docker build -t dahuanya-backend .

# 运行容器
docker run -p 8000:8000 dahuanya-backend
```

### Docker Compose部署
```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend
```

## 📊 监控和日志

### 日志配置
- 使用Python标准logging模块
- 支持不同级别的日志输出
- 集成Sentry进行错误监控

### 性能监控
- 集成Prometheus指标
- 支持健康检查端点
- 数据库连接池监控

## 🤝 贡献指南

### 开发流程
1. Fork项目
2. 创建功能分支 (`git checkout -b feat/feature-name`)
3. 提交更改 (`git commit -m 'feat: add new feature'`)
4. 推送分支 (`git push origin feat/feature-name`)
5. 创建Pull Request

### 提交规范
使用约定式提交规范：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

## 📞 支持

如果您在使用过程中遇到问题，可以通过以下方式获取帮助：

1. 查看本文档
2. 检查API文档 (http://localhost:8000/docs)
3. 查看项目Issues
4. 联系开发团队

## 📄 许可证

本项目采用 MIT 许可证。详情请查看 [LICENSE](../LICENSE) 文件。

---

**最后更新**: 2025-01-22  
**版本**: v1.0.0
