from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0005_usage_events"
down_revision = "0004_prose_search"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usage_events",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("mode", sa.Text(), nullable=True),
        sa.Column("page_class", sa.Text(), nullable=True),
        sa.Column("query", sa.Text(), nullable=True),
        sa.Column("filters", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("inferred", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("codigos", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("result_count", sa.Integer(), nullable=True),
        sa.Column("result_empty", sa.Boolean(), nullable=True),
        sa.Column("cache_hit", sa.Boolean(), nullable=True),
        sa.Column("atalho_codigo", sa.Boolean(), nullable=True),
        sa.Column("turn", sa.Integer(), nullable=True),
        sa.Column("export_format", sa.Text(), nullable=True),
        sa.Column("copy_kind", sa.Text(), nullable=True),
        sa.Column("tokens_in", sa.Integer(), nullable=True),
        sa.Column("tokens_out", sa.Integer(), nullable=True),
        sa.Column("error_id", sa.Text(), nullable=True),
        sa.Column("referrer_host", sa.Text(), nullable=True),
        sa.Column("device", sa.Text(), nullable=True),
        sa.Column("visitor_day", sa.Text(), nullable=True),
    )
    op.execute("CREATE INDEX ix_usage_created ON usage_events (created_at)")
    op.execute("CREATE INDEX ix_usage_kind_created ON usage_events (kind, created_at)")
    op.execute("CREATE INDEX ix_usage_mode_created ON usage_events (mode, created_at)")


def downgrade() -> None:
    op.drop_table("usage_events")
