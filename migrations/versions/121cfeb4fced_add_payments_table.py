"""add payments table

Revision ID: 121cfeb4fced
Revises: 3c9e3cdfffaa
Create Date: 2026-07-09 07:16:27.045780

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '121cfeb4fced'
down_revision: Union[str, Sequence[str], None] = '3c9e3cdfffaa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.Integer(), nullable=False),
        sa.Column("method", sa.Enum("cash", "card", name="paymentmethod"), nullable=False),
        sa.Column("amount_tendered", sa.Numeric(10, 2), nullable=False),
        sa.Column("change_given", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transaction_id"),
    )


def downgrade() -> None:
    op.drop_table("payments")
    sa.Enum(name="paymentmethod").drop(op.get_bind())
