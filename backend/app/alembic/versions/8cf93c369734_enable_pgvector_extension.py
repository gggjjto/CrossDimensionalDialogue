"""enable_pgvector_extension

Revision ID: 8cf93c369734
Revises: 42a230188bee
Create Date: 2025-09-22 14:54:08.801413

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '8cf93c369734'
down_revision = '42a230188bee'
branch_labels = None
depends_on = None


def upgrade():
    # 启用 pgvector 扩展
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')


def downgrade():
    # 禁用 pgvector 扩展（注意：这会删除所有向量数据）
    op.execute('DROP EXTENSION IF EXISTS vector')
