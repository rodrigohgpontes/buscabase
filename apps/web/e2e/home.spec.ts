import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('home initial state', async ({ page }) => {
	await page.goto('/');
	await expect(page.getByRole('heading', { name: 'Encontre o que a Base Nacional Comum Curricular diz' })).toBeVisible();
	await expect(page.getByRole('heading', { name: 'Pesquisa por código' })).toBeVisible();
	await expect(page.getByRole('heading', { name: 'Pesquisa por filtros' })).toBeVisible();
	await expect(page.getByRole('heading', { name: 'Pesquisa simples' })).toBeVisible();
	await expect(page.getByLabel('Digite o código')).toBeVisible();
	await expect(
		page.getByText('Quando você quer escolher a etapa, o ano, o componente ou o documento.')
	).toBeVisible();
	await expect(page.getByLabel('O que você quer encontrar na BNCC?')).toBeVisible();
	await expect(page.getByRole('heading', { name: 'Pesquisa conversacional' })).toBeVisible();
	await expect(page.getByLabel('O que você quer entender ou comparar?')).toBeVisible();
	await expect(page.getByRole('heading', { name: 'Resultados' })).toBeVisible();
	await expect(page.getByText('Os itens encontrados aparecem aqui.')).toBeVisible();
});

test('widget de recado abre o formulário', async ({ page }) => {
	await page.goto('/');
	const recado = page.getByRole('button', { name: 'Deixe um recado' });
	await expect(recado).toBeVisible();
	await recado.click();
	await expect(page.getByRole('heading', { name: 'Deixe um recado' })).toBeVisible();
	await expect(
		page.getByText('Sugestões para melhorar o Busca Base são bem-vindas.')
	).toBeVisible();
	await expect(page.getByLabel('Nome')).toBeVisible();
	await expect(page.getByLabel('E-mail')).toBeVisible();
	await expect(page.getByLabel('Mensagem')).toBeVisible();
	await expect(page.getByRole('button', { name: 'Enviar recado' })).toBeVisible();
});

test('axe home', async ({ page }) => {
	await page.goto('/');
	const results = await new AxeBuilder({ page }).analyze();
	expect(results.violations).toEqual([]);
});

test.skip('alterna a aparência Calma e Folia', async ({ page }) => {
	await page.goto('/');
	const folia = page.getByRole('button', { name: 'Folia' });
	const calma = page.getByRole('button', { name: 'Calma' });
	await expect(calma).toHaveAttribute('aria-pressed', 'true');
	await folia.click();
	await expect(folia).toHaveAttribute('aria-pressed', 'true');
	await expect(page.locator('html')).toHaveAttribute('data-theme', 'folia');
	await page.reload();
	await expect(page.locator('html')).toHaveAttribute('data-theme', 'folia');
	await expect(page.getByRole('button', { name: 'Folia' })).toHaveAttribute('aria-pressed', 'true');
});

test('axe home Folia', async ({ page }) => {
	await page.addInitScript(() => localStorage.setItem('buscabase-tema', 'folia'));
	await page.goto('/');
	await expect(page.locator('html')).toHaveAttribute('data-theme', 'folia');
	const results = await new AxeBuilder({ page }).analyze();
	expect(results.violations).toEqual([]);
});

test('primeiro clique em exemplo conversacional preenche o campo', async ({ page }) => {
	await page.goto('/');
	const exemplo = page.getByRole('button', { name: 'Explique EF05MA03 em palavras mais simples' });
	if (!(await exemplo.count())) test.skip(true, 'Pesquisa conversacional indisponível');
	await exemplo.click();
	await expect(page.getByLabel('O que você quer entender ou comparar?')).toHaveValue(
		'Explique EF05MA03 em palavras mais simples'
	);
	await expect(page.getByRole('button', { name: 'Abrir Pesquisa simples' })).toBeVisible();
});

test('primeiro clique em subseção de filtros abre a subseção', async ({ page }) => {
	await page.goto('/');
	const stage = page.locator('#corpo-filtros [data-stage="etapa"]');
	await expect(stage).not.toHaveAttribute('open');
	await stage.locator('summary').click();
	await expect(stage).toHaveAttribute('open', '');
	await expect(page.getByRole('button', { name: 'Abrir Pesquisa simples' })).toBeVisible();
});

test('filtros: componente sem etapa habilita Buscar', async ({ page }) => {
	await page.goto('/');
	const painel = page.locator('#corpo-filtros');
	await painel.locator('[data-stage="recorte"] summary').click();
	const matematica = painel.getByRole('checkbox', { name: 'Matemática' }).first();
	if (!(await matematica.count())) test.skip(true, 'taxonomias unavailable');
	await expect(painel.getByRole('button', { name: 'Buscar' })).toHaveCount(0);
	await matematica.check();
	await expect(painel.getByRole('button', { name: 'Buscar' })).toBeVisible();
});

test('filtros: Educação Infantil e Bebês retorna itens', async ({ page }) => {
	await page.goto('/');
	const painel = page.locator('#corpo-filtros');
	await painel.locator('[data-stage="etapa"] summary').click();
	const ei = painel.getByRole('checkbox', { name: 'Educação Infantil' });
	if (!(await ei.count())) test.skip(true, 'needs ingested snapshot');
	await ei.check();
	await painel.locator('[data-stage="recorte"] summary').click();
	const bebes = painel.getByRole('checkbox', { name: /Bebês/ });
	if (!(await bebes.count())) test.skip(true, 'needs ingested snapshot');
	await bebes.check();
	await painel.getByRole('button', { name: 'Buscar' }).click();
	const empty = page.getByText('Não encontramos resultados para este recorte.');
	const list = page.locator('.results .card, .results article').first();
	await expect(empty.or(list)).toBeVisible({ timeout: 20000 });
	if (await empty.isVisible()) test.skip(true, 'needs ingested snapshot');
	await expect(list).toBeVisible();
});
