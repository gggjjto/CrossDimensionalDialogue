# 七牛云存储配置说明

## 环境变量配置

在项目根目录的 `.env` 文件中添加以下七牛云相关配置：

```bash
# 七牛云存储配置
QINIU_ACCESS_KEY=your_qiniu_access_key
QINIU_SECRET_KEY=your_qiniu_secret_key
QINIU_BUCKET_NAME=your_bucket_name
QINIU_DOMAIN=your_domain.com
QINIU_USE_HTTPS=true
QINIU_CDN_DOMAIN=your_cdn_domain.com
```

## 配置获取步骤

### 1. 注册七牛云账号

访问 [七牛云官网](https://www.qiniu.com/) 注册账号并完成实名认证。

### 2. 创建存储空间

1. 登录七牛云控制台
2. 进入"对象存储" -> "空间管理"
3. 点击"新建空间"
4. 填写空间名称（如：dahuanya-storage）
5. 选择存储区域（建议选择离用户最近的区域）
6. 选择访问控制（公开或私有）

### 3. 绑定域名

1. 在存储空间设置中找到"域名管理"
2. 点击"绑定域名"
3. 输入你的域名（如：storage.yourdomain.com）
4. 配置CNAME记录指向七牛云提供的CNAME地址

### 4. 获取访问密钥

1. 进入"个人中心" -> "密钥管理"
2. 查看或创建AccessKey和SecretKey
3. 将密钥信息填入环境变量

## 配置参数说明

| 参数名 | 说明 | 示例值 | 必填 |
|--------|------|--------|------|
| `QINIU_ACCESS_KEY` | 七牛云访问密钥 | `abc123def456` | 是 |
| `QINIU_SECRET_KEY` | 七牛云秘密密钥 | `xyz789uvw012` | 是 |
| `QINIU_BUCKET_NAME` | 存储空间名称 | `dahuanya-storage` | 是 |
| `QINIU_DOMAIN` | 绑定的域名 | `storage.yourdomain.com` | 是 |
| `QINIU_USE_HTTPS` | 是否使用HTTPS | `true` | 否 |
| `QINIU_CDN_DOMAIN` | CDN加速域名 | `cdn.yourdomain.com` | 否 |

## 安全建议

1. **密钥安全**：不要将AccessKey和SecretKey提交到代码仓库
2. **域名配置**：建议使用HTTPS域名
3. **访问控制**：根据需求设置合适的访问权限
4. **定期轮换**：定期更换访问密钥

## 测试配置

配置完成后，可以运行测试脚本验证配置是否正确：

```bash
cd backend
uv run app/scripts/test_qiniu_storage.py
```

## 常见问题

### Q: 上传失败，提示"认证失败"

A: 检查AccessKey和SecretKey是否正确，确保没有多余的空格或字符。

### Q: 无法访问上传的文件

A: 检查域名配置是否正确，确保CNAME记录已生效。

### Q: 上传速度慢

A: 可以配置CDN加速域名，或选择离用户更近的存储区域。

### Q: 如何设置文件访问权限

A: 在存储空间设置中可以配置访问控制策略，支持公开访问、私有访问等模式。
