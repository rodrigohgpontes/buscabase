from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision = "0004_prose_search"
down_revision = "0003_prose_blocks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("prose_blocks", sa.Column("texto_hash", sa.Text(), nullable=True))
    op.add_column("prose_blocks", sa.Column("embedding_model", sa.Text(), nullable=True))
    op.add_column("prose_blocks", sa.Column("embedding", Vector(3072), nullable=True))
    op.execute(
        """
        CREATE INDEX ix_prose_blocks_tsv ON prose_blocks USING gin (
            to_tsvector('portuguese', coalesce(text, ''))
        )
        WHERE type NOT IN ('running_header', 'running_footer', 'page_number', 'figure')
          AND text <> ''
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_prose_blocks_embedding")
    op.execute("DROP INDEX IF EXISTS ix_prose_blocks_tsv")
    op.drop_column("prose_blocks", "embedding")
    op.drop_column("prose_blocks", "embedding_model")
    op.drop_column("prose_blocks", "texto_hash")
