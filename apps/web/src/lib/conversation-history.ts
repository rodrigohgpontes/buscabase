export type ConversationHistoryTurn = {
	role: 'user' | 'assistant';
	text: string;
	citedSources?: { kind?: string; item?: { codigo: string } }[];
};

export type HistoryPayloadTurn = {
	role: 'user' | 'assistant';
	content: string;
	codigos?: string[];
};

/** Prior turns sent to /api/perguntar — text plus cited codes, not the current question. */
export function conversationHistory(turns: ConversationHistoryTurn[]): HistoryPayloadTurn[] {
	return turns.map((turn) => {
		const codigos = [
			...new Set(
				(turn.citedSources || [])
					.filter((entry) => entry.kind !== 'prose')
					.map((entry) => entry.item?.codigo)
					.filter((codigo): codigo is string => Boolean(codigo))
			)
		];
		return {
			role: turn.role,
			content: turn.text,
			...(codigos.length ? { codigos } : {})
		};
	});
}
