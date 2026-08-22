import type { ProseBlock } from '$lib/types';

export type ProseRenderGroup =
	| { kind: 'list'; blocks: ProseBlock[] }
	| { kind: 'table'; blocks: ProseBlock[] }
	| { kind: 'single'; block: ProseBlock };

export function groupProseBlocks(blocks: ProseBlock[]): ProseRenderGroup[] {
	const groups: ProseRenderGroup[] = [];
	let index = 0;
	while (index < blocks.length) {
		const current = blocks[index];
		if (current.type === 'list_item') {
			const list: ProseBlock[] = [];
			while (index < blocks.length && blocks[index].type === 'list_item') {
				list.push(blocks[index]);
				index += 1;
			}
			groups.push({ kind: 'list', blocks: list });
			continue;
		}
		if (current.type === 'table_header' || current.type === 'table_cell') {
			const table: ProseBlock[] = [];
			while (
				index < blocks.length &&
				(blocks[index].type === 'table_header' || blocks[index].type === 'table_cell')
			) {
				table.push(blocks[index]);
				index += 1;
			}
			groups.push({ kind: 'table', blocks: table });
			continue;
		}
		groups.push({ kind: 'single', block: current });
		index += 1;
	}
	return groups;
}

export function headingTag(type: string): 'h2' | 'h3' | 'h4' | 'p' | 'article' {
	if (type === 'heading_1' || type === 'title') return 'h2';
	if (type === 'heading_2') return 'h3';
	if (type === 'heading_3') return 'h4';
	if (type === 'article' || type === 'card') return 'article';
	return 'p';
}

export function isChromeType(type: string): boolean {
	return type === 'running_header' || type === 'running_footer' || type === 'page_number';
}
