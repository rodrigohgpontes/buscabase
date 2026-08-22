from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")

    op.create_table(
        "snapshots",
        sa.Column("tag", sa.Text(), primary_key=True),
        sa.Column("schema_version", sa.Text(), nullable=False),
        sa.Column("etag", sa.Text(), nullable=True),
        sa.Column("embedding_model", sa.Text(), nullable=False),
        sa.Column("embedding_dimension", sa.Integer(), nullable=False),
        sa.Column("item_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("changelog_category", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )

    op.create_table(
        "documentos",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("nome", sa.Text(), nullable=False),
        sa.Column("tipo", sa.Text(), nullable=False),
        sa.Column("esfera", sa.Text(), nullable=True),
        sa.Column("derivado_de", sa.Text(), nullable=True),
        sa.Column("slug", sa.Text(), nullable=False, unique=True),
        sa.Column("data_version", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
    )

    op.create_table(
        "etapas",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("nome", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False, unique=True),
        sa.Column("payload", sa.JSON(), nullable=False),
    )

    op.create_table(
        "areas",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("etapa_id", sa.Text(), nullable=True),
        sa.Column("nome", sa.Text(), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("documento_id", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.UniqueConstraint("slug", name="uq_areas_slug"),
    )

    op.create_table(
        "componentes",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("etapa_id", sa.Text(), nullable=True),
        sa.Column("area_id", sa.Text(), nullable=True),
        sa.Column("nome", sa.Text(), nullable=False),
        sa.Column("sigla", sa.Text(), nullable=True),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("documento_id", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.UniqueConstraint("slug", name="uq_componentes_slug"),
    )

    op.create_table(
        "recortes",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("etapa_id", sa.Text(), nullable=True),
        sa.Column("tipo", sa.Text(), nullable=False),
        sa.Column("nome", sa.Text(), nullable=False),
        sa.Column("faixa", sa.Text(), nullable=True),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("anos", sa.ARRAY(sa.Integer()), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.UniqueConstraint("slug", name="uq_recortes_slug"),
    )

    op.create_table(
        "contextos",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("tipo", sa.Text(), nullable=False),
        sa.Column("nome", sa.Text(), nullable=False),
        sa.Column("componente_id", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
    )

    op.create_table(
        "items",
        sa.Column("codigo", sa.Text(), primary_key=True),
        sa.Column("tipo", sa.Text(), nullable=False),
        sa.Column("documento_id", sa.Text(), nullable=False),
        sa.Column("etapa", sa.Text(), nullable=True),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column("texto_hash", sa.Text(), nullable=False),
        sa.Column("anos", sa.ARRAY(sa.Integer()), nullable=True),
        sa.Column("componente_id", sa.Text(), nullable=True),
        sa.Column("area_id", sa.Text(), nullable=True),
        sa.Column("recorte_id", sa.Text(), nullable=True),
        sa.Column("unidade_ou_campo", sa.Text(), nullable=True),
        sa.Column("objetos", sa.JSON(), nullable=True),
        sa.Column("vigencia_status", sa.Text(), nullable=False, server_default="vigente"),
        sa.Column("vigencia_desde", sa.Text(), nullable=True),
        sa.Column("vigencia_ate", sa.Text(), nullable=True),
        sa.Column("fonte", sa.JSON(), nullable=False),
        sa.Column("pagina_pdf", sa.Text(), nullable=True),
        sa.Column("url_path", sa.Text(), nullable=False),
        sa.Column("data_version", sa.Text(), nullable=False),
        sa.Column("embedding_model", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("tsv", sa.TEXT(), nullable=True),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_index("ix_items_tipo", "items", ["tipo"])
    op.create_index("ix_items_etapa", "items", ["etapa"])
    op.create_index("ix_items_documento", "items", ["documento_id"])
    op.create_index("ix_items_componente", "items", ["componente_id"])
    op.create_index("ix_items_vigencia", "items", ["vigencia_status"])
    op.execute("CREATE INDEX ix_items_codigo_trgm ON items USING gin (codigo gin_trgm_ops)")
    op.execute(
        "CREATE INDEX ix_items_tsv ON items USING gin (to_tsvector('portuguese', coalesce(texto,'') || ' ' || coalesce(unidade_ou_campo,'') || ' ' || coalesce(codigo,'')))"
    )

    op.create_table(
        "alinhamentos_ei",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("codigos", sa.ARRAY(sa.Text()), nullable=False),
    )

    op.create_table(
        "operational_events",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("mode", sa.Text(), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("query_len", sa.Integer(), nullable=True),
        sa.Column("query_hash", sa.Text(), nullable=True),
        sa.Column("filters_hash", sa.Text(), nullable=True),
        sa.Column("result_count", sa.Integer(), nullable=True),
        sa.Column("error_id", sa.Text(), nullable=True),
    )
    op.execute(
        "CREATE INDEX ix_events_created ON operational_events (created_at)"
    )


def downgrade() -> None:
    op.drop_table("operational_events")
    op.drop_table("alinhamentos_ei")
    op.drop_table("items")
    op.drop_table("contextos")
    op.drop_table("recortes")
    op.drop_table("componentes")
    op.drop_table("areas")
    op.drop_table("etapas")
    op.drop_table("documentos")
    op.drop_table("snapshots")
