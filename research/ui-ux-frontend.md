# UI, experiência e arquitetura frontend do Busca Base

**Status:** decisão de produto e pesquisa de interface  
**Data:** 2026-08-20  
**Escopo:** interface pública, experiência de uso, frontend, descoberta por buscadores e desempenho  
**Depende de:** [local-llm-semantic-search.md](./local-llm-semantic-search.md), [bncc-dev-reuse-and-search-modes.md](./bncc-dev-reuse-and-search-modes.md) e [bncc-dados-as-sole-source.md](./bncc-dados-as-sole-source.md)  
**Guias relacionados:** [ux-writing-style-guide.md](./ux-writing-style-guide.md) e [design-style-guide.md](./design-style-guide.md)

Este documento não redefine ingestão, recuperação, modelos ou hospedagem. Ele transforma as decisões técnicas já tomadas em uma experiência pública para o **Busca Base**, em [www.buscabase.com.br](https://www.buscabase.com.br).

---

## 1. Decisão resumida

O Busca Base será um site em português brasileiro, centrado em **uma única página de consulta** com quatro modos:

1. **Pesquisa por código** — abre um item oficial a partir de um código;
2. **Pesquisa por filtros** — recorta etapa, ano, campo, área, componente ou documento;
3. **Pesquisa simples** — encontra itens por tema, etapa, ano e componente;
4. **Pesquisa conversacional** — conversa com a Base, compara itens e organiza percursos, sempre com fontes.

Na home em estado inicial, **Pesquisa por código**, **Pesquisa por filtros** e **Pesquisa simples** ficam visíveis e expandidos, nessa ordem. **Pesquisa conversacional** fica visível como seção retrátil e **fechada**. Depois de uma consulta, o modo usado permanece com os resultados; os outros viram botões discretos no topo. Os modos não se misturam em um campo único: cada um deixa claro o que aceita, o que retorna e quanto pode demorar.

A navegação principal será mínima. A página inicial concentra a tarefa. **Sobre**, privacidade, acessibilidade e os índices públicos ficam no rodapé. Em paralelo, o site terá páginas estáveis e indexáveis para habilidades, anos, etapas, componentes e outras dimensões úteis da BNCC. Essas páginas existem para descoberta e referência; todas exibem uma chamada muito visível para continuar a consulta na página inicial.

### Escolha de frontend

- **SvelteKit + Svelte + TypeScript**;
- `adapter-node` no mesmo Docker Compose da aplicação;
- SSR para a primeira resposta e hidratação apenas do necessário;
- pré-renderização das páginas públicas derivadas do snapshot fixado da BNCC;
- FastAPI continua responsável pela busca, conversa, exportações e acesso aos dados;
- Caddy no notebook (ou Traefik no Coolify em produção) entrega assets, aplica compressão e encaminha `/api`;
- CSS próprio com tokens; sem framework visual pesado e sem fonte web na primeira versão;
- Vitest para unidades e Playwright + axe-core para fluxos, acessibilidade e regressão visual.

SvelteKit é uma boa escolha aqui porque combina SSR, pré-renderização por rota, divisão de código e navegação progressiva sem transformar o produto em uma SPA vazia. Isso atende ao mesmo tempo SEO, conexões lentas e uma interface interativa. `adapter-node` também mantém uma implantação previsível em contêiner e permite o frontend separado do FastAPI, como recomenda a documentação do SvelteKit para backends em outra linguagem.

---

## 2. Objetivo do produto

O Busca Base ajuda uma pessoa a **encontrar, entender, conferir e reutilizar** o que a BNCC diz.

O produto não deve:

- parecer um repositório para especialistas;
- exigir que a pessoa conheça a estrutura da BNCC antes de pesquisar;
- fingir que a BNCC é um manual de aula;
- inventar códigos, progressões ou orientações pedagógicas;
- apresentar uma resposta gerada sem os trechos que a sustentam;
- usar “IA” como proposta de valor ou esconder o custo de espera de uma conversa;
- parecer um site oficial do MEC ou do Governo Federal.

### Princípios de experiência

1. **Começar pela intenção.** Código, tema e pergunta são intenções diferentes.
2. **Mostrar a Base, não só uma interpretação.** O texto oficial e seu contexto vêm antes da síntese.
3. **Ajudar a avançar.** Todo erro, vazio ou espera oferece um próximo passo concreto.
4. **Não exigir conhecimento técnico.** Filtros e termos oficiais são explicados no ponto de uso.
5. **Não infantilizar.** Linguagem simples serve tanto a especialistas quanto a iniciantes.
6. **Ser útil antes de estar completo.** Pesquisa por código, Pesquisa por filtros e Pesquisa simples continuam disponíveis se Pesquisa conversacional estiver sobrecarregada.
7. **Facilitar a saída.** Copiar, compartilhar e baixar fazem parte do resultado, não são extras.
8. **Ser rápido no aparelho real.** O caso de referência é um Android básico em rede móvel instável.

---

## 3. Públicos e situações de uso

Personas representam necessidades recorrentes, não caixas demográficas. Uma mesma pessoa pode assumir mais de um papel.

### 3.1 Públicos prioritários

| Pessoa e contexto | O que precisa fazer | Barreiras prováveis | Como o Busca Base ajuda |
|---|---|---|---|
| **Responsável por uma criança**, com pouca familiaridade digital ou escolar | Entender o que a criança deve aprender em determinada etapa | Não conhece códigos nem termos curriculares; receio de “perguntar errado” | Busca por linguagem cotidiana, exemplos de perguntas e explicação sem substituir o texto oficial |
| **Professora ou professor preparando aula** | Encontrar habilidades por tema, ano e componente; copiar para o planejamento | Pouco tempo, celular, necessidade de reutilizar texto | Busca rápida, filtros persistentes, seleção de resultados e cópia com referência |
| **Coordenação pedagógica** | Conferir códigos, comparar anos e orientar planejamento coletivo | Precisa de precisão e contexto completo | Busca exata, comparação, metadados, vigência e fonte oficial |
| **Técnica ou técnico de secretaria de educação** | Analisar cobertura curricular e responder consultas | Vocabulário especializado, muitas consultas e necessidade de rastreabilidade | Filtros estruturais, URLs estáveis, exportação e versão do recorte |

### 3.2 Públicos secundários

- **Estudantes do Ensino Médio, EJA e licenciaturas**, que querem entender objetivos e habilidades sem ler o documento inteiro;
- **gestão escolar**, que precisa localizar referências para projetos, reuniões e comunicação com famílias;
- **pesquisadoras e pesquisadores em educação**, que precisam conferir texto, estrutura, vigência e origem;
- **formadores, editoras e produtoras de material didático**, que verificam alinhamento sem depender de uma resposta gerada;
- **jornalistas, organizações da sociedade civil e equipes de políticas públicas**, que precisam de uma referência pública e compartilhável;
- **pessoas com deficiência, idosas, neurodivergentes ou com letramento limitado**, presentes em todos os grupos anteriores e não tratadas como um público à parte.

### 3.3 Prioridade quando necessidades entram em conflito

1. correção e rastreabilidade;
2. compreensão por quem não domina a BNCC;
3. conclusão da tarefa em celular;
4. velocidade de consulta;
5. eficiência para uso repetido;
6. recursos avançados.

Um atalho para especialista não pode retirar rótulos, contexto ou previsibilidade de quem está chegando pela primeira vez.

---

## 4. Arquitetura de informação

### 4.1 Mapa mínimo de páginas

| Rota conceitual | Finalidade | Indexação |
|---|---|---|
| `/` | Os quatro modos de consulta, resultados e conversa | Sim; página canônica do produto |
| `/sobre` | O que é, limites, fonte dos dados, versão e atribuição | Sim |
| `/privacidade` | Tratamento de consultas, logs e direitos | Sim |
| `/acessibilidade` | Compromissos, recursos e canal para relatar barreiras | Sim |
| `/habilidade/[codigo]` | Registro completo e permalink de uma habilidade | Sim |
| `/aprendizagem/[codigo]` | Objetivos de EI ou complementos que não são “habilidade” | Sim, se a taxonomia do dado exigir |
| `/competencia/[id-ou-slug]` | Competência geral ou específica | Sim |
| `/etapa/[slug]` | Visão de uma etapa | Sim |
| `/ano/[slug]` | Itens de um ano ou faixa | Sim |
| `/area/[slug]` | Área do conhecimento | Sim |
| `/componente/[slug]` | Componente curricular | Sim |
| `/documento/[slug]` | BNCC 2018, Computação e futuros complementos publicados na fonte | Sim |
| `/indices` | Acesso humano às dimensões públicas | Sim; link somente no rodapé da home |

Páginas de campo de experiências, unidade temática e objeto de conhecimento só devem ser indexadas quando tiverem:

- identidade estável no snapshot;
- título compreensível fora da hierarquia;
- conjunto não vazio e conteúdo útil;
- URL canônica;
- introdução própria baseada apenas nos dados;
- links internos coerentes.

Não criar páginas para toda combinação de filtros. “Matemática + 5º ano + frações + BNCC 2018” pode ser um estado de busca, mas não merece automaticamente uma página indexável. Isso evita milhares de páginas duplicadas ou rasas.

### 4.2 Navegação

**Cabeçalho da página inicial**

- símbolo quadrado da marca + nome **Busca Base**, ligados à própria home;
- sem menu global, sem link Sobre no cabeçalho;
- sem entrar, criar conta ou configurações na primeira versão.

**Cabeçalho de páginas de descoberta**

- marca;
- botão primário **Buscar na Base**, levando à home;
- quando possível, o link já carrega o contexto, por exemplo `/?modo=buscar&ano=5&componente=matematica`.

**Rodapé**

- Sobre;
- Privacidade;
- Acessibilidade;
- Índices: habilidades, etapas, anos, áreas, componentes, competências e documentos;
- recorte dos dados;
- atribuição ao `bncc-dados`;
- aviso curto de que o Busca Base não é um site oficial do MEC.

Na home, os índices de descoberta aparecem apenas no rodapé. Nas páginas de descoberta, a volta à busca aparece no início e depois do conteúdo principal.

---

## 5. Página inicial: os quatro modos no mesmo lugar

### 5.1 Estrutura

1. cabeçalho mínimo;
2. título: **Encontre o que você precisa na Base Nacional Comum Curricular**;
3. frase curta: **Busque por código, por filtros ou por tema. Se quiser, também pode perguntar.**
4. área dos modos, nesta ordem:
   - **Pesquisa por código**, sempre expandido no estado inicial;
   - **Pesquisa por filtros**, sempre expandido no estado inicial;
   - **Pesquisa simples**, sempre expandido no estado inicial;
   - **Pesquisa conversacional**, seção retrátil **fechada** no estado inicial;
5. resultados, resposta ou estado de orientação no mesmo fluxo, abaixo do modo usado;
6. aviso de fonte/limite quando necessário;
7. rodapé.

Não há seletor de abas. Os quatro modos existem como seções da mesma página. Não vão para um menu, nem em celular.

### 5.2 Estados da home

**Inicial (sem consulta nesta visita, ou depois de Nova consulta)**

- Pesquisa por código, Pesquisa por filtros e Pesquisa simples ocupam o centro, um abaixo do outro;
- Pesquisa conversacional aparece como cabeçalho retrátil, fechado;
- nenhum campo recebe foco automático;
- os filtros ficam na seção Pesquisa por filtros.

**Depois de executar uma consulta**

- o modo usado permanece no fluxo, com o campo compacto e os resultados abaixo;
- os outros dois modos viram **botões discretos no topo** da área de consulta, na ordem Por código, Buscar, Perguntar;
- o botão do modo ativo não aparece no topo: o próprio formulário compacto o representa;
- um controle **Nova consulta** devolve o estado inicial e limpa resultados visíveis, preservando o texto digitado.

A transição entre estado inicial e estado focado usa animação CSS (altura, opacidade e posição), cerca de 400 ms, com easing simples. Com `prefers-reduced-motion`, a troca é instantânea. A animação explica o reagrupamento; não atrasa o envio da consulta.

Ao trocar de modo pelos botões do topo:

- expandir o modo escolhido e minimizar os outros, com a mesma animação;
- preservar texto e filtros compatíveis;
- restaurar resultados daquele modo se ainda existirem na sessão;
- não iniciar geração de Perguntar só por abrir a seção;
- atualizar a URL com estado compartilhável, sem indexar combinações de consulta.

Pesquisa conversacional aberta manualmente no estado inicial (sem envio) não minimiza os outros modos. A minimização ocorre **somente após uma consulta executada**.

### 5.3 Buscar

- rótulo **O que você quer encontrar na BNCC?**;
- ajuda visível: **Habilidade é o que a Base diz que deve ser aprendido em cada etapa.**;
- exemplos abaixo do campo, como botões: “frações no 5º ano”, “argumentação no Ensino Médio”;
- botão **Buscar**;
- placeholder: `Ex.: frações no 5º ano`.

O placeholder nunca substitui o rótulo. A busca aceita linguagem cotidiana e termos oficiais. Se o texto for um único código válido, o resultado exato aparece primeiro, sem repreender a pessoa por ter usado o modo “errado”.

**Filtros (decidido)**

Visíveis por padrão, na seção Buscar, **abaixo** do campo, dos exemplos e do botão. Cada filtro é um conjunto de opções visíveis, agrupadas quando a etapa ainda não foi escolhida. Não usar `<select multiple>`, não usar coluna lateral e nunca colocar filtros acima da consulta:

| Filtro | Controle | Padrão |
|---|---|---|
| Etapa | opções visíveis; reduz anos, áreas e componentes | nenhum (todas) |
| Ano ou faixa | opções visíveis, agrupadas por etapa até uma etapa ser marcada | nenhum (todos) |
| Componente curricular | opções visíveis, agrupadas por etapa; campo para reduzir a lista se houver mais de 12 | nenhum (todos) |
| Documento | opções visíveis | todos os vigentes |

Atrás de **Mais filtros**:

- área do conhecimento;
- tipo de item: habilidade, objetivo de aprendizagem, competência.

Regras:

- filtros valem para Buscar e, quando aberta, para Perguntar;
- Por código ignora filtros: o código é a chave;
- itens `revogado` ficam de fora do padrão; só entram se a pessoa marcar **Incluir itens revogados** em Mais filtros;
- filtros aplicados viram chips removíveis acima dos resultados;
- **Limpar filtros** aparece só quando houver ao menos um filtro;
- a URL guarda os filtros da consulta atual.

### 5.4 Por código e as sugestões após dois caracteres

**Rótulo:** `Digite o código`  
**Ajuda:** `O código começa com EI, EF ou EM. Exemplo: EF05MA03`

O campo aceita minúsculas, espaços e colagem. A normalização é visível apenas quando útil.

Depois de **dois caracteres alfanuméricos normalizados**, mostrar entre **três e cinco cartões pequenos** imediatamente abaixo do campo. Não são autocomplete e não completam o texto.

Cada cartão é compacto:

> **EF05MA03**  
> Identificar e representar frações…  
> 5º · Matemática

Conteúdo máximo do cartão:

- código completo, em destaque;
- enunciado em **uma linha**, com reticências se necessário;
- **uma linha curta** de contexto: ano ou faixa + componente;
- sem unidade temática, objetos de conhecimento, documento ou página.

Regras:

- cartões em linha que quebra; no celular, até dois por linha;
- altura alvo de 72–88 px;
- ordenar primeiro por prefixo de código e depois por relevância;
- debounce de 150 ms, sem chamada a LLM;
- não abrir sugestões para entrada inválida que ainda possa ser corrigida;
- destacar o código pela tipografia, não só pela cor;
- nome acessível completo: código, enunciado inteiro, ano e componente;
- Tab e Shift+Tab percorrem os cartões; Enter no campo executa a consulta digitada;
- Escape fecha as sugestões;
- anunciar apenas “4 sugestões de código”, sem recitar a lista a cada tecla;
- clicar no cartão abre o registro, não preenche o campo;
- não usar `role="combobox"`;
- no máximo cinco cartões; se houver mais correspondências, o último controle é **Ver mais códigos**, que executa a consulta pelo prefixo.

Estados após envio:

- **formato inválido:** explicar como reconhecer um código e oferecer Buscar;
- **formato válido, código inexistente:** explicar que a numeração oficial pode ter lacunas e oferecer códigos próximos;
- **encontrado:** mostrar o registro completo e as ações de reutilização.

### 5.5 Perguntar

No estado inicial, só o cabeçalho retrátil. Ao expandir, o modo começa orientado, não com uma tela de chat vazia.

Mostrar:

- rótulo **O que você quer entender ou comparar?**;
- aviso permanente: **As respostas usam trechos da Base e mostram as fontes. A BNCC não é um plano de aula.**;
- exemplos: “Explique EF05MA03 em palavras mais simples”, “Compare frações no 5º e no 6º ano”;
- os mesmos filtros visíveis de Buscar, se já estiverem aplicados; senão, o mesmo bloco compacto de etapa, ano e componente;
- botão **Perguntar**.

A conversa pode:

- explicar um item;
- comparar códigos;
- localizar diferenças entre anos;
- organizar um percurso entre itens recuperados, com aviso de que a ordem não é oficial;
- manter filtros durante os turnos;
- recusar metodologia ou informação que a BNCC não contém.

Não deve:

- apresentar a ferramenta como pessoa;
- usar “pensando” ou revelar cadeia de raciocínio;
- gerar código sem validar nos dados;
- esconder o trecho oficial atrás da resposta;
- iniciar uma nova geração quando a pessoa apenas abre uma fonte ou expande a seção.

---

## 6. Resultados e reutilização

### 6.1 Cartão de resultado

A ordem de informação é:

1. código ou identificador;
2. tipo de item;
3. texto oficial;
4. etapa, ano/faixa, área e componente;
5. unidade/campo e objetos de conhecimento, quando existirem;
6. fonte oficial, página e vigência;
7. ações;
8. link permanente no domínio Busca Base.

O texto oficial deve ser distinguido de resumos e explicações geradas. Não usar aspas decorativas para trechos longos; usar rótulo explícito **Texto da BNCC**.

### 6.2 Ações

As ações principais têm texto, não apenas ícones:

- **Copiar texto**;
- **Copiar texto e referência**;
- **Compartilhar**;
- **Baixar**;
- **Perguntar sobre este item**, quando Perguntar estiver disponível.

Comportamento:

- copiar oferece confirmação curta e não rouba foco;
- “texto e referência” inclui o texto oficial, código, contexto, URL, documento e recorte;
- compartilhar usa Web Share API quando disponível e copia o link como alternativa;
- baixar um item oferece `.txt` legível;
- impressão usa a folha de estilo de impressão do site; não há geração de PDF nem `.docx` na primeira versão;
- uma seleção com vários itens baixa `.txt` e `.csv`;
- conversa oferece **Copiar resposta**, **Copiar resposta e fontes** e `.txt` — não CSV;
- perguntar sobre um item troca para Perguntar, preserva o código e prepara uma pergunta editável, sem iniciar geração automaticamente;
- exportações são geradas no servidor e repetem a versão dos dados.

CSV da seleção: `codigo`, `tipo`, `texto`, `etapa`, `anos`, `componente`, `unidade_ou_campo`, `documento`, `fonte`, `url`, `recorte`.

Em celular, as ações quebram em duas linhas. Primeira linha: **Copiar texto** e **Copiar texto e referência**. Segunda: **Compartilhar**, **Baixar .txt** e **Perguntar sobre este item**. Não usar menu de três pontos nem rolagem horizontal.

### 6.3 Seleção de vários resultados

Para planejamento:

- checkbox à esquerda do código, rótulo acessível `Selecionar EF05MA03`;
- cartão selecionado ganha borda primária e o checkbox marcado — não só um fundo;
- limite de **50** itens; ao tentar o 51º, avisar e não marcar;
- seleção vale para o conjunto atual de resultados e sobrevive a **Mostrar mais**;
- troca de modo ou **Nova consulta** limpa a seleção;
- depois do primeiro item, uma barra de ações:
  - no celular, fixa no rodapé com padding extra no conteúdo para não cobrir foco;
  - no desktop, fixa abaixo do campo compacto, acima da lista — não sobrepõe cartões;
- a barra traz contador textual, **Copiar texto e referência**, **Baixar .txt**, **Baixar .csv** e **Limpar seleção**;
- remover um item ou limpar tudo não pede confirmação.

### 6.4 Fontes na conversa

Cada afirmação curricular relevante deve apontar para uma fonte numerada. Ao tocar na fonte:

- revelar o trecho oficial na mesma página;
- mostrar código e contexto;
- oferecer o permalink;
- não mandar a pessoa ao `bncc.dev`;
- manter a resposta visível para comparação.

---

## 7. Espera, streaming e indisponibilidade do LLM

### 7.1 Princípios

- responder imediatamente à ação, mesmo quando o conteúdo demora;
- mostrar trabalho compreensível, sem percentuais inventados;
- preservar a pergunta e os filtros;
- permitir cancelar;
- separar espera na fila de geração em andamento;
- oferecer Buscar como alternativa, nunca como erro do usuário.

### 7.2 Sequência de estados

1. **Até 300 ms:** manter o botão pressionado/desabilitado e reservar espaço; evitar um flash de spinner.
2. **Busca de fontes:** `Procurando trechos na Base…`
3. **Validação:** `Conferindo códigos e fontes…`
4. **Fila, quando houver:** `Há outras perguntas na fila. A sua será respondida em seguida.` Mostrar posição ou estimativa apenas se forem confiáveis.
5. **Primeiro texto:** iniciar streaming e trocar o status por `Resposta em andamento`.
6. **Fim:** mover foco somente se a ação da pessoa indicar isso; anunciar a conclusão em região viva discreta.

Um indicador visual deve ser acompanhado por texto. Skeleton é aceitável para cartões previsíveis, mas não para fingir o tamanho de uma resposta desconhecida.

### 7.3 Controles durante a espera

- **Cancelar pergunta**;
- **Ver trechos encontrados**, assim que a recuperação terminar;
- **Fazer uma busca em vez disso**, reaproveitando texto e filtros;
- campo bloqueado somente durante o envio; depois, permitir preparar a próxima mensagem sem dispará-la.

### 7.4 Falhas

| Situação | Resposta da interface |
|---|---|
| Pesquisa conversacional temporariamente desativada | Modo visível e indisponível com motivo curto; os outros três modos ativos |
| Limite por sessão/IP | Informar quando pode tentar de novo; oferecer Buscar |
| Conexão interrompida durante streaming | Manter o trecho recebido, marcar como incompleto e oferecer continuar/tentar novamente |
| Nenhuma fonte suficiente | Dizer que não foi encontrado suporte na Base; mostrar consultas alternativas |
| Erro interno | Preservar a pergunta; gerar identificador de suporte sem expor detalhes técnicos |

Nunca substituir silenciosamente o modelo local por uma API externa.

---

## 8. Estados de orientação

### Vazio inicial

Mostrar exemplos diferentes por modo. Exemplos são botões de preenchimento, não carrossel. Em Buscar, a ajuda sobre o que é habilidade permanece visível.

### Nenhum resultado

Ordem:

1. dizer o que foi buscado;
2. mostrar filtros que podem ter restringido;
3. oferecer **Remover filtros**;
4. sugerir termos próximos ou grafia;
5. oferecer Perguntar somente se estiver disponível e fizer sentido.

### Muitos resultados

- mostrar primeiro os mais relevantes;
- explicar filtros em linguagem comum;
- não paginar antes de a pessoa ver um primeiro conjunto útil;
- usar **Mostrar mais** com URL/estado preservado;
- nunca rolagem infinita sem alternativa.

### Offline ou conexão instável

- informar que a consulta precisa de conexão;
- preservar campos;
- permitir nova tentativa;
- páginas já carregadas continuam legíveis;
- não prometer modo offline completo na primeira versão.

---

## 9. Descoberta, SEO e busca por IA

### 9.1 Princípio

Descoberta não justifica conteúdo artificial. Cada página indexável precisa responder a uma intenção real, apresentar informação visível e ter valor sem executar JavaScript.

### 9.2 Templates indexáveis

**Habilidade/aprendizagem**

- H1 com código e resumo fiel;
- texto oficial integral;
- contexto hierárquico;
- objetos de conhecimento;
- fonte, vigência e recorte;
- itens relacionados por relações existentes nos dados, não por texto inventado;
- CTA no topo: **Buscar esta habilidade na Base**;
- CTA após o conteúdo: **Fazer outra busca**.

**Ano/faixa**

- explicação curta do recorte;
- etapas e componentes presentes;
- agrupamentos úteis;
- lista paginável ou seções de itens;
- link para abrir a home com o filtro aplicado.

**Etapa, área, componente, competência e documento**

- definição factual;
- posição na estrutura;
- itens que pertencem ao recorte;
- links para dimensões adjacentes;
- data e versão.

### 9.3 Metadados

Toda página deve ter:

- `<html lang="pt-BR">`;
- `<title>` único e descritivo;
- meta description fiel ao conteúdo;
- URL canônica absoluta em `https://www.buscabase.com.br`;
- Open Graph básico;
- `robots` coerente;
- data de atualização quando ela for real;
- uma única H1;
- breadcrumbs visíveis nas páginas de descoberta.

Fórmulas iniciais:

- habilidade: `EF05MA03: habilidade de Matemática do 5º ano | Busca Base`;
- ano: `Habilidades da BNCC para o 5º ano | Busca Base`;
- componente: `Matemática na BNCC: habilidades e anos | Busca Base`;
- competência: `[Nome da competência] na BNCC | Busca Base`.

Descriptions não devem ser apenas o mesmo texto cortado em todas as páginas. Para habilidades, podem combinar código, contexto e o início do enunciado oficial.

### 9.4 Dados estruturados

Usar JSON-LD somente quando corresponder ao conteúdo visível:

- `WebSite` e `Organization` na home/sobre;
- `WebPage` nas páginas;
- `BreadcrumbList` onde houver breadcrumbs;
- `DefinedTerm` para códigos e conceitos quando a modelagem for adequada;
- `Dataset` na página que descreve o conjunto de dados, não em cada resultado.

Não adicionar `FAQPage`, avaliações ou marcações educacionais sem conteúdo equivalente e sem suporte documentado. Dados estruturados ajudam máquinas a entender a página, mas não garantem destaque.

### 9.5 URLs, parâmetros e canonicals

- slugs em minúsculas, sem acentos e com hífens;
- códigos em maiúsculas na interface; a URL aceita variação e redireciona para uma forma canônica;
- buscas e conversas ficam em `/` com parâmetros compartilháveis;
- parâmetros de consulta e combinações de filtros usam canonical para `/` e `noindex` quando gerarem uma página;
- nenhuma sessão, mensagem pessoal ou consulta fica no sitemap;
- páginas removidas por mudança de vigência continuam explicando o estado ou redirecionam somente quando houver equivalente real.

### 9.6 Sitemap

Gerar sitemap a partir do mesmo snapshot validado usado na aplicação. Mesmo abaixo do limite de 50 mil URLs, separar por tipo facilita monitoramento:

- `/sitemap.xml` — índice;
- `/sitemaps/paginas.xml`;
- `/sitemaps/habilidades.xml`;
- `/sitemaps/competencias.xml`;
- `/sitemaps/estrutura.xml`.

Incluir apenas URLs canônicas, indexáveis e retornando `200`. `lastmod` muda somente quando o registro ou o template visível mudar. O build falha se um código indexado não gerar página.

### 9.7 Otimização para respostas de IA

O que ajuda:

- HTML renderizado no servidor ou pré-renderizado;
- trechos curtos e factuais antes de explicações;
- títulos descritivos;
- códigos e relações em texto, não apenas em elementos visuais;
- fontes, versão e datas explícitas;
- permalinks estáveis;
- JSON-LD coerente;
- sitemap e links internos;
- política clara no `robots.txt`;
- páginas `.md` ou representação textual somente se houver uma necessidade comprovada e canonical para o HTML.

Publicar `/llms.txt` apontando para Sobre, recorte dos dados, coleções principais e a regra de que a consulta acontece em `/`. Ele não substitui HTML, sitemap ou links internos e não é tratado como garantia de indexação.

### 9.8 Evitar

- páginas de todas as combinações possíveis;
- texto “SEO” gerado por LLM;
- títulos que prometem plano de aula quando a página só contém uma habilidade;
- esconder links no rodapé por CSS ou gerar blocos enormes de links;
- duplicar o texto de uma habilidade em URLs concorrentes;
- indexar resultados de busca internos;
- afirmar que o Busca Base é a fonte oficial.

---

## 10. Acessibilidade

Meta: **WCAG 2.2 nível AA**, com eMAG e o padrão de acessibilidade do Governo Digital como referências brasileiras.

Requisitos de base:

- HTML semântico antes de ARIA;
- navegação completa por teclado;
- link **Pular para o conteúdo**;
- títulos de página únicos para anúncio de rota;
- ordem de foco igual à ordem visual;
- foco sempre visível e nunca encoberto;
- regiões vivas apenas para status importante;
- mensagens de erro ligadas ao campo;
- rótulos persistentes;
- contraste AA e informação nunca transmitida só por cor;
- zoom a 200% sem perda e reflow a 320 CSS px;
- alvos de toque de 44 × 44 CSS px como meta interna;
- respeito a `prefers-reduced-motion`;
- leitura útil com CSS ou JavaScript indisponível nas páginas públicas;
- códigos pronunciáveis por leitor de tela por meio de texto acessível quando necessário;
- teste com TalkBack no Android, NVDA/Firefox, VoiceOver/Safari e somente teclado.

As sugestões de código, a transição entre estado inicial e focado, filtros, seleção múltipla, notificações de cópia e streaming precisam de testes manuais; um scanner não valida o fluxo. Códigos são anunciados como estão escritos, precedidos do tipo (`Habilidade EF05MA03`); não soletrar letra a letra.

---

## 11. Desempenho e resiliência

### 11.1 Metas de campo

No 75º percentil móvel:

- LCP ≤ 2,5 s;
- INP ≤ 200 ms;
- CLS ≤ 0,1.

Metas internas mais úteis que uma nota isolada:

- HTML útil na primeira resposta;
- home utilizável antes de carregar recursos não essenciais;
- JavaScript inicial da home ≤ 75 kB comprimidos;
- CSS crítico ≤ 20 kB comprimidos;
- nenhuma fonte web na primeira versão;
- nenhuma imagem heroica;
- ícones locais em SVG;
- nenhuma dependência de terceiros bloqueando renderização;
- resultado de Por código percebido em menos de 500 ms no Brasil quando o dado estiver em cache;
- busca com estado imediato e orçamento de backend medido separadamente;
- primeira fonte da conversa disponível antes do primeiro token gerado, quando possível.

Os números de bytes são orçamentos iniciais, não garantias. Devem ser medidos no bundle real e revistos apenas com justificativa.

### 11.2 Estratégia

- pré-renderizar páginas de descoberta no build do novo snapshot;
- cache imutável para assets com hash;
- cache de CDN para páginas públicas;
- Brotli/Gzip;
- divisão por rota;
- carregar código da conversa só quando a seção Perguntar for expandida;
- evitar bibliotecas de ícones, datas, animação e componentes quando a plataforma resolve;
- reservar altura para status e resultados para evitar deslocamento;
- limitar preloads; em rede lenta, preload indiscriminado compete com a consulta;
- não instalar service worker na primeira versão: dados curriculares desatualizados e cache inconsistente custam mais que o ganho offline.

### 11.3 Medição

- Lighthouse CI como barreira de regressão, não como única verdade;
- Web Vitals reais, anonimizados e separados por tipo de página;
- teste em Android básico e perfil de rede lenta;
- peso por rota no CI;
- tempo de cada etapa: frontend, API, recuperação, rerank, fila, primeiro token e conclusão;
- consultas nunca entram em analytics de terceiros;
- o uso primeiro-partido guarda o texto da consulta, filtros e códigos neste Postgres.

---

## 12. Arquitetura frontend proposta

### 12.1 Responsabilidades

**SvelteKit**

- páginas e componentes;
- SSR e pré-renderização;
- metadados;
- sitemap e `robots.txt`;
- estado de interface e URL;
- proxy/BFF fino para manter API na mesma origem;
- streaming ao navegador;
- fallback de formulários quando aplicável.

**FastAPI**

- normalização e validação de código;
- sugestões por prefixo;
- busca híbrida;
- conversa e citações;
- exportações;
- rate limit e disponibilidade do modo Perguntar;
- acesso a Postgres e às APIs configuráveis de embed, rerank e geração.

O SvelteKit não replica regras da BNCC. Tipos de resposta podem ser compartilhados por OpenAPI gerado pelo FastAPI.

### 12.2 Renderização por grupo

| Grupo | Estratégia |
|---|---|
| Home sem consulta | SSR, com shell pequeno e conteúdo útil |
| Resultado interativo na home | requisição cliente progressiva, estado na URL |
| Sobre, privacidade, acessibilidade | pré-renderizado |
| Habilidades, competências e dimensões | pré-renderizado a cada snapshot |
| Sitemap, `robots.txt`, `/llms.txt` | gerado no build |
| Exportações | stream/arquivo pelo FastAPI |

Se a pré-renderização passar a ser lenta, manter páginas populares estáticas e usar SSR com cache para a cauda. Com cerca de milhares de registros, pré-renderizar tudo ainda é simples.

### 12.3 Estado e URLs

- estado local de cada modo fica no componente da home;
- filtros compartilhados ficam na URL;
- estado inicial não leva `modo` na URL; após consulta, `modo=codigo|buscar|perguntar`;
- conversa completa não vai automaticamente para a URL;
- links compartilhados de conversa exigem ação explícita e política de retenção;
- botão Voltar restaura modo, consulta, filtros, posição, seleção e o estado inicial/focado;
- nenhuma store global para dados que pertencem a uma página.

### 12.4 Componentes iniciais

- `Cabecalho`;
- `AreaDeModos`;
- `ModoCompacto`;
- `SecaoPerguntar`;
- `CampoPorCodigo`;
- `SugestoesDeCodigo`;
- `CampoDeBusca`;
- `FiltrosDaBase`;
- `BotaoNovaConsulta`;
- `CampoDePergunta`;
- `EstadoDeEspera`;
- `CartaoDeAprendizagem`;
- `TrechoFonte`;
- `AcoesDeResultado`;
- `BarraDeSelecao`;
- `Aviso`;
- `PaginacaoOuMostrarMais`;
- `Rodape`.

Nomes de código podem ficar em inglês se esse for o padrão da equipe, mas todo texto renderizado, acessível, metadata e mensagem de erro deve estar em pt-BR.

### 12.5 Dependências

Adotar somente quando houver necessidade:

- SvelteKit/Svelte/TypeScript;
- schema validator leve para contratos da API;
- Playwright;
- Vitest;
- axe-core;
- formatter e linter oficiais.

Não adotar inicialmente:

- Tailwind;
- biblioteca completa de componentes;
- Redux ou equivalente;
- cliente GraphQL;
- framework de RAG no frontend;
- editor rich text;
- pacote de animação JavaScript;
- PWA;
- Storybook antes de existir um conjunto estável de componentes.

---

## 13. Privacidade, confiança e limites

- não exigir conta;
- não pedir nome, escola ou dados de estudante;
- alertar no campo de conversa para não inserir dados pessoais;
- registrar consultas no analytics primeiro-partido (texto, filtros, códigos), sem cookie e sem IP na mesma linha;
- não enviar consultas a analytics de terceiros;
- permitir compartilhar somente por ação;
- deixar claro quando uma resposta foi gerada;
- mostrar o recorte de dados;
- separar texto oficial, resumo do Busca Base e conteúdo gerado;
- não usar selo, brasão ou identidade que sugira chancela pública;
- manter atribuição ao `bncc-dados` no rodapé e em Sobre, não no caminho principal de busca.

---

## 14. Critérios de aceite para a primeira versão

### Fluxos

- na primeira visita, Pesquisa por código, Pesquisa por filtros e Pesquisa simples estão abertos e Pesquisa conversacional está fechada;
- após uma busca, os outros modos viram botões no topo, com animação;
- uma pessoa encontra `EF05MA03` digitando ou escolhendo um cartão após dois caracteres;
- uma busca por “frações no 5º ano” retorna itens relevantes e permite filtrar;
- uma pergunta mostra fontes antes ou junto da resposta;
- Perguntar pode ser desativado sem quebrar os outros modos;
- qualquer resultado pode ser copiado, compartilhado e baixado;
- Voltar não apaga a busca;
- páginas de habilidade levam à home com CTA proeminente;
- índices da home aparecem somente no rodapé.

### Qualidade

- nenhum código exibido por conversa deixa de existir no snapshot;
- texto oficial não é alterado;
- todos os templates têm título, description, canonical e H1 únicos;
- sitemap contém apenas páginas válidas;
- contraste, teclado, reflow, TalkBack e NVDA passam no roteiro manual;
- metas de Core Web Vitals são acompanhadas em campo;
- JavaScript desnecessário não é carregado nas páginas de descoberta;
- nenhum texto de interface está em inglês.

### Pesquisa com pessoas

Antes de estabilizar a navegação, testar ao menos:

- 5 responsáveis com diferentes níveis de letramento digital;
- 5 docentes de etapas/componentes diferentes;
- 3 profissionais de coordenação ou secretaria;
- 3 pessoas que usem tecnologia assistiva ou tenham barreiras motoras/cognitivas relevantes.

Tarefas, sem ensinar o caminho:

1. descobrir o que uma criança do 5º ano aprende sobre frações;
2. abrir um código recebido em um planejamento;
3. comparar dois anos;
4. copiar um resultado com referência;
5. entender por que uma pergunta não pode ser respondida pela BNCC.

Medir conclusão, tempo, erros, confiança e compreensão da diferença entre texto oficial e explicação.

---

## 15. Sequência recomendada de implementação

1. implementar a home nos dois estados (inicial e focado) com a animação;
2. tokens e componentes básicos acessíveis;
3. Por código com sugestões locais;
4. Buscar com filtros, resultados e ações;
5. templates pré-renderizados e sitemap;
6. Perguntar com fontes, fila, cancelamento e falhas;
7. seleção e exportação múltipla;
8. métricas de campo e refinamento com pesquisa.

Não esperar a conversa para testar a interface. O produto precisa ser completo e útil com Pesquisa por código, Pesquisa por filtros e Pesquisa simples.

---

## 16. Decisões desta passagem

- nome: **Busca Base**;
- domínio: `www.buscabase.com.br`;
- idioma: português brasileiro;
- home com Pesquisa por código, Pesquisa por filtros e Pesquisa simples expandidos; Pesquisa conversacional retrátil e fechada;
- ordem visual: Pesquisa por código, Pesquisa por filtros, Pesquisa simples, Pesquisa conversacional;
- após consulta, os outros modos viram botões discretos no topo, com animação CSS de ~400 ms;
- **Nova consulta** restaura o estado inicial;
- sem Sobre no cabeçalho;
- filtros visíveis: etapa, ano/faixa, componente, documento; em Mais filtros: área, tipo, revogados;
- cartões de código pequenos: código + 1 linha de enunciado + ano e componente;
- “habilidade” permanece o termo oficial, com uma linha de explicação em Buscar;
- Perguntar leva aviso permanente de que a BNCC não é plano de aula;
- seleção múltipla por checkbox, limite 50, barra inferior no celular e abaixo do campo no desktop;
- exportar: `.txt` sempre; `.csv` na seleção múltipla; impressão pelo navegador; sem `.docx` e sem PDF gerado na v1;
- `/llms.txt` publicado;
- marca: símbolo quadrado + **Busca Base**; botões dos modos não usados são secundários;
- metadados do cartão de resultado em uma linha (`5º ano · Matemática · Números`); objetos completos na página da habilidade;
- comparação em blocos empilhados no celular, sem tabela larga;
- leitores de tela anunciam `Habilidade EF05MA03` sem soletrar;
- páginas de descoberta levam à home;
- links aos índices somente no rodapé da home;
- frontend em SvelteKit/Svelte/TypeScript;
- CSS próprio, sem fonte web e sem biblioteca visual pesada inicialmente;
- WCAG 2.2 AA;
- páginas estruturais pré-renderizadas;
- sitemap segmentado;
- cópia, compartilhamento e download são requisitos de primeira classe.

Pesquisa com pessoas na implementação mede compreensão e conclusão de tarefas. Não reabre estas decisões de produto, a menos que um teste mostre bloqueio real.

---

## 17. Referências

- [SvelteKit — Project types](https://svelte.dev/docs/kit/project-types)
- [SvelteKit — Page options e prerenderização](https://svelte.dev/docs/kit/page-options)
- [SvelteKit — Performance](https://svelte.dev/docs/kit/performance)
- [SvelteKit — Accessibility](https://svelte.dev/docs/kit/accessibility)
- [SvelteKit — SEO](https://svelte.dev/docs/kit/seo)
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [W3C — Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)
- [Web Vitals](https://web.dev/articles/vitals)
- [Google Search Central — Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Design System do Governo Federal](https://www.gov.br/governodigital/pt-br/estrategias-e-governanca-digital/transformacao-digital/ferramentas/design-system/design-system)
- [Lei nº 15.263/2025 — Política Nacional de Linguagem Simples](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15263.htm)
