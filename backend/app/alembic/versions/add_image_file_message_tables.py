"""Add image and file message tables

Revision ID: add_image_file_message_tables
Revises: e2b5fa48b264_add_conversation_and_message_tables_v2
Create Date: 2024-01-15 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "add_image_file_message_tables"
down_revision = "e2b5fa48b264"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建图片消息表
    op.create_table(
        "image_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_url", sa.String(length=500), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column(
            "format",
            sa.Enum("jpeg", "png", "gif", "webp", "bmp", name="imageformat"),
            nullable=False,
        ),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("thumbnail_url", sa.String(length=500), nullable=True),
        sa.Column("compressed_url", sa.String(length=500), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "processing_status",
            sa.Enum(
                "pending", "processing", "completed", "failed", name="processingstatus"
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="CASCADE"),
        sa.CheckConstraint("file_size > 0", name="check_file_size_positive"),
        sa.CheckConstraint("width > 0", name="check_width_positive"),
        sa.CheckConstraint("height > 0", name="check_height_positive"),
        sa.CheckConstraint(
            "quality_score >= 0 AND quality_score <= 1",
            name="check_quality_score_range",
        ),
    )

    # 创建图片消息表索引
    op.create_index("idx_image_messages_message_id", "image_messages", ["message_id"])
    op.create_index("idx_image_messages_format", "image_messages", ["format"])
    op.create_index(
        "idx_image_messages_status", "image_messages", ["processing_status"]
    )
    op.create_index(
        "idx_image_messages_created_at",
        "image_messages",
        ["created_at"],
        postgresql_using="btree",
    )

    # 创建文件消息表
    op.create_table(
        "file_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_url", sa.String(length=500), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_extension", sa.String(length=20), nullable=False),
        sa.Column(
            "file_type",
            sa.Enum(
                "document",
                "image",
                "video",
                "audio",
                "archive",
                "other",
                name="filetype",
            ),
            nullable=False,
        ),
        sa.Column("checksum", sa.String(length=64), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("preview_url", sa.String(length=500), nullable=True),
        sa.Column("download_count", sa.Integer(), nullable=False),
        sa.Column(
            "processing_status",
            sa.Enum(
                "pending", "processing", "completed", "failed", name="processingstatus"
            ),
            nullable=False,
        ),
        sa.Column(
            "security_scan_status",
            sa.Enum(
                "pending",
                "scanning",
                "safe",
                "unsafe",
                "failed",
                name="securityscanstatus",
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"], ondelete="CASCADE"),
        sa.CheckConstraint("file_size > 0", name="check_file_size_positive"),
        sa.CheckConstraint(
            "download_count >= 0", name="check_download_count_non_negative"
        ),
    )

    # 创建文件消息表索引
    op.create_index("idx_file_messages_message_id", "file_messages", ["message_id"])
    op.create_index("idx_file_messages_type", "file_messages", ["file_type"])
    op.create_index("idx_file_messages_status", "file_messages", ["processing_status"])
    op.create_index(
        "idx_file_messages_security", "file_messages", ["security_scan_status"]
    )
    op.create_index(
        "idx_file_messages_created_at",
        "file_messages",
        ["created_at"],
        postgresql_using="btree",
    )

    # 创建文件处理任务表
    op.create_table(
        "file_processing_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("image_message_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "task_type",
            sa.Enum(
                "image_compress",
                "image_resize",
                "image_format_convert",
                "file_scan",
                "thumbnail_generate",
                name="tasktype",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "processing", "completed", "failed", name="processingstatus"
            ),
            nullable=False,
        ),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "result_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["file_message_id"], ["file_messages.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["image_message_id"], ["image_messages.id"], ondelete="CASCADE"
        ),
        sa.CheckConstraint(
            "progress >= 0 AND progress <= 100", name="check_progress_range"
        ),
    )

    # 创建文件处理任务表索引
    op.create_index(
        "idx_file_tasks_file_message_id", "file_processing_tasks", ["file_message_id"]
    )
    op.create_index(
        "idx_file_tasks_image_message_id", "file_processing_tasks", ["image_message_id"]
    )
    op.create_index("idx_file_tasks_type", "file_processing_tasks", ["task_type"])
    op.create_index("idx_file_tasks_status", "file_processing_tasks", ["status"])


def downgrade() -> None:
    # 删除文件处理任务表
    op.drop_index("idx_file_tasks_status", table_name="file_processing_tasks")
    op.drop_index("idx_file_tasks_type", table_name="file_processing_tasks")
    op.drop_index("idx_file_tasks_image_message_id", table_name="file_processing_tasks")
    op.drop_index("idx_file_tasks_file_message_id", table_name="file_processing_tasks")
    op.drop_table("file_processing_tasks")

    # 删除文件消息表
    op.drop_index("idx_file_messages_created_at", table_name="file_messages")
    op.drop_index("idx_file_messages_security", table_name="file_messages")
    op.drop_index("idx_file_messages_status", table_name="file_messages")
    op.drop_index("idx_file_messages_type", table_name="file_messages")
    op.drop_index("idx_file_messages_message_id", table_name="file_messages")
    op.drop_table("file_messages")

    # 删除图片消息表
    op.drop_index("idx_image_messages_created_at", table_name="image_messages")
    op.drop_index("idx_image_messages_status", table_name="image_messages")
    op.drop_index("idx_image_messages_format", table_name="image_messages")
    op.drop_index("idx_image_messages_message_id", table_name="image_messages")
    op.drop_table("image_messages")

    # 删除枚举类型
    op.execute("DROP TYPE IF EXISTS tasktype")
    op.execute("DROP TYPE IF EXISTS securityscanstatus")
    op.execute("DROP TYPE IF EXISTS filetype")
    op.execute("DROP TYPE IF EXISTS imageformat")
