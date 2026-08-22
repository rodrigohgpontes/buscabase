export type ShareTarget = {
	id: 'whatsapp' | 'linkedin' | 'telegram' | 'email';
	label: string;
	href: string;
};

export function shareSearchText(): string {
	return 'Consulta na BNCC no Busca Base';
}

export function shareItemText(codigo: string): string {
	return `${codigo} na BNCC — Busca Base`;
}

export function shareConversationText(): string {
	return 'Conversa sobre a BNCC no Busca Base';
}

export function shareTargets(url: string, text: string): ShareTarget[] {
	const encodedUrl = encodeURIComponent(url);
	const encodedText = encodeURIComponent(text);
	const message = encodeURIComponent(`${text}\n${url}`);

	return [
		{
			id: 'whatsapp',
			label: 'WhatsApp',
			href: `https://wa.me/?text=${message}`
		},
		{
			id: 'linkedin',
			label: 'LinkedIn',
			href: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`
		},
		{
			id: 'telegram',
			label: 'Telegram',
			href: `https://t.me/share/url?url=${encodedUrl}&text=${encodedText}`
		},
		{
			id: 'email',
			label: 'E-mail',
			href: `mailto:?subject=${encodedText}&body=${message}`
		}
	];
}
