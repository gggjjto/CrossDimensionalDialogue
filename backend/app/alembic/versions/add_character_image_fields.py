"""Add character image generation fields

Revision ID: add_character_image_fields
Revises:
Create Date: 2024-01-22 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_character_image_fields"
down_revision = "e2b5fa48b264"
branch_labels = None
depends_on = None


def upgrade():
    """添加角色AI图片生成相关字段"""
    # 添加自动生成图片字段
    op.add_column(
        "characters",
        sa.Column(
            "auto_generate_image", sa.Boolean(), nullable=False, server_default="false"
        ),
    )

    # 添加图片风格字段
    op.add_column(
        "characters",
        sa.Column(
            "image_style", sa.String(20), nullable=True, server_default="realistic"
        ),
    )

    # 添加图片尺寸字段
    op.add_column(
        "characters",
        sa.Column(
            "image_size", sa.String(20), nullable=True, server_default="1024x1024"
        ),
    )


def downgrade():
    """删除角色AI图片生成相关字段"""
    op.drop_column("characters", "image_size")
    op.drop_column("characters", "image_style")
    op.drop_column("characters", "auto_generate_image")
