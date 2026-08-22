from alembic import op
import sqlalchemy as sa


revision = "0003_prose_blocks"
down_revision = "0002_gemini_embedding_dimension"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prose_documents",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("arquivo", sa.Text(), nullable=False),
        sa.Column("sha256", sa.Text(), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=False),
        sa.Column("data_version", sa.Text(), nullable=False),
        sa.Column("extracted_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_table(
        "prose_pages",
        sa.Column("documento_id", sa.Text(), sa.ForeignKey("prose_documents.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("page", sa.Integer(), primary_key=True),
        sa.Column("width", sa.Float(), nullable=False),
        sa.Column("height", sa.Float(), nullable=False),
    )
    op.create_table(
        "prose_blocks",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("documento_id", sa.Text(), sa.ForeignKey("prose_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("page", sa.Integer(), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("raw_lines", sa.JSON(), nullable=False),
        sa.Column("bbox", sa.JSON(), nullable=False),
        sa.Column("font_size", sa.Float(), nullable=True),
        sa.Column("font_name", sa.Text(), nullable=True),
        sa.Column("item_codigo", sa.Text(), nullable=True),
    )
    op.create_index("ix_prose_blocks_doc_page_seq", "prose_blocks", ["documento_id", "page", "seq"])
    op.create_index("ix_prose_blocks_item_codigo", "prose_blocks", ["item_codigo"])


def downgrade() -> None:
    op.drop_index("ix_prose_blocks_item_codigo", table_name="prose_blocks")
    op.drop_index("ix_prose_blocks_doc_page_seq", table_name="prose_blocks")
    op.drop_table("prose_blocks")
    op.drop_table("prose_pages")
    op.drop_table("prose_documents")
