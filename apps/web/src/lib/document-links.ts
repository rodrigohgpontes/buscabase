export type OfficialDocumentLink = {
	href: string;
	label: string;
};

const LINKS: Record<string, OfficialDocumentLink[]> = {
	'bncc-2018': [
		{
			href: 'https://basenacionalcomum.mec.gov.br/images/BNCC_EI_EF_110518_versaofinal_site.pdf',
			label: 'PDF homologado da Base Nacional Comum Curricular'
		}
	],
	'computacao-2022': [
		{
			href: 'https://www.gov.br/mec/pt-br/cne/pdf/pareceres-do-cne/ceb/2022/anexo-ao-parecer-cneceb-no-2-2022-bncc-computacao.pdf',
			label: 'Anexo ao Parecer CNE/CEB nº 2/2022'
		},
		{
			href: 'https://www.gov.br/mec/pt-br/cne/pdf/pareceres-do-cne/ceb/2022/pceb002_22.pdf',
			label: 'Parecer CNE/CEB nº 2/2022'
		},
		{
			href: 'https://www.gov.br/mec/pt-br/cne/pdf/resolucoes-do-cne/ceb/2022/rceb001_22.pdf',
			label: 'Resolução CNE/CEB nº 1/2022'
		}
	],
	'arte-2026': [
		{
			href: 'https://www.gov.br/mec/pt-br/cne/2026/marco-2026/pceb002_26.pdf',
			label: 'Parecer CNE/CEB nº 2/2026'
		}
	]
};

export function officialDocumentLinks(
	documentoId: string | null | undefined
): OfficialDocumentLink[] {
	if (!documentoId) return [];
	return LINKS[documentoId] ?? [];
}
