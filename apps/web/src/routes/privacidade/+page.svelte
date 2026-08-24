<script lang="ts">
	import MetasSociais from '$lib/components/MetasSociais.svelte';
	import { absoluteUrl } from '$lib/social';

	let { data } = $props();

	const title = 'Privacidade | Busca Base';
	const description =
		'Como o Busca Base trata dados pessoais segundo a LGPD: consultas, registros operacionais, serviços externos e direitos.';
</script>

<svelte:head>
	<title>{title}</title>
	<meta name="description" content={description} />
</svelte:head>

<MetasSociais {title} {description} url={absoluteUrl('/privacidade')} />

<div class="wrap reading">
	<nav class="breadcrumbs" aria-label="Trilha">
		<a href="/">Busca Base</a>
		<span aria-hidden="true">›</span>
		<span>Privacidade</span>
	</nav>
	<h1>Privacidade</h1>
	<p>
		O Busca Base não exige conta. Não pedimos escola nem dados de estudante. Nome e e-mail só
		aparecem se você mandar um recado.
	</p>
	<p>
		Esta página descreve o tratamento de dados pessoais segundo a Lei Geral de Proteção de Dados
		(LGPD).
	</p>

	<h2>Quem é responsável</h2>
	<p>
		O responsável pelo tratamento (controlador) é Rodrigo Pontes. Para exercer direitos ou tirar
		dúvidas: <a href="mailto:contato@rodrigopontes.com.br">contato@rodrigopontes.com.br</a>.
	</p>

	<h2>O que tratamos</h2>
	<p>
		Não criamos cadastro. Não pedimos escola nem identificadores de estudante. Nome e e-mail só são
		pedidos se você escolher mandar um recado, para podermos responder.
	</p>
	<p>
		Quando você busca ou pergunta, o texto da consulta é processado para devolver resultados ou uma
		resposta com fontes. Evite colar dados pessoais — o site não precisa deles.
	</p>
	<p>
		Guardamos as consultas neste servidor (texto da busca ou da pergunta, filtros, códigos
		encontrados, modo, tempo de resposta e se houve resultado) para operar o site e entender o
		uso. Esse registro não tem prazo de apagamento automático. Não fica em serviço de medição de
		terceiros.
	</p>
	<p>
		Não gravamos o endereço IP junto da consulta. O servidor que entrega o site pode registrar
		dados técnicos de acesso, como IP, pelo tempo necessário à operação e à segurança.
	</p>
	<p>
		Se você mandar um recado, guardamos neste servidor o nome, o e-mail, a mensagem e a página em
		que o recado foi enviado. Não usamos ferramenta de formulário de terceiros. A base é o
		consentimento ao enviar. Para apagar um recado, escreva para
		<a href="mailto:contato@rodrigopontes.com.br">contato@rodrigopontes.com.br</a>.
	</p>

	<h2>Cache</h2>
	<p>
		Resultados de busca e respostas de Perguntar podem ser guardados por até 7 dias, com chave
		protegida por código autenticado. Isso evita repetir o mesmo trabalho e não cria um histórico
		público da conversa.
	</p>

	<h2>O que fica só no seu aparelho</h2>
	<p>
		O histórico de Perguntar fica só nesta sessão do navegador. Você pode copiar a resposta com as
		fontes ou compartilhar um link que guarda a conversa no próprio endereço — o servidor não
		armazena essa conversa.
	</p>
	<p>
		A escolha entre Calma e Folia fica só neste navegador. Não enviamos essa preferência ao
		servidor.
	</p>
	<p>Não usamos cookies de medição ou publicidade.</p>

	<h2>Para que e com que base</h2>
	<p>Tratamos esses dados para:</p>
	<ul>
		<li>atender o pedido de consulta, busca ou pergunta;</li>
		<li>manter o site funcionando e diagnosticar falhas;</li>
		<li>entender o uso do serviço;</li>
		<li>evitar trabalho repetido com o cache de curta duração;</li>
		<li>receber e responder recados, quando você os envia.</li>
	</ul>
	<p>
		A base é o atendimento do seu pedido, o interesse legítimo em operar e proteger o serviço, sem
		prejudicar direitos, e o consentimento quando você manda um recado.
	</p>

	<h2>Compartilhamento e tratamento fora do Brasil</h2>
	<p>
		A busca por tema envia o texto da consulta à OpenRouter, que encaminha a serviços de embeddings
		e, quando a chave está configurada, de reordenação. Esses serviços recebem a consulta para
		devolver vetores e uma ordem de relevância.
	</p>
	<p>
		Perguntar envia a pergunta, até oito turnos da conversa e os trechos recuperados da Base à
		OpenRouter, que encaminha a um serviço de geração de respostas por inteligência artificial. Se
		esse serviço estiver indisponível, só Perguntar é desligado. Por código e Buscar continuam no
		ar. Não há substituição silenciosa por outro gerador.
	</p>
	<p>
		Esse processamento pode ocorrer fora do Brasil, na medida necessária para devolver o resultado.
		Não usamos o texto das consultas para treinar modelos próprios.
	</p>

	<h2>Seus direitos</h2>
	<p>Você pode pedir:</p>
	<ul>
		<li>confirmação de que tratamos dados seus;</li>
		<li>acesso aos dados;</li>
		<li>correção de dados incompletos ou desatualizados;</li>
		<li>
			anonimização, bloqueio ou eliminação de dados desnecessários ou tratados em desacordo com a
			LGPD;
		</li>
		<li>informação sobre o compartilhamento;</li>
		<li>portabilidade, quando couber;</li>
		<li>revogação de consentimento, quando o tratamento tiver se baseado nele.</li>
	</ul>
	<p>
		Para exercer, escreva para
		<a href="mailto:contato@rodrigopontes.com.br">contato@rodrigopontes.com.br</a>. Responderemos no
		prazo previsto na LGPD.
	</p>
	<p>
		Se a consulta não tiver dados que permitam identificar você, pode não haver registro pessoal a
		corrigir ou entregar.
	</p>

	<h2>Atualização</h2>
	<p>Se o tratamento mudar, esta página muda. Recorte dos dados: {data.recorte ?? 'não informado'}.</p>
	<p><a class="btn btn-primary" href="/">Buscar na Base</a></p>
</div>
