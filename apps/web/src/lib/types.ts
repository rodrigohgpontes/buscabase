export type Item = {
	codigo: string;
	tipo: string;
	tipo_label: string;
	texto: string;
	etapa: string | null;
	anos: number[] | null;
	anos_label: string | null;
	componente: string | null;
	area: string | null;
	unidade_ou_campo: string | null;
	objetos: { id?: string; nome?: string }[];
	documento: string | null;
	documento_id: string | null;
	vigencia: { status: string; desde?: string | null; ate?: string | null };
	fonte: Record<string, string | null>;
	pagina_pdf: string | null;
	url_path: string;
	permalink: string;
	recorte: string;
	contexto_curto: string;
	metadados_linha: string;
	nome_acessivel: string;
	relacionados?: Item[];
};

export type FonteItem = {
	kind: 'item';
	item: Item;
};

export type FonteProse = {
	kind: 'prose';
	documento_id: string;
	documento: string;
	page: number;
	block_id: string;
	type: string;
	texto: string;
	item_codigo?: string | null;
	url_path: string;
};

export type Fonte = FonteItem | FonteProse;
export type CitedSource = Fonte & { n: number };

export type ProseBlock = {
	id: string;
	type: string;
	text: string;
	page: number;
	seq: number;
	item_codigo?: string | null;
};

export type ProseDocumentMeta = {
	id: string;
	nome: string;
	page_count: number;
	extracted_at: string | null;
};

export type ProsePagePayload = {
	documento_id: string;
	page: number;
	width: number;
	height: number;
	blocks: ProseBlock[];
};

export type Suggestion = {
	codigo: string;
	texto: string;
	texto_completo: string;
	contexto: string;
	url_path: string;
	nome_acessivel: string;
};

export type SuggestionResponse = {
	q: string;
	items: Suggestion[];
	ver_mais: boolean;
	anuncio: string;
};

export type InferredChip = {
	kind: string;
	id: string;
	label: string;
	phrase: string;
};

export type SearchResponse = {
	q: string;
	total: number;
	offset: number;
	limit: number;
	atalho_codigo: boolean;
	items: Item[];
	trechos?: FonteProse[];
	recorte: string;
	inferred?: InferredChip[];
};

export type TaxOption = {
	id: string;
	nome: string;
	slug?: string;
	etapa?: string | null;
	area?: string | null;
	sigla?: string | null;
	tipo?: string;
	faixa?: string | null;
	anos?: number[];
	presenca?: { anos?: number[] } | null;
	tem_aprendizagens?: boolean;
};

export type Taxonomies = {
	etapas: TaxOption[];
	anos: TaxOption[];
	componentes: TaxOption[];
	areas: TaxOption[];
	campos?: TaxOption[];
	documentos: TaxOption[];
	tipos: TaxOption[];
	competencias?: (TaxOption & { tipo?: string })[];
};
