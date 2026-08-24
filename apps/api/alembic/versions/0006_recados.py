from alembic import op
import sqlalchemy as sa


revision = "0006_recados"
down_revision = "0005_usage_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recados",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("nome", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("mensagem", sa.Text(), nullable=False),
        sa.Column("pagina", sa.Text(), nullable=True),
    )
    op.execute("CREATE INDEX ix_recados_created ON recados (created_at DESC)")


def downgrade() -> None:
    op.drop_table("recados")
