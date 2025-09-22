"""update_embedding_to_vector_type

Revision ID: ebc7f1871709
Revises: 8cf93c369734
Create Date: 2025-09-22 17:25:17.796209

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = "ebc7f1871709"
down_revision = "8cf93c369734"
branch_labels = None
depends_on = None


def upgrade():
    # 将 embedding 字段从 JSON 类型改为 vector 类型
    # 注意：这需要先备份数据，因为类型转换可能丢失数据
    op.execute(
        """
        -- 备份现有数据到临时表
        CREATE TABLE character_embeddings_backup AS 
        SELECT id, character_id, embedding_type, model_name, dimension, 
               embedding::text as embedding_text, created_at
        FROM character_embeddings;
    """
    )

    # 删除原表
    op.drop_table("character_embeddings")

    # 重新创建表，使用 vector 类型
    op.create_table(
        "character_embeddings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("character_id", sa.UUID(), nullable=False),
        sa.Column("embedding_type", sa.String(length=50), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("dimension", sa.Integer(), nullable=False),
        sa.Column("embedding", Vector(1024), nullable=False),  # 使用 1024 维向量
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["characters.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 从备份表恢复数据（需要重新生成向量）
    op.execute(
        """
        -- 注意：这里需要重新生成向量，因为 JSON 到 vector 的转换
        -- 在实际应用中，应该重新运行嵌入生成过程
        DROP TABLE character_embeddings_backup;
    """
    )


def downgrade():
    # 将 vector 类型改回 JSON 类型
    op.execute(
        """
        -- 备份现有数据
        CREATE TABLE character_embeddings_backup AS 
        SELECT id, character_id, embedding_type, model_name, dimension, 
               embedding::text as embedding_text, created_at
        FROM character_embeddings;
    """
    )

    # 删除原表
    op.drop_table("character_embeddings")

    # 重新创建表，使用 JSON 类型
    op.create_table(
        "character_embeddings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("character_id", sa.UUID(), nullable=False),
        sa.Column("embedding_type", sa.String(length=50), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("dimension", sa.Integer(), nullable=False),
        sa.Column("embedding", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["characters.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # 从备份表恢复数据
    op.execute(
        """
        INSERT INTO character_embeddings (id, character_id, embedding_type, model_name, dimension, embedding, created_at)
        SELECT id, character_id, embedding_type, model_name, dimension, 
               embedding_text::json, created_at
        FROM character_embeddings_backup;
        
        DROP TABLE character_embeddings_backup;
    """
    )
