import { describe, expect, it } from 'vitest';
import { deviceClass, pageClass, referrerHost, shouldRecordPage, usoGuard } from './usage';

describe('pageClass', () => {
	it('distingue início vazio de início com consulta', () => {
		expect(pageClass('/', new URLSearchParams())).toBe('home');
		expect(pageClass('/', new URLSearchParams('modo=buscar&q=frações'))).toBe('home_consulta');
	});

	it('classifica páginas da Base', () => {
		expect(pageClass('/habilidade/EF05MA03', new URLSearchParams())).toBe('habilidade');
		expect(pageClass('/aprendizagem/EI03EO01', new URLSearchParams())).toBe('habilidade');
		expect(pageClass('/indices', new URLSearchParams())).toBe('indices');
		expect(pageClass('/documento/bncc-2018', new URLSearchParams())).toBe('documento');
		expect(pageClass('/ano/5', new URLSearchParams())).toBe('dimensao');
		expect(pageClass('/sobre', new URLSearchParams())).toBe('institucional');
		expect(pageClass('/contato', new URLSearchParams())).toBe('outro');
	});
});

describe('shouldRecordPage', () => {
	it('ignora uso, api e arquivos de descoberta', () => {
		expect(shouldRecordPage('/uso')).toBe(false);
		expect(shouldRecordPage('/api/uso')).toBe(false);
		expect(shouldRecordPage('/robots.txt')).toBe(false);
		expect(shouldRecordPage('/')).toBe(true);
		expect(shouldRecordPage('/habilidade/EF05MA03')).toBe(true);
	});
});

describe('deviceClass', () => {
	it('separa bot, celular e computador', () => {
		expect(deviceClass('Mozilla/5.0 Googlebot/2.1')).toBe('bot');
		expect(deviceClass('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)')).toBe('mobile');
		expect(deviceClass('Mozilla/5.0 (X11; Linux x86_64) Firefox/128.0')).toBe('desktop');
	});
});

describe('referrerHost', () => {
	it('guarda só o host e ignora o próprio site', () => {
		expect(referrerHost('https://www.google.com/search?q=bncc')).toBe('google.com');
		expect(referrerHost('https://www.buscabase.com.br/?modo=buscar', 'www.buscabase.com.br')).toBe(
			undefined
		);
	});
});

describe('usoGuard', () => {
	it('some se não há senha', () => {
		expect(usoGuard('', 'uso', null)).toBe(404);
		expect(usoGuard(undefined, 'uso', 'Basic dXNvOnx')).toBe(404);
	});

	it('pede credencial ou recusa a errada', () => {
		expect(usoGuard('segredo', 'uso', null)).toBe(401);
		expect(usoGuard('segredo', 'uso', `Basic ${btoa('uso:errado')}`)).toBe(401);
		expect(usoGuard('segredo', 'uso', `Basic ${btoa('uso:segredo')}`)).toBe(200);
	});
});
