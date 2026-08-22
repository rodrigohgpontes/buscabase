export type AnswerInline =
	| { type: 'text'; text: string }
	| { type: 'bold'; text: string }
	| { type: 'citation'; n: number };

export type AnswerBlock =
	| { type: 'paragraph'; parts: AnswerInline[] }
	| { type: 'list'; ordered: boolean; items: AnswerInline[][] }
	| { type: 'heading'; text: string };

const CITATION_RE = /\[(\d+)\]/g;
const BOLD_RE = /\*\*([^*]+)\*\*/g;
const HEADING_RE = /^#{1,6}\s+(.+)$/;
const UL_RE = /^[-*•]\s+(.+)$/;
const OL_RE = /^(\d+)[.)]\s+(.+)$/;

function parseInlines(text: string): AnswerInline[] {
	const parts: AnswerInline[] = [];
	const combined = /(\*\*[^*]+\*\*|\[\d+\])/g;
	let last = 0;
	let match: RegExpExecArray | null;
	while ((match = combined.exec(text)) !== null) {
		if (match.index > last) {
			parts.push({ type: 'text', text: text.slice(last, match.index) });
		}
		const token = match[0];
		const bold = /^\*\*([^*]+)\*\*$/.exec(token);
		const cite = /^\[(\d+)\]$/.exec(token);
		if (bold) {
			parts.push({ type: 'bold', text: bold[1] });
		} else if (cite) {
			parts.push({ type: 'citation', n: Number(cite[1]) });
		}
		last = match.index + token.length;
	}
	if (last < text.length) {
		parts.push({ type: 'text', text: text.slice(last) });
	}
	return parts.length ? parts : [{ type: 'text', text }];
}

function stripHeadingMarkers(line: string): string {
	const heading = HEADING_RE.exec(line.trim());
	if (heading) return heading[1].trim();
	return line.replace(BOLD_RE, '$1').trim();
}

/** Parse model markdown into readable blocks (no HTML injection). */
export function parseAnswer(raw: string): AnswerBlock[] {
	const text = (raw || '').replace(/\r\n/g, '\n').trim();
	if (!text) return [];

	const lines = text.split('\n');
	const blocks: AnswerBlock[] = [];
	let paragraph: string[] = [];
	let listItems: AnswerInline[][] | null = null;
	let listOrdered = false;

	function flushParagraph() {
		if (!paragraph.length) return;
		const joined = paragraph.join(' ').replace(/\s+/g, ' ').trim();
		if (joined) blocks.push({ type: 'paragraph', parts: parseInlines(joined) });
		paragraph = [];
	}

	function flushList() {
		if (listItems?.length) {
			blocks.push({ type: 'list', ordered: listOrdered, items: listItems });
		}
		listItems = null;
	}

	for (const line of lines) {
		const trimmed = line.trim();
		if (!trimmed) {
			flushParagraph();
			flushList();
			continue;
		}

		const heading = HEADING_RE.exec(trimmed);
		if (heading) {
			flushParagraph();
			flushList();
			blocks.push({ type: 'heading', text: stripHeadingMarkers(trimmed) });
			continue;
		}

		const ul = UL_RE.exec(trimmed);
		if (ul) {
			flushParagraph();
			if (!listItems || listOrdered) {
				flushList();
				listItems = [];
				listOrdered = false;
			}
			listItems.push(parseInlines(ul[1]));
			continue;
		}

		const ol = OL_RE.exec(trimmed);
		if (ol) {
			flushParagraph();
			if (!listItems || !listOrdered) {
				flushList();
				listItems = [];
				listOrdered = true;
			}
			listItems.push(parseInlines(ol[2]));
			continue;
		}

		flushList();
		paragraph.push(trimmed);
	}

	flushParagraph();
	flushList();
	return blocks;
}

export function snippetText(text: string, max = 180): string {
	const clean = (text || '').replace(/\s+/g, ' ').trim();
	if (clean.length <= max) return clean;
	return clean.slice(0, max - 1).trimEnd() + '…';
}

/** Collect citation numbers present in the answer for a11y / linking. */
export function citationNumbers(raw: string): number[] {
	const found = new Set<number>();
	for (const match of raw.matchAll(CITATION_RE)) {
		found.add(Number(match[1]));
	}
	return [...found].sort((a, b) => a - b);
}

/** Citation numbers in order of first appearance in the text. */
export function citationOrder(raw: string): number[] {
	const seen = new Set<number>();
	const order: number[] = [];
	for (const match of raw.matchAll(CITATION_RE)) {
		const n = Number(match[1]);
		if (seen.has(n)) continue;
		seen.add(n);
		order.push(n);
	}
	return order;
}

/**
 * Keep only sources cited in the answer and renumber them [1]…[k]
 * in order of first appearance, rewriting the answer text to match.
 */
export function normalizeCitations<T>(
	raw: string,
	sources: T[]
): { text: string; sources: Array<T & { n: number }> } {
	const original = citationOrder(raw).filter((n) => n >= 1 && n <= sources.length);
	if (!original.length) {
		return { text: raw, sources: [] };
	}

	const map = new Map<number, number>();
	const cited = original.map((oldN, index) => {
		const n = index + 1;
		map.set(oldN, n);
		return { ...sources[oldN - 1], n };
	});

	const text = raw.replace(CITATION_RE, (token, digits: string) => {
		const oldN = Number(digits);
		const next = map.get(oldN);
		return next === undefined ? token : `[${next}]`;
	});

	return { text, sources: cited };
}

/** @deprecated Prefer normalizeCitations — kept for callers that only need the list. */
export function citedSources<T>(raw: string, sources: T[]): Array<T & { n: number }> {
	return normalizeCitations(raw, sources).sources;
}
