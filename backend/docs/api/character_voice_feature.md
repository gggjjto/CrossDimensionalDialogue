# 角色音色功能文档

## 概述

为角色添加了音色字段，让每个角色可以设置自己的默认音色，提供更个性化的语音体验。

## 功能特性

### 1. 角色默认音色

- 每个角色可以设置 `default_voice` 字段
- 默认值为 "Cherry"（芊悦音色）
- 支持17种预置音色选择

### 2. 音色选择优先级

系统按以下优先级选择音色：

1. **用户偏好音色** - 用户通过 `voice_preference` 参数指定
2. **角色默认音色** - 角色设置的 `default_voice` 字段  
3. **全局默认音色** - Cherry（芊悦）音色

### 3. 数据库字段

```sql
ALTER TABLE characters ADD COLUMN default_voice VARCHAR(50) DEFAULT 'Cherry';
```

## API 使用

### 创建角色时设置音色

```json
POST /api/v1/characters/
{
  "name": "小美",
  "short_bio": "温柔可爱的AI助手",
  "persona_text": "我是一个温柔可爱的AI助手...",
  "default_voice": "Cherry"  // 设置默认音色
}
```

### 更新角色音色

```json
PUT /api/v1/characters/{character_id}
{
  "default_voice": "Jennifer"  // 更新为詹妮弗音色
}
```

### 语音对话时使用角色音色

```json
POST /api/v1/voice/message
{
  "conversation_id": "uuid",
  "audio_file_url": "https://storage.example.com/audio.wav"
  // 不指定voice_preference，将使用角色的default_voice
}
```

## 可用音色列表

| 音色名称 | 中文名 | 特点 | 性别 |
|---------|--------|------|------|
| Cherry | 芊悦 | 阳光积极、亲切自然小姐姐（默认） | 女 |
| Jennifer | 詹妮弗 | 品牌级、电影质感般美语女声 | 女 |
| Katerina | 卡捷琳娜 | 御姐音色，韵律回味十足 | 女 |
| Jada | 上海-阿珍 | 沪上阿姐，风风火火 | 女 |
| Sunny | 四川-晴儿 | 甜到你心里的川妹子 | 女 |
| Kiki | 粤语-阿清 | 甜美港风闺蜜 | 女 |
| Ethan | 晨煦 | 标准普通话，带部分北方口音 | 男 |
| Ryan | 甜茶 | 节奏拉满，戏感炸裂 | 男 |
| Elias | 墨讲师 | 严谨叙事，适合知识讲解 | 男 |
| Dylan | 北京-晓东 | 北京胡同里长大的少年 | 男 |
| Marcus | 陕西-秦川 | 面宽话短，心实声沉 | 男 |
| Roy | 闽南-阿杰 | 诙谐直爽、市井活泼 | 男 |
| Peter | 天津-李彼得 | 相声捧哏风格 | 男 |
| Rocky | 粤语-阿强 | 幽默风趣，在线陪聊 | 男 |
| Eric | 四川-程川 | 一个跳脱市井的四川成都男子 | 男 |

## 技术实现

### 1. 数据模型更新

- `Character` 模型添加 `default_voice` 字段
- `CharacterCreate` 和 `CharacterUpdate` 支持音色设置
- `CharacterPublic` 返回音色信息

### 2. 服务层更新

- `DialogueOrchestrationService` 添加角色音色选择逻辑
- `_get_character_default_voice()` 方法实现角色音色选择
- 音色选择优先级：用户偏好 > 角色默认 > 全局默认

### 3. 数据库迁移

- 自动生成迁移文件：`54e9f8e460e3_add_default_voice_to_character.py`
- 添加 `default_voice` 字段到 `characters` 表
- 默认值为 "Cherry"

## 使用场景

### 1. 角色个性化

不同角色可以设置不同的音色，体现角色特点：

- **温柔角色** → Cherry（芊悦）
- **专业角色** → Elias（墨讲师）
- **活泼角色** → Sunny（四川-晴儿）
- **幽默角色** → Rocky（粤语-阿强）

### 2. 用户体验

- 用户可以为不同角色设置不同的音色偏好
- 系统自动选择最合适的音色
- 提供一致的语音体验

### 3. 内容创作

- 创作者可以为角色设置专属音色
- 增强角色的辨识度和个性化
- 提升用户沉浸感

## 注意事项

1. **音色可用性**：系统会检查音色是否可用，不可用时自动降级
2. **向后兼容**：现有角色会自动使用默认音色Cherry
3. **性能考虑**：音色选择逻辑轻量级，不影响响应速度
4. **扩展性**：未来可以支持更多音色或自定义音色

## 测试验证

```python
# 测试角色音色选择
test_character = Character(
    name='测试角色',
    default_voice='Jennifer'
)

# 验证音色选择逻辑
selected_voice = dialogue_orchestration_service._get_character_default_voice(
    test_character, available_voices
)
# 结果: Jennifer
```

## 总结

角色音色功能为系统增加了重要的个性化能力，让每个角色都有自己独特的"声音"，提升了用户体验和内容创作的灵活性。通过合理的优先级设计，既保证了用户的选择权，又提供了智能的默认行为。
