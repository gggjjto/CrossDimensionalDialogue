# 角色管理 API 接口文档

## 概述

角色管理模块提供了完整的角色和标签CRUD操作，支持角色创建、查询、更新、删除以及标签管理功能。

## 基础信息

- **基础URL**: `/api/v1/characters`
- **认证方式**: JWT Token (Bearer)
- **响应格式**: 统一JSON格式

## 角色管理接口

### 1. 创建角色

**接口**: `POST /api/v1/characters/`

**权限**: 需要超级用户权限

**请求参数**:

```json
{
  "name": "角色名称",
  "short_bio": "角色简介",
  "avatar_url": "头像URL（可选）",
  "persona_text": "角色人格定义（系统prompt）",
  "example_lines": ["示例台词1", "示例台词2"],
  "source": "来源/版权声明（可选）",
  "tag_ids": ["标签ID1", "标签ID2"]
}
```

**响应示例**:

```json
{
  "code": 0,
  "msg": "角色创建成功",
  "data": {
    "id": "uuid-string",
    "name": "苏格拉底",
    "short_bio": "古希腊哲学家，西方哲学的奠基者",
    "avatar_url": "https://example.com/socrates.jpg",
    "persona_text": "你是一位古希腊哲学家，以苏格拉底的方式思考问题...",
    "example_lines": ["我知道我什么都不知道", "未经审视的人生不值得过"],
    "source": "历史人物",
    "is_active": true,
    "created_at": "2025-01-22T10:00:00Z",
    "updated_at": "2025-01-22T10:00:00Z"
  }
}
```

**错误响应**:

```json
{
  "code": 400,
  "msg": "角色名称已存在",
  "data": null
}
```

### 2. 获取角色列表

**接口**: `GET /api/v1/characters/`

**权限**: 公开访问

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `skip` | integer | 否 | 跳过的记录数，默认0 |
| `limit` | integer | 否 | 返回的记录数，默认100，最大100 |
| `is_active` | boolean | 否 | 是否只返回可用角色 |
| `tag_ids` | array | 否 | 标签ID过滤，多个用逗号分隔 |

**响应示例**:

```json
{
  "code": 0,
  "msg": "获取角色列表成功",
  "data": {
    "characters": [
      {
        "id": "uuid-string",
        "name": "苏格拉底",
        "short_bio": "古希腊哲学家",
        "is_active": true,
        "created_at": "2025-01-22T10:00:00Z"
      }
    ],
    "total": 1,
    "skip": 0,
    "limit": 100
  }
}
```

### 3. 获取角色详情

**接口**: `GET /api/v1/characters/{character_id}`

**权限**: 公开访问

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `character_id` | string | 是 | 角色UUID |

**响应示例**:

```json
{
  "code": 0,
  "msg": "获取角色详情成功",
  "data": {
    "id": "uuid-string",
    "name": "苏格拉底",
    "short_bio": "古希腊哲学家，西方哲学的奠基者",
    "avatar_url": "https://example.com/socrates.jpg",
    "persona_text": "你是一位古希腊哲学家...",
    "example_lines": ["我知道我什么都不知道"],
    "source": "历史人物",
    "is_active": true,
    "created_at": "2025-01-22T10:00:00Z",
    "updated_at": "2025-01-22T10:00:00Z",
    "tags": [
      {
        "id": "tag-uuid",
        "name": "哲学",
        "description": "哲学相关角色"
      }
    ]
  }
}
```

**错误响应**:

```json
{
  "code": 404,
  "msg": "角色未找到",
  "data": null
}
```

### 4. 更新角色

**接口**: `PUT /api/v1/characters/{character_id}`

**权限**: 需要超级用户权限

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `character_id` | string | 是 | 角色UUID |

**请求参数**:

```json
{
  "name": "更新后的角色名称（可选）",
  "short_bio": "更新后的角色简介（可选）",
  "avatar_url": "更新后的头像URL（可选）",
  "persona_text": "更新后的角色人格定义（可选）",
  "example_lines": ["新的示例台词"],
  "source": "更新后的来源（可选）",
  "is_active": true,
  "tag_ids": ["新的标签ID列表"]
}
```

**响应示例**:

```json
{
  "code": 0,
  "msg": "角色更新成功",
  "data": {
    "id": "uuid-string",
    "name": "更新后的苏格拉底",
    "short_bio": "更新后的角色简介",
    "is_active": true,
    "updated_at": "2025-01-22T11:00:00Z"
  }
}
```

### 5. 删除角色

**接口**: `DELETE /api/v1/characters/{character_id}`

**权限**: 需要超级用户权限

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `character_id` | string | 是 | 角色UUID |

**响应示例**:

```json
{
  "code": 0,
  "msg": "角色删除成功",
  "data": {
    "id": "uuid-string",
    "name": "苏格拉底",
    "is_active": false,
    "updated_at": "2025-01-22T12:00:00Z"
  }
}
```

### 6. 搜索角色

**接口**: `GET /api/v1/characters/search`

**权限**: 公开访问

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | 是 | 搜索查询 |
| `search_type` | string | 否 | 搜索类型：text/vector/hybrid，默认text |
| `limit` | integer | 否 | 返回数量限制，默认10，最大100 |
| `offset` | integer | 否 | 偏移量，默认0 |
| `tag_ids` | array | 否 | 标签过滤 |
| `is_active` | boolean | 否 | 是否只搜索可用角色，默认true |

**响应示例**:

```json
{
  "code": 0,
  "msg": "搜索完成",
  "data": {
    "results": [
      {
        "character": {
          "id": "uuid-string",
          "name": "苏格拉底",
          "short_bio": "古希腊哲学家"
        },
        "score": 0.95,
        "match_type": "text"
      }
    ],
    "total": 1,
    "query": "苏格拉底",
    "search_type": "text"
  }
}
```

## 标签管理接口

### 1. 创建标签

**接口**: `POST /api/v1/characters/tags/`

**权限**: 需要超级用户权限

**请求参数**:

```json
{
  "name": "标签名称",
  "description": "标签描述（可选）",
  "color": "#FF0000"
}
```

**响应示例**:

```json
{
  "code": 0,
  "msg": "标签创建成功",
  "data": {
    "id": "tag-uuid",
    "name": "哲学",
    "description": "哲学相关角色",
    "color": "#FF0000",
    "created_at": "2025-01-22T10:00:00Z",
    "updated_at": "2025-01-22T10:00:00Z"
  }
}
```

### 2. 获取标签列表

**接口**: `GET /api/v1/characters/tags/`

**权限**: 公开访问

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `skip` | integer | 否 | 跳过的记录数，默认0 |
| `limit` | integer | 否 | 返回的记录数，默认100，最大100 |

**响应示例**:

```json
{
  "code": 0,
  "msg": "获取标签列表成功",
  "data": {
    "tags": [
      {
        "id": "tag-uuid",
        "name": "哲学",
        "description": "哲学相关角色",
        "color": "#FF0000",
        "created_at": "2025-01-22T10:00:00Z"
      }
    ],
    "total": 1,
    "skip": 0,
    "limit": 100
  }
}
```

### 3. 获取标签详情

**接口**: `GET /api/v1/characters/tags/{tag_id}`

**权限**: 公开访问

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tag_id` | string | 是 | 标签UUID |

**响应示例**:

```json
{
  "code": 0,
  "msg": "获取标签详情成功",
  "data": {
    "id": "tag-uuid",
    "name": "哲学",
    "description": "哲学相关角色",
    "color": "#FF0000",
    "created_at": "2025-01-22T10:00:00Z",
    "updated_at": "2025-01-22T10:00:00Z"
  }
}
```

### 4. 更新标签

**接口**: `PUT /api/v1/characters/tags/{tag_id}`

**权限**: 需要超级用户权限

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tag_id` | string | 是 | 标签UUID |

**请求参数**:

```json
{
  "name": "更新后的标签名称（可选）",
  "description": "更新后的标签描述（可选）",
  "color": "#00FF00"
}
```

**响应示例**:

```json
{
  "code": 0,
  "msg": "标签更新成功",
  "data": {
    "id": "tag-uuid",
    "name": "更新后的哲学",
    "description": "更新后的描述",
    "color": "#00FF00",
    "updated_at": "2025-01-22T11:00:00Z"
  }
}
```

### 5. 删除标签

**接口**: `DELETE /api/v1/characters/tags/{tag_id}`

**权限**: 需要超级用户权限

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tag_id` | string | 是 | 标签UUID |

**响应示例**:

```json
{
  "code": 0,
  "msg": "标签删除成功",
  "data": {
    "id": "tag-uuid",
    "name": "哲学",
    "description": "哲学相关角色"
  }
}
```

## 错误码说明

| 错误码 | HTTP状态码 | 说明 | 解决方案 |
|--------|------------|------|----------|
| 400 | 400 | 请求参数错误 | 检查请求参数格式和内容 |
| 401 | 401 | 未授权 | 检查JWT token是否有效 |
| 403 | 403 | 权限不足 | 确认用户是否有相应权限 |
| 404 | 404 | 资源未找到 | 检查资源ID是否正确 |
| 422 | 422 | 数据验证失败 | 检查请求数据是否符合验证规则 |
| 500 | 500 | 服务器内部错误 | 联系技术支持 |

## 使用示例

### JavaScript/TypeScript

```typescript
// 获取角色列表
async function getCharacters() {
  const response = await fetch('/api/v1/characters/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  const data = await response.json();
  
  if (data.code === 0) {
    console.log('角色列表:', data.data.characters);
  } else {
    console.error('获取失败:', data.msg);
  }
}

// 创建角色
async function createCharacter(characterData: any) {
  const response = await fetch('/api/v1/characters/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(characterData)
  });
  const data = await response.json();
  
  if (data.code === 0) {
    console.log('创建成功:', data.data);
  } else {
    console.error('创建失败:', data.msg);
  }
}
```

### Python

```python
import requests

# 获取角色列表
def get_characters():
    response = requests.get(
        'http://localhost:8000/api/v1/characters/',
        headers={'Authorization': f'Bearer {token}'}
    )
    data = response.json()
    
    if data['code'] == 0:
        print('角色列表:', data['data']['characters'])
    else:
        print('获取失败:', data['msg'])

# 创建角色
def create_character(character_data):
    response = requests.post(
        'http://localhost:8000/api/v1/characters/',
        json=character_data,
        headers={'Authorization': f'Bearer {token}'}
    )
    data = response.json()
    
    if data['code'] == 0:
        print('创建成功:', data['data'])
    else:
        print('创建失败:', data['msg'])
```

## 注意事项

1. **认证**: 创建、更新、删除操作需要超级用户权限
2. **分页**: 列表接口支持分页，建议合理设置limit参数
3. **搜索**: 搜索接口支持文本搜索，后续将支持向量搜索
4. **软删除**: 删除角色是软删除，只是将is_active设为false
5. **标签关联**: 角色和标签是多对多关系，可以动态关联
6. **数据验证**: 所有输入数据都会进行严格验证

---

如有问题或建议，请联系开发团队。
