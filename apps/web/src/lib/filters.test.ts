import { describe, expect, it } from 'vitest';
import {
	appliedChips,
	emptyFilterReason,
	formatAppliedCount,
	groupByEtapa,
	hasFilterScope,
	helpDependente,
	joinNomes,
	keepAllowed,
	nomeAno,
	nomeComContexto,
	needsGrouping,
	pruneSelection,
	showsEiAxes,
	showsEscolarAxes,
	visibleAnos,
	visibleCampos,
	visibleComponentes,
	visibleForEtapas,
	visibleTipos
} from '$lib/filters';
import type { TaxOption, Taxonomies } from '$lib/types';

const etapas: TaxOption[] = [
	{ id: 'EI', nome: 'Educação Infantil' },
	{ id: 'EF', nome: 'Ensino Fundamental' },
	{ id: 'EM', nome: 'Ensino Médio' }
];

const anos: TaxOption[] = [
	{ id: 'ei-grupo-01', nome: 'Bebês', etapa: 'EI', tipo: 'grupo_etario', faixa: '0–1a6m' },
	{ id: 'ei-grupo-03', nome: 'Crianças pequenas', etapa: 'EI', tipo: 'grupo_etario', faixa: '4a–5a11m' },
	{ id: 'ef-ano-03', nome: '3º ano', etapa: 'EF', tipo: 'ano', anos: [3] },
	{ id: 'ef-ano-05', nome: '5º ano', etapa: 'EF', tipo: 'ano', anos: [5] },
	{ id: 'ef-ano-06', nome: '6º ano', etapa: 'EF', tipo: 'ano', anos: [6] },
	{ id: 'em-sem-seriacao', nome: 'Sem seriação', etapa: 'EM', tipo: 'sem_seriacao' }
];

const componentes: TaxOption[] = [
	{ id: 'ef-comp-ma', nome: 'Matemática', etapa: 'EF', area: 'ef-area-matematica' },
	{ id: 'em-comp-mat', nome: 'Matemática', etapa: 'EM', area: 'em-area-mat' },
	{ id: 'ef-comp-lp', nome: 'Língua Portuguesa', etapa: 'EF', area: 'ef-area-linguagens' },
	{
		id: 'ef-comp-li',
		nome: 'Língua Inglesa',
		etapa: 'EF',
		area: 'ef-area-linguagens',
		sigla: 'LI',
		presenca: { anos: [6, 7, 8, 9] }
	},
	{
		id: 'em-comp-biologia',
		nome: 'Biologia',
		etapa: 'EM',
		area: 'em-area-cnt',
		tem_aprendizagens: false
	},
	{ id: 'co-comp', nome: 'Computação', etapa: null, area: null }
];

const areas: TaxOption[] = [
	{ id: 'ef-area-matematica', nome: 'Matemática', etapa: 'EF' },
	{ id: 'ef-area-linguagens', nome: 'Linguagens', etapa: 'EF' },
	{ id: 'em-area-cnt', nome: 'Ciências da Natureza e suas Tecnologias', etapa: 'EM' }
];

const campos: TaxOption[] = [
	{ id: 'ei-campo-eo', nome: 'O eu, o outro e o nós' },
	{ id: 'ei-campo-cg', nome: 'Corpo, gestos e movimentos' }
];

const tipos: TaxOption[] = [
	{ id: 'habilidade', nome: 'Habilidade' },
	{ id: 'objetivo', nome: 'Objetivo de aprendizagem e desenvolvimento' },
	{ id: 'competencia_geral', nome: 'Competência geral' },
	{ id: 'competencia_especifica', nome: 'Competência específica' }
];

const tax: Taxonomies = {
	etapas,
	anos,
	componentes,
	areas,
	campos,
	documentos: [{ id: 'bncc-2018', nome: 'Base Nacional Comum Curricular' }],
	tipos
};

describe('joinNomes', () => {
	it('liga dois nomes com e', () => {
		expect(joinNomes(['Educação Infantil', 'Ensino Fundamental'])).toBe(
			'Educação Infantil e Ensino Fundamental'
		);
	});
});

describe('formatAppliedCount', () => {
	it('usa singular e plural', () => {
		expect(formatAppliedCount(1)).toBe('1 filtro aplicado');
		expect(formatAppliedCount(2)).toBe('2 filtros aplicados');
	});
});

describe('nomeAno', () => {
	it('acrescenta a faixa etária', () => {
		expect(nomeAno(anos[0])).toBe('Bebês (0–1a6m)');
		expect(nomeAno(anos[3])).toBe('5º ano');
	});
});

describe('hasFilterScope e eixos', () => {
	it('aceita qualquer recorte, não só etapa', () => {
		expect(
			hasFilterScope({
				etapas: [],
				anos: [],
				componentes: ['ef-comp-ma'],
				areas: [],
				campos: [],
				documentos: [],
				tipos: [],
				incluirRevogados: false
			})
		).toBe(true);
		expect(showsEiAxes([])).toBe(true);
		expect(showsEiAxes(['EF'])).toBe(false);
		expect(showsEscolarAxes(['EI'])).toBe(false);
		expect(showsEscolarAxes(['EF'])).toBe(true);
	});
});

describe('visibleForEtapas', () => {
	it('mantém itens sem etapa e os da etapa escolhida', () => {
		const visible = visibleForEtapas(componentes, ['EF']);
		expect(visible.map((item) => item.id)).toEqual([
			'ef-comp-ma',
			'ef-comp-lp',
			'ef-comp-li',
			'co-comp'
		]);
	});

	it('mostra todos quando nenhuma etapa está marcada', () => {
		expect(visibleForEtapas(anos, []).length).toBe(6);
	});
});

describe('visibleTipos e visibleCampos', () => {
	it('reduz tipos pela etapa', () => {
		expect(visibleTipos(tipos, ['EI']).map((tipo) => tipo.id)).toEqual([
			'objetivo',
			'competencia_geral'
		]);
		expect(visibleTipos(tipos, ['EF']).map((tipo) => tipo.id)).toEqual([
			'habilidade',
			'competencia_geral',
			'competencia_especifica'
		]);
		expect(visibleTipos(tipos, []).length).toBe(4);
	});

	it('esconde campos fora da Educação Infantil', () => {
		expect(visibleCampos(campos, ['EI']).length).toBe(2);
		expect(visibleCampos(campos, ['EF']).length).toBe(0);
		expect(visibleCampos(campos, []).length).toBe(2);
	});
});

describe('visibleComponentes', () => {
	it('reduz por área depois da etapa e omite componente sem aprendizagens', () => {
		const visible = visibleComponentes(componentes, ['EF'], ['ef-area-matematica']);
		expect(visible.map((item) => item.id)).toEqual(['ef-comp-ma']);
	});

	it('esconde Computação nas faixas de bebês e bem pequenas', () => {
		const visible = visibleComponentes(componentes, ['EI'], [], [anos[0]]);
		expect(visible.map((item) => item.id)).not.toContain('co-comp');
	});
});

describe('visibleAnos', () => {
	it('restringe anos quando o componente tem presença', () => {
		const visible = visibleAnos(anos, ['EF'], [componentes[3]]);
		expect(visible.map((item) => item.id)).toEqual(['ef-ano-06']);
	});
});

describe('keepAllowed', () => {
	it('remove anos que saíram da etapa', () => {
		const remaining = keepAllowed(['ef-ano-05', 'ei-grupo-01'], visibleForEtapas(anos, ['EF']));
		expect(remaining).toEqual(['ef-ano-05']);
	});
});

describe('pruneSelection', () => {
	it('retira tipo e campo ilegais ao mudar a etapa', () => {
		const pruned = pruneSelection(
			{
				etapas: ['EI'],
				anos: ['ef-ano-05'],
				componentes: ['ef-comp-ma'],
				areas: ['ef-area-matematica'],
				campos: ['ei-campo-eo'],
				documentos: ['bncc-2018'],
				tipos: ['habilidade'],
				incluirRevogados: false
			},
			tax
		);
		expect(pruned.anos).toEqual([]);
		expect(pruned.componentes).toEqual([]);
		expect(pruned.areas).toEqual([]);
		expect(pruned.tipos).toEqual([]);
		expect(pruned.campos).toEqual(['ei-campo-eo']);
	});
});

describe('emptyFilterReason', () => {
	it('explica EI com habilidade', () => {
		expect(
			emptyFilterReason(
				{
					etapas: ['EI'],
					anos: [],
					componentes: [],
					areas: [],
					campos: [],
					documentos: [],
					tipos: ['habilidade'],
					incluirRevogados: false
				},
				tax
			).texto
		).toContain('objetivos de aprendizagem');
	});

	it('explica Inglês antes do 6º ano', () => {
		expect(
			emptyFilterReason(
				{
					etapas: ['EF'],
					anos: ['ef-ano-03'],
					componentes: ['ef-comp-li'],
					areas: [],
					campos: [],
					documentos: [],
					tipos: [],
					incluirRevogados: false
				},
				tax
			).texto
		).toContain('6º ano');
	});

	it('explica componente sem aprendizagens', () => {
		expect(
			emptyFilterReason(
				{
					etapas: ['EM'],
					anos: [],
					componentes: ['em-comp-biologia'],
					areas: [],
					campos: [],
					documentos: [],
					tipos: [],
					incluirRevogados: false
				},
				tax
			).texto
		).toContain('área');
	});
});

describe('groupByEtapa', () => {
	it('agrupa e separa complementos', () => {
		const groups = groupByEtapa(componentes, etapas);
		expect(groups.map((group) => group.nome)).toEqual([
			'Ensino Fundamental',
			'Ensino Médio',
			'Complementos'
		]);
	});
});

describe('needsGrouping', () => {
	it('omite grupo quando só uma etapa está escolhida', () => {
		expect(needsGrouping(1, 2)).toBe(false);
		expect(needsGrouping(0, 2)).toBe(true);
	});
});

describe('nomeComContexto', () => {
	it('acrescenta a etapa quando o nome se repete', () => {
		expect(nomeComContexto(componentes[0], componentes, etapas)).toBe(
			'Matemática · Ensino Fundamental'
		);
		expect(nomeComContexto(componentes[2], componentes, etapas)).toBe('Língua Portuguesa');
	});
});

describe('helpDependente', () => {
	it('explica a dependência', () => {
		expect(helpDependente([])).toContain('agrupadas');
		expect(helpDependente([etapas[1]])).toBe('Mostrando opções de Ensino Fundamental.');
	});
});

describe('appliedChips', () => {
	it('lista rótulos removíveis na ordem da hierarquia', () => {
		const chips = appliedChips({
			etapas: ['EI'],
			anos: ['ei-grupo-01'],
			componentes: [],
			areas: [],
			campos: ['ei-campo-eo'],
			documentos: ['bncc-2018'],
			tipos: [],
			incluirRevogados: true,
			tax
		});
		expect(chips.map((chip) => chip.label)).toEqual([
			'Educação Infantil',
			'Bebês (0–1a6m)',
			'O eu, o outro e o nós',
			'Base Nacional Comum Curricular',
			'Itens revogados'
		]);
		expect(chips[1].removeLabel).toBe('Remover filtro Bebês (0–1a6m)');
	});
});
