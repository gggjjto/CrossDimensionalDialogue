"""add voice_catalog table

Revision ID: f1a2b3c4d5e6
Revises: e2b5fa48b264
Create Date: 2025-09-24 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "f1a2b3c4d5e6"
down_revision = "e2b5fa48b264"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "voice_catalog",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "provider", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False
        ),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column(
            "voice", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False
        ),
        sa.Column(
            "preview_url", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True
        ),
        sa.Column(
            "description", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_voice_catalog_provider", "voice_catalog", ["provider"], unique=False
    )
    op.create_unique_constraint(
        "uq_voice_catalog_provider_voice", "voice_catalog", ["provider", "voice"]
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_voice_catalog_provider_voice", "voice_catalog", type_="unique"
    )
    op.drop_index("ix_voice_catalog_provider", table_name="voice_catalog")
    op.drop_table("voice_catalog")
