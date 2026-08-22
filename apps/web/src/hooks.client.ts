import type { HandleClientError } from '@sveltejs/kit';

export const handleError: HandleClientError = ({ status }) => {
	if (status === 404) {
		return {
			message: 'Não encontramos esta página.',
			titulo: 'Página não encontrada',
			texto: 'Ela pode ter mudado de endereço ou ainda não estar no recorte atual.'
		};
	}
	return {
		message: 'Não foi possível concluir agora.',
		titulo: 'Não foi possível concluir agora',
		texto: 'Sua consulta foi preservada. Tente novamente ou volte à busca.'
	};
};
