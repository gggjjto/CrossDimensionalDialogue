# 会话管理数据库迁移设计

## 概述

本文档详细描述了会话管理功能所需的数据库表结构、索引设计、约束关系和迁移脚本。所有表都使用PostgreSQL数据库，并遵循项目的命名规范和设计原则。

## 数据库表设计

### 1. 会话表 (conversations)

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'ended', 'archived')),
    settings JSONB,
    message_count INTEGER DEFAULT 0 CHECK (message_count >= 0),
    last_message_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 索引
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_character_id ON conversations(character_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_last_message_at ON conversations(last_message_at DESC);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX idx_conversations_user_status ON conversations(user_id, status);
CREATE INDEX idx_conversations_deleted_at ON conversations(deleted_at) WHERE deleted_at IS NULL;

-- 复合索引
CREATE INDEX idx_conversations_user_character ON conversations(user_id, character_id);
CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);
```

### 2. 消息表 (messages)

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('user', 'character', 'system')),
    sender_id UUID,
    content TEXT NOT NULL,
    content_type VARCHAR(20) NOT NULL DEFAULT 'text' CHECK (content_type IN ('text', 'audio', 'image', 'file')),
    audio_url VARCHAR(500),
    audio_duration INTEGER CHECK (audio_duration > 0),
    image_url VARCHAR(500),
    file_url VARCHAR(500),
    file_size INTEGER CHECK (file_size > 0),
    metadata JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'sending' CHECK (status IN ('sending', 'sent', 'failed', 'deleted')),
    parent_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 索引
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_sender_type ON messages(sender_type);
CREATE INDEX idx_messages_sender_id ON messages(sender_id);
CREATE INDEX idx_messages_content_type ON messages(content_type);
CREATE INDEX idx_messages_status ON messages(status);
CREATE INDEX idx_messages_parent_id ON messages(parent_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at DESC);

-- 复合索引
CREATE INDEX idx_messages_conversation_sender ON messages(conversation_id, sender_type);
CREATE INDEX idx_messages_conversation_type ON messages(conversation_id, content_type);
```

### 3. 会话上下文表 (conversation_contexts)

```sql
CREATE TABLE conversation_contexts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    context_type VARCHAR(20) NOT NULL CHECK (context_type IN ('summary', 'memory', 'key_points', 'emotion')),
    content TEXT NOT NULL,
    importance_score FLOAT CHECK (importance_score >= 0 AND importance_score <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 索引
CREATE INDEX idx_conversation_contexts_conversation_id ON conversation_contexts(conversation_id);
CREATE INDEX idx_conversation_contexts_type ON conversation_contexts(context_type);
CREATE INDEX idx_conversation_contexts_importance ON conversation_contexts(importance_score DESC);
CREATE INDEX idx_conversation_contexts_created_at ON conversation_contexts(created_at DESC);

-- 复合索引
CREATE INDEX idx_conversation_contexts_conv_type ON conversation_contexts(conversation_id, context_type);
```

### 4. 会话标签表 (conversation_tags)

```sql
CREATE TABLE conversation_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    tag_name VARCHAR(50) NOT NULL,
    tag_value VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 索引
CREATE INDEX idx_conversation_tags_conversation_id ON conversation_tags(conversation_id);
CREATE INDEX idx_conversation_tags_name ON conversation_tags(tag_name);
CREATE INDEX idx_conversation_tags_value ON conversation_tags(tag_value);

-- 复合索引
CREATE INDEX idx_conversation_tags_conv_name ON conversation_tags(conversation_id, tag_name);
CREATE UNIQUE INDEX idx_conversation_tags_unique ON conversation_tags(conversation_id, tag_name, tag_value);
```

### 5. 用户会话限制表 (user_conversation_limits)

```sql
CREATE TABLE user_conversation_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    limit_type VARCHAR(30) NOT NULL CHECK (limit_type IN ('daily_messages', 'hourly_messages', 'max_conversations', 'daily_audio_duration')),
    limit_value INTEGER NOT NULL CHECK (limit_value > 0),
    current_value INTEGER DEFAULT 0 CHECK (current_value >= 0),
    reset_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 索引
CREATE INDEX idx_user_limits_user_id ON user_conversation_limits(user_id);
CREATE INDEX idx_user_limits_type ON user_conversation_limits(limit_type);
CREATE INDEX idx_user_limits_reset_at ON user_conversation_limits(reset_at);

-- 复合索引
CREATE UNIQUE INDEX idx_user_limits_user_type ON user_conversation_limits(user_id, limit_type);
```

### 6. 消息向量表 (message_embeddings)

```sql
CREATE TABLE message_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    embedding_type VARCHAR(20) NOT NULL CHECK (embedding_type IN ('content', 'summary', 'emotion')),
    model_name VARCHAR(100) NOT NULL,
    dimension INTEGER NOT NULL CHECK (dimension > 0),
    embedding VECTOR(1536), -- 使用pgvector扩展
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 索引
CREATE INDEX idx_message_embeddings_message_id ON message_embeddings(message_id);
CREATE INDEX idx_message_embeddings_type ON message_embeddings(embedding_type);
CREATE INDEX idx_message_embeddings_model ON message_embeddings(model_name);

-- 向量索引（使用pgvector的HNSW索引）
CREATE INDEX idx_message_embeddings_vector ON message_embeddings USING hnsw (embedding vector_cosine_ops);
```

### 7. 会话统计表 (conversation_stats)

```sql
CREATE TABLE conversation_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    stat_date DATE NOT NULL,
    total_messages INTEGER DEFAULT 0,
    user_messages INTEGER DEFAULT 0,
    character_messages INTEGER DEFAULT 0,
    text_messages INTEGER DEFAULT 0,
    audio_messages INTEGER DEFAULT 0,
    image_messages INTEGER DEFAULT 0,
    total_duration INTEGER DEFAULT 0, -- 秒
    average_message_length FLOAT DEFAULT 0,
    positive_sentiment FLOAT DEFAULT 0,
    neutral_sentiment FLOAT DEFAULT 0,
    negative_sentiment FLOAT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 索引
CREATE INDEX idx_conversation_stats_conversation_id ON conversation_stats(conversation_id);
CREATE INDEX idx_conversation_stats_date ON conversation_stats(stat_date DESC);

-- 复合索引
CREATE UNIQUE INDEX idx_conversation_stats_unique ON conversation_stats(conversation_id, stat_date);
```

## 触发器设计

### 1. 更新会话消息计数触发器

```sql
-- 创建函数
CREATE OR REPLACE FUNCTION update_conversation_message_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE conversations 
        SET message_count = message_count + 1,
            last_message_at = NEW.created_at,
            updated_at = NOW()
        WHERE id = NEW.conversation_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE conversations 
        SET message_count = message_count - 1,
            updated_at = NOW()
        WHERE id = OLD.conversation_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trigger_update_conversation_message_count
    AFTER INSERT OR DELETE ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_message_count();
```

### 2. 更新会话时间戳触发器

```sql
-- 创建函数
CREATE OR REPLACE FUNCTION update_conversation_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations 
    SET updated_at = NOW()
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trigger_update_conversation_updated_at
    AFTER INSERT OR UPDATE ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_updated_at();
```

### 3. 更新消息时间戳触发器

```sql
-- 创建函数
CREATE OR REPLACE FUNCTION update_message_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trigger_update_message_updated_at
    BEFORE UPDATE ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_message_updated_at();
```

## 视图设计

### 1. 会话详情视图

```sql
CREATE VIEW conversation_details AS
SELECT 
    c.id,
    c.user_id,
    c.character_id,
    c.title,
    c.description,
    c.status,
    c.settings,
    c.message_count,
    c.last_message_at,
    c.created_at,
    c.updated_at,
    u.email as user_email,
    u.full_name as user_name,
    ch.name as character_name,
    ch.short_bio as character_bio,
    ch.avatar_url as character_avatar
FROM conversations c
JOIN users u ON c.user_id = u.id
JOIN characters ch ON c.character_id = ch.id
WHERE c.deleted_at IS NULL;
```

### 2. 消息详情视图

```sql
CREATE VIEW message_details AS
SELECT 
    m.id,
    m.conversation_id,
    m.sender_type,
    m.sender_id,
    m.content,
    m.content_type,
    m.audio_url,
    m.audio_duration,
    m.image_url,
    m.file_url,
    m.file_size,
    m.metadata,
    m.status,
    m.parent_id,
    m.created_at,
    m.updated_at,
    c.title as conversation_title,
    c.user_id as conversation_user_id
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
WHERE c.deleted_at IS NULL;
```

### 3. 用户会话统计视图

```sql
CREATE VIEW user_conversation_stats AS
SELECT 
    u.id as user_id,
    u.email,
    u.full_name,
    COUNT(c.id) as total_conversations,
    COUNT(CASE WHEN c.status = 'active' THEN 1 END) as active_conversations,
    COUNT(CASE WHEN c.status = 'paused' THEN 1 END) as paused_conversations,
    COUNT(CASE WHEN c.status = 'ended' THEN 1 END) as ended_conversations,
    COALESCE(SUM(c.message_count), 0) as total_messages,
    MAX(c.last_message_at) as last_activity_at
FROM users u
LEFT JOIN conversations c ON u.id = c.user_id AND c.deleted_at IS NULL
GROUP BY u.id, u.email, u.full_name;
```

## 存储过程设计

### 1. 清理过期会话

```sql
CREATE OR REPLACE FUNCTION cleanup_expired_conversations()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- 软删除超过30天未活动的会话
    UPDATE conversations 
    SET deleted_at = NOW()
    WHERE deleted_at IS NULL 
    AND last_message_at < NOW() - INTERVAL '30 days'
    AND status = 'ended';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- 硬删除超过90天的已删除会话
    DELETE FROM conversations 
    WHERE deleted_at IS NOT NULL 
    AND deleted_at < NOW() - INTERVAL '90 days';
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;
```

### 2. 重置用户限制

```sql
CREATE OR REPLACE FUNCTION reset_user_limits()
RETURNS INTEGER AS $$
DECLARE
    reset_count INTEGER;
BEGIN
    -- 重置每日限制
    UPDATE user_conversation_limits 
    SET current_value = 0,
        reset_at = NOW() + INTERVAL '1 day',
        updated_at = NOW()
    WHERE limit_type = 'daily_messages' 
    AND reset_at <= NOW();
    
    -- 重置每小时限制
    UPDATE user_conversation_limits 
    SET current_value = 0,
        reset_at = NOW() + INTERVAL '1 hour',
        updated_at = NOW()
    WHERE limit_type = 'hourly_messages' 
    AND reset_at <= NOW();
    
    GET DIAGNOSTICS reset_count = ROW_COUNT;
    
    RETURN reset_count;
END;
$$ LANGUAGE plpgsql;
```

### 3. 生成会话统计

```sql
CREATE OR REPLACE FUNCTION generate_conversation_stats(p_conversation_id UUID, p_date DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
DECLARE
    stat_record conversation_stats%ROWTYPE;
BEGIN
    -- 计算统计数据
    SELECT 
        p_conversation_id,
        p_date,
        COUNT(m.id) as total_messages,
        COUNT(CASE WHEN m.sender_type = 'user' THEN 1 END) as user_messages,
        COUNT(CASE WHEN m.sender_type = 'character' THEN 1 END) as character_messages,
        COUNT(CASE WHEN m.content_type = 'text' THEN 1 END) as text_messages,
        COUNT(CASE WHEN m.content_type = 'audio' THEN 1 END) as audio_messages,
        COUNT(CASE WHEN m.content_type = 'image' THEN 1 END) as image_messages,
        COALESCE(SUM(m.audio_duration), 0) as total_duration,
        COALESCE(AVG(LENGTH(m.content)), 0) as average_message_length
    INTO stat_record
    FROM messages m
    WHERE m.conversation_id = p_conversation_id
    AND DATE(m.created_at) = p_date;
    
    -- 插入或更新统计记录
    INSERT INTO conversation_stats (
        conversation_id, stat_date, total_messages, user_messages, 
        character_messages, text_messages, audio_messages, image_messages,
        total_duration, average_message_length
    ) VALUES (
        stat_record.conversation_id, stat_record.stat_date, stat_record.total_messages,
        stat_record.user_messages, stat_record.character_messages, stat_record.text_messages,
        stat_record.audio_messages, stat_record.image_messages, stat_record.total_duration,
        stat_record.average_message_length
    )
    ON CONFLICT (conversation_id, stat_date)
    DO UPDATE SET
        total_messages = EXCLUDED.total_messages,
        user_messages = EXCLUDED.user_messages,
        character_messages = EXCLUDED.character_messages,
        text_messages = EXCLUDED.text_messages,
        audio_messages = EXCLUDED.audio_messages,
        image_messages = EXCLUDED.image_messages,
        total_duration = EXCLUDED.total_duration,
        average_message_length = EXCLUDED.average_message_length,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;
```

## 数据迁移脚本

### 1. 创建扩展

```sql
-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 启用pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2. 创建表结构

```sql
-- 按顺序创建所有表
-- 1. conversations表
-- 2. messages表
-- 3. conversation_contexts表
-- 4. conversation_tags表
-- 5. user_conversation_limits表
-- 6. message_embeddings表
-- 7. conversation_stats表
```

### 3. 创建索引

```sql
-- 创建所有必要的索引
-- 包括单列索引、复合索引和向量索引
```

### 4. 创建触发器

```sql
-- 创建所有触发器函数和触发器
```

### 5. 创建视图

```sql
-- 创建所有视图
```

### 6. 创建存储过程

```sql
-- 创建所有存储过程
```

## 性能优化建议

### 1. 分区策略

```sql
-- 按时间分区messages表
CREATE TABLE messages_2024_01 PARTITION OF messages
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE messages_2024_02 PARTITION OF messages
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

### 2. 数据归档策略

```sql
-- 创建归档表
CREATE TABLE messages_archive (LIKE messages INCLUDING ALL);

-- 定期归档旧数据
INSERT INTO messages_archive 
SELECT * FROM messages 
WHERE created_at < NOW() - INTERVAL '1 year';

DELETE FROM messages 
WHERE created_at < NOW() - INTERVAL '1 year';
```

### 3. 缓存策略

```sql
-- 创建物化视图用于缓存
CREATE MATERIALIZED VIEW conversation_summary AS
SELECT 
    conversation_id,
    COUNT(*) as message_count,
    MAX(created_at) as last_message_at,
    COUNT(CASE WHEN sender_type = 'user' THEN 1 END) as user_message_count,
    COUNT(CASE WHEN sender_type = 'character' THEN 1 END) as character_message_count
FROM messages
GROUP BY conversation_id;

-- 创建索引
CREATE UNIQUE INDEX idx_conversation_summary_id ON conversation_summary(conversation_id);

-- 定期刷新物化视图
REFRESH MATERIALIZED VIEW conversation_summary;
```

## 监控和维护

### 1. 性能监控查询

```sql
-- 查看表大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 查看索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### 2. 维护任务

```sql
-- 定期清理过期数据
SELECT cleanup_expired_conversations();

-- 重置用户限制
SELECT reset_user_limits();

-- 更新表统计信息
ANALYZE conversations;
ANALYZE messages;
ANALYZE conversation_contexts;
```

## 安全考虑

### 1. 行级安全策略

```sql
-- 启用行级安全
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- 创建策略
CREATE POLICY conversation_user_policy ON conversations
    FOR ALL TO authenticated
    USING (user_id = current_user_id());

CREATE POLICY message_user_policy ON messages
    FOR ALL TO authenticated
    USING (conversation_id IN (
        SELECT id FROM conversations WHERE user_id = current_user_id()
    ));
```

### 2. 数据加密

```sql
-- 对敏感数据进行加密存储
-- 使用PostgreSQL的pgcrypto扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 加密函数示例
CREATE OR REPLACE FUNCTION encrypt_content(content TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN encode(encrypt(content::bytea, 'encryption_key', 'aes'), 'base64');
END;
$$ LANGUAGE plpgsql;
```

这个数据库迁移设计提供了完整的会话管理功能所需的数据库结构，包括表设计、索引优化、触发器、视图、存储过程等，确保系统的高性能、可扩展性和数据一致性。
