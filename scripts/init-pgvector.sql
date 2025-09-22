-- 初始化 pgvector 扩展
-- 这个脚本会在 PostgreSQL 容器启动时自动执行

-- 启用 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 验证扩展是否安装成功
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- 显示 pgvector 版本信息
SELECT vector_version();
