from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Area, Componente, Documento, Item, ProseBlock, Recorte, Snapshot


def public_item(db: Session, item: Item) -> dict:
    componente = db.get(Componente, item.componente_id) if item.componente_id else None
    area = db.get(Area, item.area_id) if item.area_id else None
    recorte = db.get(Recorte, item.recorte_id) if item.recorte_id else None
    documento = db.get(Documento, item.documento_id) if item.documento_id else None
    snapshot = db.execute(select(Snapshot).where(Snapshot.active.is_(True))).scalar_one_or_none()
    recorte_tag = snapshot.tag if snapshot else item.data_version
    tipo_label = {
        "habilidade": "Habilidade",
        "objetivo": "Objetivo de aprendizagem e desenvolvimento",
        "competencia_geral": "Competência geral",
        "competencia_especifica": "Competência específica",
    }.get(item.tipo, "Item da Base")
    anos_label = _anos_label(item, recorte)
    contexto_curto = " · ".join(
        part for part in [anos_label, componente.nome if componente else None] if part
    )
    metadados_linha = " · ".join(
        part
        for part in [
            anos_label,
            componente.nome if componente else None,
            item.unidade_ou_campo,
        ]
        if part
    )
    origin = settings.public_origin.rstrip("/")
    permalink = f"{origin}{item.url_path}"
    return {
        "codigo": item.codigo,
        "tipo": item.tipo,
        "tipo_label": tipo_label,
        "texto": item.texto,
        "etapa": item.etapa,
        "anos": item.anos,
        "anos_label": anos_label,
        "componente_id": item.componente_id,
        "componente": componente.nome if componente else None,
        "area_id": item.area_id,
        "area": area.nome if area else None,
        "unidade_ou_campo": item.unidade_ou_campo,
        "objetos": item.objetos or [],
        "documento_id": item.documento_id,
        "documento": documento.nome if documento else item.documento_id,
        "vigencia": {
            "status": item.vigencia_status,
            "desde": item.vigencia_desde,
            "ate": item.vigencia_ate,
        },
        "fonte": item.fonte,
        "pagina_pdf": item.pagina_pdf,
        "url_path": item.url_path,
        "permalink": permalink,
        "recorte": recorte_tag,
        "contexto_curto": contexto_curto,
        "metadados_linha": metadados_linha,
        "nome_acessivel": f"{tipo_label} {item.codigo}",
    }


def suggestion_card(db: Session, item: Item) -> dict:
    data = public_item(db, item)
    texto = item.texto
    if len(texto) > 270:
        texto = texto[:269].rstrip() + "…"
    return {
        "codigo": item.codigo,
        "texto": texto,
        "texto_completo": item.texto,
        "contexto": data["contexto_curto"] or data["tipo_label"],
        "url_path": item.url_path,
        "nome_acessivel": f"{data['tipo_label']} {item.codigo}. {item.texto}. {data['contexto_curto']}",
    }


def public_item_fonte(db: Session, item: Item) -> dict:
    return {"kind": "item", "item": public_item(db, item)}


def public_prose_block(block: ProseBlock) -> dict:
    return {
        "id": block.id,
        "type": block.type,
        "text": block.text,
        "page": block.page,
        "seq": block.seq,
        "item_codigo": block.item_codigo,
    }


def public_prose_fonte(db: Session, block: ProseBlock) -> dict:
    documento = db.get(Documento, block.documento_id)
    nome = documento.nome if documento else block.documento_id
    slug = documento.slug if documento else block.documento_id
    text = block.text or ""
    limit = settings.perguntar_source_text_chars
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return {
        "kind": "prose",
        "documento_id": block.documento_id,
        "documento": nome,
        "page": block.page,
        "block_id": block.id,
        "type": block.type,
        "texto": text,
        "item_codigo": block.item_codigo,
        "url_path": f"/documento/{slug}#{block.id}",
    }


def _anos_label(item: Item, recorte: Recorte | None) -> str | None:
    if recorte and recorte.tipo == "grupo_etario":
        faixa = recorte.faixa or recorte.nome
        return recorte.nome if not recorte.faixa else f"{recorte.nome} ({recorte.faixa})"
    if not item.anos:
        if item.etapa == "EM":
            return "Ensino Médio"
        return None
    if len(item.anos) == 1:
        return f"{item.anos[0]}º ano"
    joined = " e ".join(f"{ano}º" for ano in item.anos)
    return f"{joined} anos"
