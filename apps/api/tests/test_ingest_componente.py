from app.ingest import resolve_componente_id


def test_resolve_computacao_from_sigla_dict_and_code():
    assert resolve_componente_id({"componente": "CO"}) == "co-comp"
    assert resolve_componente_id({"componente": {"id": "CO", "nome": "Computação"}}) == "co-comp"
    assert resolve_componente_id({"codigo": "EF05CO01"}) == "co-comp"
    assert resolve_componente_id({"componente": "ef-comp-ge"}) == "ef-comp-ge"
    assert resolve_componente_id({"codigo": "EF05GE01"}) is None
