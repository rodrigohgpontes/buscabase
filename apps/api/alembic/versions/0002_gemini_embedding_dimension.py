from alembic import op


revision = "0002_gemini_embedding_dimension"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_items_embedding")
    op.execute(
        "ALTER TABLE items ALTER COLUMN embedding TYPE vector(3072) "
        "USING NULL::vector(3072)"
    )
    op.execute("UPDATE items SET embedding_model = NULL")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_items_embedding")
    op.execute(
        "ALTER TABLE items ALTER COLUMN embedding TYPE vector(1536) "
        "USING NULL::vector(1536)"
    )
    op.execute("UPDATE items SET embedding_model = NULL")
