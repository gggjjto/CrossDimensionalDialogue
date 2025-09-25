"""merge heads for voice_catalog and images

Revision ID: bd5380ce070b
Revises: add_character_image_fields, add_image_file_message_tables, f1a2b3c4d5e6
Create Date: 2025-09-24 20:09:09.460532

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'bd5380ce070b'
down_revision = ('add_character_image_fields', 'add_image_file_message_tables', 'f1a2b3c4d5e6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
