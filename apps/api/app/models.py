from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Float, ForeignKey, JSON, Boolean, DateTime, Integer, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.config import settings
from app.db import Base


class Snapshot(Base):
    __tablename__ = "snapshots"

    tag: Mapped[str] = mapped_column(Text, primary_key=True)
    schema_version: Mapped[str] = mapped_column(Text)
    etag: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding_model: Mapped[str] = mapped_column(Text)
    embedding_dimension: Mapped[int] = mapped_column(Integer)
    item_count: Mapped[int] = mapped_column(Integer, default=0)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    changelog_category: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Documento(Base):
    __tablename__ = "documentos"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    nome: Mapped[str] = mapped_column(Text)
    tipo: Mapped[str] = mapped_column(Text)
    esfera: Mapped[str | None] = mapped_column(Text, nullable=True)
    derivado_de: Mapped[str | None] = mapped_column(Text, nullable=True)
    slug: Mapped[str] = mapped_column(Text, unique=True)
    data_version: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSON)


class Etapa(Base):
    __tablename__ = "etapas"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    nome: Mapped[str] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(Text, unique=True)
    payload: Mapped[dict] = mapped_column(JSON)


class Area(Base):
    __tablename__ = "areas"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    etapa_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    nome: Mapped[str] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(Text, unique=True)
    documento_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSON)


class Componente(Base):
    __tablename__ = "componentes"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    etapa_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    area_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    nome: Mapped[str] = mapped_column(Text)
    sigla: Mapped[str | None] = mapped_column(Text, nullable=True)
    slug: Mapped[str] = mapped_column(Text, unique=True)
    documento_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSON)


class Recorte(Base):
    __tablename__ = "recortes"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    etapa_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo: Mapped[str] = mapped_column(Text)
    nome: Mapped[str] = mapped_column(Text)
    faixa: Mapped[str | None] = mapped_column(Text, nullable=True)
    slug: Mapped[str] = mapped_column(Text, unique=True)
    anos: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON)


class Contexto(Base):
    __tablename__ = "contextos"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    tipo: Mapped[str] = mapped_column(Text)
    nome: Mapped[str] = mapped_column(Text)
    componente_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSON)


class Item(Base):
    __tablename__ = "items"

    codigo: Mapped[str] = mapped_column(Text, primary_key=True)
    tipo: Mapped[str] = mapped_column(Text)
    documento_id: Mapped[str] = mapped_column(Text)
    etapa: Mapped[str | None] = mapped_column(Text, nullable=True)
    texto: Mapped[str] = mapped_column(Text)
    texto_hash: Mapped[str] = mapped_column(Text)
    anos: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), nullable=True)
    componente_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    area_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorte_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    unidade_ou_campo: Mapped[str | None] = mapped_column(Text, nullable=True)
    objetos: Mapped[list | None] = mapped_column(JSON, nullable=True)
    vigencia_status: Mapped[str] = mapped_column(Text, default="vigente")
    vigencia_desde: Mapped[str | None] = mapped_column(Text, nullable=True)
    vigencia_ate: Mapped[str | None] = mapped_column(Text, nullable=True)
    fonte: Mapped[dict] = mapped_column(JSON)
    pagina_pdf: Mapped[str | None] = mapped_column(Text, nullable=True)
    url_path: Mapped[str] = mapped_column(Text)
    data_version: Mapped[str] = mapped_column(Text)
    embedding_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict] = mapped_column(JSON)
    tsv: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding = mapped_column(Vector(settings.embedding_dimension), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AlinhamentoEI(Base):
    __tablename__ = "alinhamentos_ei"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON)
    codigos: Mapped[list[str]] = mapped_column(ARRAY(Text))


class OperationalEvent(Base):
    __tablename__ = "operational_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    kind: Mapped[str] = mapped_column(Text)
    mode: Mapped[str | None] = mapped_column(Text, nullable=True)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    query_len: Mapped[int | None] = mapped_column(Integer, nullable=True)
    query_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    filters_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_id: Mapped[str | None] = mapped_column(Text, nullable=True)


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    kind: Mapped[str] = mapped_column(Text)
    mode: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_class: Mapped[str | None] = mapped_column(Text, nullable=True)
    query: Mapped[str | None] = mapped_column(Text, nullable=True)
    filters: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    inferred: Mapped[list | None] = mapped_column(JSON, nullable=True)
    codigos: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    result_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    result_empty: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    cache_hit: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    atalho_codigo: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    turn: Mapped[int | None] = mapped_column(Integer, nullable=True)
    export_format: Mapped[str | None] = mapped_column(Text, nullable=True)
    copy_kind: Mapped[str | None] = mapped_column(Text, nullable=True)
    tokens_in: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_out: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    referrer_host: Mapped[str | None] = mapped_column(Text, nullable=True)
    device: Mapped[str | None] = mapped_column(Text, nullable=True)
    visitor_day: Mapped[str | None] = mapped_column(Text, nullable=True)


class ProseDocument(Base):
    __tablename__ = "prose_documents"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    arquivo: Mapped[str] = mapped_column(Text)
    sha256: Mapped[str] = mapped_column(Text)
    page_count: Mapped[int] = mapped_column(Integer)
    data_version: Mapped[str] = mapped_column(Text)
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProsePage(Base):
    __tablename__ = "prose_pages"

    documento_id: Mapped[str] = mapped_column(Text, ForeignKey("prose_documents.id", ondelete="CASCADE"), primary_key=True)
    page: Mapped[int] = mapped_column(Integer, primary_key=True)
    width: Mapped[float] = mapped_column(Float)
    height: Mapped[float] = mapped_column(Float)


class ProseBlock(Base):
    __tablename__ = "prose_blocks"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    documento_id: Mapped[str] = mapped_column(Text, ForeignKey("prose_documents.id", ondelete="CASCADE"))
    page: Mapped[int] = mapped_column(Integer)
    seq: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(Text)
    text: Mapped[str] = mapped_column(Text)
    raw_lines: Mapped[list] = mapped_column(JSON)
    bbox: Mapped[list] = mapped_column(JSON)
    font_size: Mapped[float | None] = mapped_column(Float, nullable=True)
    font_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    item_codigo: Mapped[str | None] = mapped_column(Text, nullable=True)
    texto_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding = mapped_column(Vector(settings.embedding_dimension), nullable=True)
