# 大黄鸭AI角色扮演平台 - 文档索引

## 📚 文档分类

### 🚀 快速开始
- [快速开始指南](guides/quick_start.md) - 5分钟快速体验系统功能

### 📖 API文档
- [用户管理API](api/user.md) - 用户注册、登录、管理功能
- [角色管理API](api/characters.md) - 角色创建、搜索、管理
- [对话管理API](api/conversations.md) - 对话创建、消息发送
- [登录认证API](api/login.md) - 用户认证和授权

### 🎯 功能指南
- [角色管理](systematic_design/character/) - 角色创建、搜索、管理
  - [角色API文档](systematic_design/character/character_api.md) - 详细的API接口说明
  - [角色管理说明](systematic_design/character/README.md) - 功能状态和快速开始
- [对话服务](systematic_design/conversation/) - 对话编排和消息处理
  - [对话服务文档](systematic_design/conversation/conversation_service.md) - 服务架构和实现
  - [对话服务详细设计](systematic_design/conversation/conversation_service_detailed.md) - 详细技术实现

### 💾 存储服务
- [七牛云存储指南](storage/qiniu_storage_guide.md) - 完整的使用指南
- [七牛云配置说明](storage/qiniu_configuration.md) - 配置步骤和参数说明

### 🛠️ 开发文档
- [系统架构](development/framework.md) - 整体系统架构和设计理念
- [超级用户设置](superuser_setup.md) - 超级用户创建和管理指南

## 📋 文档状态

### ✅ 已完成
- [x] 角色管理功能文档
- [x] 对话服务文档
- [x] 七牛云存储文档
- [x] API接口文档
- [x] 快速开始指南
- [x] 系统架构文档
- [x] 超级用户设置文档

### 🚧 计划中
- [ ] 语音处理文档
- [ ] 部署指南
- [ ] 性能优化指南
- [ ] 故障排除指南
- [ ] 开发者贡献指南

## 🔍 按功能查找

### 角色管理
- 角色创建和编辑
- 角色搜索（文本、向量、混合）
- 标签管理
- 向量嵌入

### 对话服务
- 对话创建和管理
- 消息发送和接收
- 多LLM模型支持
- 上下文管理

### 文件存储
- 文件上传和下载
- 图片处理
- CDN加速
- 私有文件访问

### 开发相关
- 环境配置
- 数据库迁移
- API测试
- 部署指南

## 📖 阅读建议

### 新用户
1. 从[快速开始指南](guides/quick_start.md)开始
2. 查看[系统架构](development/framework.md)了解整体设计
3. 参考[API文档](api/)进行开发

### 开发者
1. 阅读[系统架构](development/framework.md)
2. 查看各模块的详细文档
3. 参考[API文档](api/)进行集成

### 运维人员
1. 查看[七牛云配置说明](storage/qiniu_configuration.md)
2. 参考[系统架构](development/framework.md)了解部署要求
3. 查看各服务的配置说明

## 🔄 文档更新

文档会随着功能开发持续更新，请关注：
- 新功能发布时的文档更新
- API变更时的接口文档更新
- 配置变更时的配置说明更新

## 📝 反馈建议

如果您发现文档中的问题或有改进建议，请：
1. 提交GitHub Issue
2. 发送邮件到 support@dahuangya.com
3. 直接提交Pull Request

---

**最后更新**: 2024-09-23  
**文档版本**: v2.0.0
