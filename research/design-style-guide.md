# Guia de estilo visual do Busca Base

**Status:** direção visual da primeira versão pública  
**Data:** 2026-08-21  
**Escopo:** marca digital, tokens, composição, componentes, estados e acessibilidade visual  
**Documento relacionado:** [ui-ux-frontend.md](./ui-ux-frontend.md) e [ux-writing-style-guide.md](./ux-writing-style-guide.md)

O Busca Base deve parecer uma ferramenta pública confiável, clara e independente. A interface precisa funcionar para uma pessoa especialista em currículo e para alguém que usa um celular básico e não conhece a estrutura da BNCC.

Este guia define direção e regras. Os valores abaixo estão decididos para esta versão. Testes visuais e de acessibilidade na implementação corrigem contraste, tamanho e bugs; não reabrem as escolhas de produto.

---

## 1. Direção visual

### Três atributos

**Clara**  
Poucos elementos disputam atenção. Espaço, alinhamento e tipografia explicam a hierarquia antes de bordas ou cores. As quatro intenções da home — código, filtros, tema e pergunta — ocupam blocos distintos. O campo e o botão da tarefa são o que a pessoa vê primeiro em cada bloco.

**Confiável**  
Informação oficial, explicação e ação têm aparência distinta e previsível. A interface não exagera resultados nem tenta parecer “mágica”. Cantos retos e superfícies estáveis comunicam catálogo, não aplicativo de consumo.

**Próxima**  
Texto legível, controles grandes e exemplos concretos. Próxima não significa infantil, informal demais ou decorativa.

### Princípios desta versão

1. **Cantos retos.** Controles, cartões, campos, avisos e a marca usam raio 0. O círculo fica só no indicador de progresso.
2. **Sem marcador lateral.** Não usar barra vertical à esquerda para estado, citação ou ênfase. Separar com espaço, painel, borda completa ou uma faixa superior.
3. **Seções com ar.** Cada modo, o resultado e o rodapé são grupos visuais. O intervalo entre grupos é maior que o intervalo dentro do grupo.
4. **Espaço em branco vale mais que linha.** Prefira padding e gap a caixas aninhadas. Uma borda existe para delimitar um painel ou um controle, não para desenhar a página.
5. **A interação principal é proeminente.** Em cada modo, o campo e o botão de envio são maiores, mais contrastados e vêm antes de filtros, exemplos e ajuda longa.

### O que evitar

- aparência de painel administrativo;
- estética de chatbot como centro do produto;
- excesso de cartões;
- cantos arredondados, pílulas e “chips” ovalados;
- barra colorida na borda esquerda;
- azul como cor de marca, ação ou link;
- gradientes;
- sombras fortes;
- vidro, transparência ou desfoque decorativo;
- cores nacionais como atalho para credibilidade;
- brasões, selos ou elementos que façam o projeto parecer oficial;
- ilustrações genéricas de educação;
- mascote;
- animações de “IA pensando”;
- texto pequeno para “caber”;
- ícones sem rótulo nas ações principais.

---

## 2. Marca

### 2.1 Nome

A marca é escrita como:

> **Busca Base**

As duas palavras têm o mesmo peso. “Busca” é a ação; “Base” é a referência à BNCC e à ideia de fundamento. Não destacar uma palavra com cor diferente por padrão.

No texto da interface, metadados e leitores de tela, manter o espaço. O desenho do logotipo pode unir as palavras; isso não altera a grafia oficial.

### 2.2 Assinatura

A assinatura combina o **símbolo quadrado** (arquivo da marca) e o nome **Busca Base** ao lado, em peso 700.

Regras:

- o símbolo é o PNG da marca (três cubos isométricos e uma lupa), em quadrado, sem recorte redondo;
- o arquivo tem fundo transparente; no cabeçalho os cubos assentam no papel da página;
- altura visível no cabeçalho: 48 px (área clicável mínima de 44 px no conjunto);
- `width` e `height` reservados para evitar deslocamento;
- a imagem tem alternativa vazia quando o nome aparece em texto ao lado;
- o link inteiro se chama `Busca Base`;
- o favicon é o mesmo símbolo (cubos + lupa), em SVG e PNG 32 px, testado a 16 px; o ícone da Apple usa o símbolo sobre papel `#F6F1E7`. Não usar monograma BB.

Não usar o logotipo como imagem heroica acima do H1. A home começa pela tarefa. A marca vive no cabeçalho.

### 2.3 Símbolo

O símbolo mostra uma lupa sobre uma estrutura de cubos. Lê-se: encontrar um item preciso dentro da Base.

Não substituir por livro aberto, lâmpada, cérebro, robô, bandeira ou balão de conversa.

### 2.4 Independência institucional

O Busca Base pode aprender com o Design System do Governo Federal, mas não deve copiar cabeçalho, assinatura, cores ou componentes de modo que pareça um serviço oficial. O aviso de independência deve aparecer no rodapé e em Sobre:

> O Busca Base é um projeto independente e não é um site oficial do MEC.

---

## 3. Cor

A paleta sai da marca: verde da palavra e do cubo, dourado do cubo encontrado, azul só no cubo de cima do símbolo. Não há azul de interface (links, botões ou fundos).

### 3.1 Paleta

| Token | Valor | Uso | Contraste |
|---|---:|---|---|
| `--color-text` | `#1A2118` | texto principal | 16,2:1 sobre superfície |
| `--color-text-muted` | `#545247` | texto secundário | 7,7:1 sobre superfície |
| `--color-primary` | `#185C37` | ação primária e links | 8,00:1 sobre branco; 7,11:1 sobre papel |
| `--color-primary-hover` | `#0F5132` | hover/pressed | 9,36:1 sobre branco |
| `--color-focus` | `#9A3412` | anel de foco em superfície clara | 7,19:1 sobre superfície |
| `--color-focus-on-dark` | `#E8B830` | foco sobre preto ou verde escuro | 10,7:1 sobre `#0A0A0A` |
| `--color-background` | `#F6F1E7` | fundo da página (papel) | — |
| `--color-surface` | `#FFFDF8` | painéis, campos e cartões | — |
| `--color-surface-subtle` | `#EBE4D6` | agrupamento interno e rodapé | — |
| `--color-border` | `#C9C1B0` | limites de painel e divisão | estrutural |
| `--color-border-strong` | `#8A8374` | campos e controles | 3,70:1 sobre superfície |
| `--color-success` | `#166534` | estado positivo | 7,13:1 sobre branco |
| `--color-warning` | `#92400E` | atenção | 7,00:1 sobre branco |
| `--color-error` | `#B42318` | erro | 5,9:1 sobre branco |
| `--color-accent` | `#E8B830` | destaque pontual, nunca texto sobre papel | |
| `--color-on-primary` | `#FFFFFF` | texto em botão primário | 8,00:1 sobre primário |
| `--color-brand` | `#0A0A0A` | texto da marca no cabeçalho | — |

Os contrastes foram calculados em sRGB. Toda combinação real, incluindo hover, disabled, bordas e componentes sobre superfícies coloridas, precisa de teste automatizado e visual.

### 3.2 Uso

- verde-floresta indica ação e navegação;
- dourado marca o cubo encontrado e um destaque raro — nunca parágrafo sobre papel, nunca o favicon sozinho;
- terracota do foco é parente do dourado e não compete com o verde;
- verde, ocre e vermelho de estado só acompanham texto;
- texto principal é quase preto com leve oliva, não azul-marinho;
- não colorir áreas, componentes e anos com uma paleta arco-íris;
- links em texto corrido são verdes e sublinhados;
- `hover` não pode ser a única indicação de clique;
- o papel (`--color-background`) separa a página dos painéis brancos; não pintar a tela inteira de branco.

### 3.3 Contraste

Meta mínima:

- texto normal: 4,5:1;
- texto grande: 3:1;
- limites e estados importantes de controles: 3:1;
- foco: visível em qualquer superfície;
- texto secundário não usa cinza abaixo do contraste AA.

`--color-border` delimita painéis e não é o único sinal de um campo. Campos usam `--color-border-strong`, rótulo, espaçamento e estado.

### 3.4 Modo escuro

Não lançar modo escuro nesta versão. Uma paleta clara bem testada é preferível a duas experiências incompletas. Implementar tokens sem acoplar cores diretamente aos componentes para permitir avaliação futura.

---

## 4. Tipografia

### 4.1 Família

Usar a pilha do sistema:

```css
font-family:
  system-ui,
  -apple-system,
  BlinkMacSystemFont,
  "Segoe UI",
  Roboto,
  Arial,
  sans-serif;
```

Razões:

- nenhum download de fonte;
- leitura familiar no aparelho da pessoa;
- melhor desempenho em conexão lenta;
- suporte amplo a acentos e símbolos;
- menor risco de texto invisível ou troca de fonte.

Códigos podem usar a fonte monoespaçada do sistema, mas não devem parecer blocos de programação:

```css
font-family: ui-monospace, "SFMono-Regular", Consolas, monospace;
```

### 4.2 Escala

| Token | Tamanho | Altura de linha | Peso | Uso |
|---|---:|---:|---:|---|
| `--text-xs` | 12 px | 16 px | 400/600 | metadado raro, nunca conteúdo essencial |
| `--text-sm` | 14 px | 20 px | 400/600 | contexto e ajuda |
| `--text-base` | 16 px | 24 px | 400 | corpo e controles |
| `--text-lg` | 18 px | 28 px | 400/600 | introduções e título de resultado |
| `--text-xl` | 20 px | 28 px | 600 | H3 |
| `--text-2xl` | 24 px | 32 px | 700 | H2 |
| `--text-3xl` | 32 px | 40 px | 700 | H1 em celular |
| `--text-4xl` | 40 px | 48 px | 700 | H1 em tela ampla, quando houver espaço |

Usar `rem` em código. O corpo permanece equivalente a 16 px com configuração padrão e respeita preferências do navegador.

### 4.3 Regras

- corpo alinhado à esquerda;
- não justificar;
- largura de leitura entre 60 e 75 caracteres;
- parágrafo com altura de linha de 1,5 ou maior;
- código com espaçamento discreto entre caracteres somente se melhorar reconhecimento;
- caixa alta restrita aos códigos oficiais;
- no máximo pesos 400, 600 e 700;
- sublinhado não é decoração: identifica links;
- títulos não pulam níveis;
- texto oficial pode ser 18 px em páginas de detalhe.

---

## 5. Espaçamento, tamanho e forma

### 5.1 Escala de 4 px

| Token | Valor |
|---|---:|
| `--space-1` | 4 px |
| `--space-2` | 8 px |
| `--space-3` | 12 px |
| `--space-4` | 16 px |
| `--space-5` | 20 px |
| `--space-6` | 24 px |
| `--space-8` | 32 px |
| `--space-10` | 40 px |
| `--space-12` | 48 px |
| `--space-16` | 64 px |

Use espaço para criar grupos. O intervalo **entre** seções da home é `--space-10` (40 px) ou maior. O intervalo **dentro** de um painel é `--space-4` a `--space-6`.

Não coloque uma borda em volta de tudo. Se dois blocos precisam parecer separados, aumente o gap antes de adicionar uma linha.

### 5.2 Raios

Todos os raios de recipiente são **0**.

| Token | Valor | Uso |
|---|---:|---|
| `--radius-sm` | 0 | (legado; não arredondar) |
| `--radius-md` | 0 | campos e botões |
| `--radius-lg` | 0 | cartões, painéis e avisos |
| `--radius` | 0 | valor canônico |

Exceção: o indicador de progresso pode ser circular, porque descreve um processo, não um recipiente.

Filtros aplicados e exemplos são retângulos, nunca pílulas.

### 5.3 Bordas e elevação

- borda de painel: 1 px `--color-border`;
- borda de campo e botão secundário: 1 px `--color-border-strong`;
- borda ativa de cartão selecionado: 2 px primária, sem alterar o tamanho externo;
- aviso e explicação gerada: borda completa + faixa **superior** de 4 px na cor de estado, nunca barra esquerda;
- sem sombra em elementos comuns;
- barra de seleção usa borda superior de 1 px, sem sombra;
- modais não são padrão para tarefas principais.

---

## 6. Layout

### 6.1 Contêineres

- largura máxima geral: 1120 px;
- coluna de leitura: 720 px;
- padding lateral: 16 px no celular, 24 px em telas médias, 32 px em telas amplas;
- conteúdo centralizado;
- página continua útil a partir de 320 CSS px;
- não criar breakpoint por aparelho específico;
- o `main` tem padding superior de 32 px e inferior de 64 px.

### 6.2 Grade

Usar fluxo de uma coluna como base. Uma grade de 12 colunas pode organizar telas amplas, mas não deve aparecer visualmente.

Na home:

- cada modo vive num **painel** (`--color-surface` sobre o papel), com padding interno de 32 px (24 px no compacto);
- os painéis não se encostam: o agrupador da home usa gap de 40 px;
- filtros ficam **dentro** da seção Buscar, **abaixo** do campo, do exemplo e do botão — nunca em coluna lateral e nunca acima da interação principal;
- conversa não usa duas colunas estreitas;
- ações acompanham o conteúdo.

### 6.3 Densidade

- primeira visita: baixa densidade, intro curta e painéis folgados;
- resultado: densidade média, com texto oficial em destaque, lista abaixo do painel ativo (não dentro dele);
- uso especialista: mais informação pode ser revelada, sem reduzir tamanho de fonte;
- metadados longos usam grupos e quebra de linha, não uma única linha horizontal.

### 6.4 Responsividade

Celular é o ponto de partida:

- controles em largura total quando isso ajuda o toque;
- campo principal + botão: empilhados no celular; lado a lado a partir de 48 rem, com o botão alinhado à base do campo;
- no estado inicial, Pesquisa por código, Pesquisa por filtros e Pesquisa simples ocupam a largura em painéis completos; Pesquisa conversacional é um painel retrátil fechado, com o cabeçalho ocupando o painel inteiro;
- no estado focado, os modos não usados são botões secundários no topo, em uma linha que quebra, com espaço abaixo antes do painel ativo;
- ações principais quebram em duas linhas; sem rolagem horizontal;
- cartões não usam colunas, exceto as sugestões de código (até dois por linha no celular);
- tabelas de comparação não existem: cada item vira um bloco empilhado, com o critério como título;
- barras fixas não cobrem conteúdo ou foco;
- teclado virtual não esconde o campo ou o botão de envio.

---

## 7. Iconografia

- SVG local, salvo o PNG da marca;
- traço simples, consistente, entre 20 e 24 px;
- ícone decorativo usa `aria-hidden`;
- ação principal inclui texto;
- ícone não substitui código, rótulo ou estado;
- evitar biblioteca que carregue centenas de ícones;
- usar símbolos conhecidos: copiar, compartilhar, baixar, filtrar, fechar;
- não usar brilho/estrela para representar IA;
- não usar robô em Perguntar.

Ícone sozinho é aceitável apenas em controles universais com nome acessível e espaço restrito, como fechar um painel. Ainda exige alvo de 44 px.

---

## 8. Movimento

### Valores

- transição curta: 120 ms;
- transição padrão: 180 ms;
- transição de modo (inicial ↔ focado): 400 ms;
- easing: `ease-out`; sem mola ou rebote.

### Usos permitidos

- mudança de hover/foco;
- expansão e recolhimento dos modos;
- expansão de Mais filtros e de Perguntar;
- entrada discreta de aviso;
- progresso indeterminado;
- realce breve de item copiado.

### Regras

- respeitar `prefers-reduced-motion`;
- não animar texto durante leitura;
- não deslocar layout ao carregar;
- streaming acrescenta texto sem efeito de máquina de escrever;
- skeleton não pulsa para sempre;
- nenhuma animação bloqueia interação;
- carregamento precisa de rótulo textual.

---

## 9. Componentes

### 9.1 Botões

**Primário**

- fundo `--color-primary`;
- texto branco;
- cantos retos;
- uma ação principal por região;
- hover `--color-primary-hover`;
- altura mínima 44 px; o botão ao lado do campo principal tem a mesma altura do input (56 px).

**Secundário**

- fundo da superfície;
- texto primário e borda `--color-border-strong`;
- ação alternativa clara.

**Terciário**

- aparência de texto, com área de toque completa;
- usado para ações de menor prioridade.

**Perigoso**

- somente para ação destrutiva real;
- não usar vermelho para “Cancelar pergunta”, porque cancelar é seguro e reversível.

Estados:

- hover;
- focus;
- pressed;
- loading com rótulo preservado;
- disabled com motivo próximo quando não for evidente.

Não usar apenas opacidade baixa para disabled; manter leitura e remover ambiguidade.

### 9.2 Links

- verde-floresta;
- sublinhado em texto corrido;
- foco explícito;
- links de navegação podem remover sublinhado apenas se forma e posição indicarem a função;
- links externos não precisam de ícone em toda ocorrência; informar quando o destino/efeito puder surpreender.

### 9.3 Campos

- rótulo acima;
- ajuda abaixo do rótulo e acima do controle;
- altura mínima 48 px; **campo principal** de Por código, Buscar e Perguntar: 56 px;
- padding horizontal 12–16 px;
- borda `--color-border-strong`;
- fundo `--color-surface`;
- foco com anel externo terracota;
- erro com texto, ícone e `aria-describedby`;
- valor nunca depende do placeholder;
- botão interno só quando sua função for clara e tiver alvo adequado.

Em tela ampla, o botão de envio fica à direita do campo, alinhado à base. Em celular, o botão fica abaixo, em largura total.

### 9.4 Modos na home

Quatro seções, nesta ordem: **Pesquisa por código**, **Pesquisa por filtros**, **Pesquisa simples**, **Pesquisa conversacional**. Cada uma é um painel.

**Estado inicial**

- Pesquisa por código, Pesquisa por filtros e Pesquisa simples são painéis completos, com título, campo proeminente, ajuda e botão;
- exemplos de Buscar e de Perguntar são retângulos discretos, abaixo do campo, sem competir com o botão primário;
- filtros de Buscar vêm depois do botão, num recuo `--color-surface-subtle` dentro do mesmo painel;
- Perguntar é um painel fechado cujo cabeçalho é o controle (`<button>` com `aria-expanded`), alvo de 44 px, ocupando a largura do painel;
- nenhum bloco usa fundo primário sólido; o destaque vem do campo grande e do botão.

**Estado focado (após consulta)**

- os modos não usados viram botões secundários no topo;
- o modo ativo fica num painel compacto: título + campo + botão;
- resultados, avisos e conversa ficam **abaixo** do painel, com o mesmo gap da home;
- **Nova consulta** é botão terciário, alinhado à direita do topo.

**Animação**

- animar altura, opacidade e `translateY` curto (8 px);
- 400 ms, `ease-out`;
- com `prefers-reduced-motion: reduce`, troca instantânea sem deslocamento;
- não usar JavaScript de animação.

**Semântica**

- não usar abas;
- os botões do topo são `button` com nome do modo;
- o painel ativo tem `aria-labelledby` no título do modo;
- abrir Perguntar no estado inicial usa `aria-expanded`.

### 9.5 Sugestões de código

Cartões pequenos em linha que quebra, 3 a 5 itens:

- largura mínima 148 px; no celular, até dois por linha;
- altura 72–88 px;
- padding 8–12 px;
- raio 0;
- código em monoespaçada, peso 700, uma linha;
- enunciado em `--text-sm`, **uma linha**, com reticências;
- contexto em `--text-xs` ou 14 px no mínimo: `5º · Matemática`;
- borda neutra, fundo da superfície;
- hover e foco claros.

Não usar:

- lista flutuante sobre conteúdo como autocomplete;
- tooltip para o enunciado;
- rolagem horizontal;
- terceira linha de contexto;
- formato de pílula.

### 9.6 Filtros

O bloco se chama **Filtros da Base**. A palavra “filtro” está no título; não use ícone de funil.

Hierarquia visível, de cima para baixo:

1. **Etapa** — reduz anos, áreas e componentes;
2. **Ano ou faixa** e **Componente curricular** — aninhados num recuo com o rótulo `Definidos pela etapa`;
3. **Documento** — eixo independente;
4. **Mais filtros:** área (também depende da etapa), tipo de item, itens revogados.

Todas as opções cabem na página como retângulos de seleção (checkbox com aparência de botão). Não usar `<select multiple>`. Anos, componentes e áreas sem etapa escolhida aparecem **agrupados pela etapa**, para não repetir “Matemática” sem contexto. Com uma etapa marcada, o agrupamento some. Se a lista de componentes passar de 12, mostre o campo **Reduzir lista de componentes**.

Estado marcado: borda primária de 2 px e peso 600 — nunca só cor de fundo. Foco no anel da face.

**Filtros aplicados**

- lista no topo do bloco, acima das opções;
- cada um é um botão retangular com o valor e a palavra **Remover**;
- nome acessível `Remover filtro 5º ano`;
- nomes ambíguos levam a etapa: `Matemática · Ensino Médio`;
- contador `2 filtros aplicados`;
- **Limpar filtros** só quando houver ao menos um;
- depois da consulta, as opções recolhem atrás de **Alterar filtros**; os aplicados continuam visíveis.

### 9.7 Cartão de resultado

Estrutura:

1. código e tipo;
2. texto oficial;
3. contexto;
4. fonte;
5. ações.

Visual:

- borda completa, cantos retos, sem sombra;
- padding de 20–24 px;
- espaço de 16 px entre grupos;
- código como âncora visual;
- texto oficial maior que metadados;
- metadados em **uma linha**: `5º ano · Matemática · Números`;
- objetos de conhecimento e página do PDF em texto menor abaixo, sem segunda grade;
- ações em duas linhas no celular, na ordem definida no guia de UI;
- `Perguntar sobre este item` aparece como ação secundária e prepara o contexto sem enviar uma pergunta;
- toda a área não é clicável se houver seleção/cópia dentro.

Resultado não é um mosaico. Usar lista vertical para preservar leitura e comparação. A lista não entra no painel do modo: fica no fluxo da página, depois de um intervalo.

### 9.8 Fonte/citação

- caixa discreta ou seção aberta, com borda completa;
- número da fonte junto do código;
- texto oficial legível;
- contexto;
- link permanente;
- expandir sem modal;
- foco vai ao trecho quando a pessoa abre uma citação.

### 9.9 Avisos

Tipos: informativo, sucesso, atenção e erro.

Todos têm:

- título opcional e específico;
- texto;
- significado redundante no texto (não só na cor);
- ação quando houver;
- cor de estado na **faixa superior** e no título, nunca como fundo saturado amplo e nunca como barra esquerda.

Sucesso curto de cópia usa notificação não bloqueante. Erros de formulário ficam junto do campo; não dependem de toast.

### 9.10 Estados de espera

- indicador de progresso de 20–24 px (círculo permitido);
- texto de status;
- espaço reservado;
- fontes recuperadas podem aparecer antes da resposta;
- botão Cancelar visível;
- progresso de fila é distinto de geração.

Evitar bolhas com três pontos, avatar do sistema e skeleton de parágrafo gerado.

### 9.11 Conversa

Não imitar mensageiro:

- pergunta da pessoa em painel discreto (`--color-surface-subtle`);
- resposta como conteúdo da página, com rótulo, aviso e faixa superior neutra — sem barra esquerda;
- fontes imediatamente após afirmações ou seção;
- campo permanece associado ao histórico;
- largura de leitura controlada;
- sem avatar;
- sem nome humano para o sistema;
- ações após cada resposta: copiar, compartilhar, baixar e ver fontes.

### 9.12 Seleção múltipla

- checkbox com rótulo `Selecionar EF05MA03`;
- cartão selecionado ganha borda primária de 2 px e o checkbox marcado, não apenas fundo;
- barra de ações aparece após a primeira seleção;
- no celular, a barra fica fixa no rodapé, com espaço reservado no conteúdo;
- no desktop, a barra fica fixa abaixo do campo compacto, acima da lista;
- contador sempre textual;
- foco nunca fica escondido atrás da barra.

### 9.13 Rodapé

Organização em poucos grupos:

- projeto;
- índices da Base;
- transparência.

Fundo `--color-surface-subtle`, separado da página por espaço, não por uma barra esquerda. Em celular, uma coluna. Links não ficam compactados em texto corrido. O recorte e a independência institucional têm contraste normal, não “letras miúdas”.

### 9.14 Cabeçalho

- fundo do papel, padding vertical de 16–24 px;
- borda inferior de 1 px;
- à esquerda: símbolo 48×48 + **Busca Base**;
- nas páginas internas: botão primário **Buscar na Base**;
- sem menu global.

---

## 10. Páginas de descoberta

Hierarquia recomendada:

1. cabeçalho com marca e **Buscar na Base**;
2. breadcrumbs;
3. H1;
4. resumo factual;
5. texto oficial ou visão do conjunto;
6. contexto e relações;
7. fonte, vigência e recorte;
8. CTA para consulta;
9. links relacionados;
10. rodapé.

O CTA principal deve aparecer acima da dobra sem empurrar o conteúdo. Não usar hero grande. A página precisa ser útil a quem chegou diretamente de um buscador.

Breadcrumbs:

- quebram linha;
- último item não é link;
- nomes completos;
- não reduzem o H1;
- dados estruturados repetem a trilha visível.

---

## 11. Visualização de texto oficial e conteúdo gerado

Os três tipos de conteúdo precisam ser visualmente distinguíveis:

| Tipo | Tratamento |
|---|---|
| Texto oficial | rótulo explícito, maior destaque, fundo da superfície |
| Metadados estruturados | lista ou definição, tipografia secundária |
| Explicação gerada | rótulo `Explicação do Busca Base`, aviso de fontes, faixa superior e padding — sem barra esquerda |

Não usar o verde da marca para fazer uma resposta gerada parecer “correta”. Confiança vem das fontes e da separação semântica.

Trecho oficial não usa aspas gigantes, itálico longo ou fonte serifada decorativa.

---

## 12. Foco e teclado

Em superfície clara:

```css
outline: 3px solid var(--color-focus);
outline-offset: 3px;
```

Em superfície escura, usar anel interno claro e anel externo `--color-focus-on-dark`, ou outra combinação validada com pelo menos 3:1 contra as cores adjacentes.

Regras:

- nunca remover `outline` sem substituição;
- foco não é igual a hover;
- foco não fica coberto por cabeçalho/barra fixa;
- ordem segue leitura;
- pular para conteúdo é o primeiro controle;
- painéis fechados não contêm elementos focáveis;
- ao abrir fonte, mover foco apenas quando isso ajuda a tarefa;
- ao copiar, manter foco no botão;
- ao trocar rota, título e foco seguem o comportamento acessível do SvelteKit.

---

## 13. Alvos e gestos

- meta interna de 44 × 44 CSS px para ações;
- espaço mínimo de 8 px entre alvos pequenos;
- nenhuma ação exige arrastar;
- qualquer gesto tem alternativa por toque;
- hover não revela ação essencial;
- menus de três pontos não concentram as ações centrais;
- seleção, filtros e sugestões funcionam com teclado e toque.

WCAG 2.2 AA exige ao menos 24 × 24 CSS px ou espaçamento equivalente em seu critério mínimo. O Busca Base adota 44 px como alvo de projeto para acomodar baixa precisão motora e uso em movimento.

---

## 14. Conteúdo vazio, erro e indisponibilidade

Estados devem ocupar o local do conteúdo esperado e manter contexto.

**Vazio inicial**

- exemplo de tarefa;
- nenhuma ilustração obrigatória;
- ação direta.

**Sem resultados**

- consulta repetida;
- filtros aplicados;
- próximos passos.

**Erro**

- faixa superior e título;
- consulta preservada;
- botão de nova tentativa.

**Perguntar indisponível**

- a seção permanece visível, fechada e indisponível;
- tratamento inativo com contraste legível;
- mensagem no cabeçalho da seção;
- Pesquisa por código, Pesquisa por filtros e Pesquisa simples continuam disponíveis;
- não exibir uma página de erro.

---

## 15. Imagens, mídia e dados

O produto central não precisa de imagem para a tarefa. A única imagem persistente é a marca no cabeçalho.

Regras da marca:

- PNG local, 302×302, exibido a 48 CSS px (e 96 px em telas 2×);
- dimensões reservadas;
- sem `loading="lazy"` no cabeçalho (está acima da dobra);
- alternativa vazia se o nome estiver ao lado; senão `Busca Base`;
- sem texto essencial que exista só na imagem.

Se houver outras imagens editoriais:

- formato AVIF/WebP com fallback quando necessário;
- dimensões reservadas;
- `loading="lazy"` abaixo da dobra;
- alternativa textual;
- sem foto de banco para preencher espaço.

Gráficos só entram quando respondem a uma pergunta. Tabela ou lista é melhor para poucos valores. Toda visualização precisa de título, unidade, legenda, fonte e alternativa textual.

---

## 16. Tokens técnicos

```css
:root {
  color-scheme: light;

  --color-text: #1a2118;
  --color-text-muted: #545247;
  --color-primary: #185c37;
  --color-primary-hover: #0f5132;
  --color-focus: #9a3412;
  --color-focus-on-dark: #e8b830;
  --color-background: #f6f1e7;
  --color-surface: #fffdf8;
  --color-surface-subtle: #ebe4d6;
  --color-border: #c9c1b0;
  --color-border-strong: #8a8374;
  --color-success: #166534;
  --color-warning: #92400e;
  --color-error: #b42318;
  --color-accent: #e8b830;
  --color-on-primary: #ffffff;
  --color-brand: #0a0a0a;

  --radius: 0;
  --radius-sm: 0;
  --radius-md: 0;
  --radius-lg: 0;

  --content-wide: 70rem;
  --content-reading: 45rem;
}
```

Não expor tokens de valor diretamente em componentes quando um token semântico resolve. Exemplo: `--button-primary-background`, derivado de `--color-primary`, permite evolução sem busca global.

---

## 17. Qualidade e testes

### Automáticos

- contraste de tokens;
- axe-core por template;
- lint de acessibilidade do Svelte;
- snapshots visuais em larguras críticas;
- zoom/reflow;
- tamanho de bundle;
- ausência de texto em inglês na interface, com lista de exceções técnicas;
- estados hover/focus/disabled;
- `prefers-reduced-motion`.

### Manuais

- somente teclado;
- TalkBack em Android;
- NVDA com Firefox;
- VoiceOver com Safari;
- 200% e 400% de zoom;
- 320 CSS px;
- modo de alto contraste/cores forçadas;
- sol forte e brilho reduzido;
- conexão lenta;
- teclado virtual;
- textos longos e códigos inesperados;
- Perguntar em fila, streaming, cancelado e interrompido.

### Revisão de componente

- [ ] Tem uma função única?
- [ ] Usa elemento HTML nativo quando possível?
- [ ] Tem rótulo visível?
- [ ] Tem nome acessível correto?
- [ ] Funciona sem mouse?
- [ ] Foco é visível e não encoberto?
- [ ] Alvo tem 44 px?
- [ ] Estado não depende só de cor?
- [ ] Texto cabe em celular e com zoom?
- [ ] Carregamento preserva tamanho e contexto?
- [ ] Erro aparece onde pode ser corrigido?
- [ ] Não adiciona JavaScript ou dependência desnecessária?

---

## 18. Decisões visuais desta passagem

- símbolo da marca (cubos + lupa) no cabeçalho, com o nome **Busca Base** ao lado; favicon do mesmo símbolo;
- paleta floresta + papel + dourado; nenhum azul de interface;
- cantos retos em toda a superfície; progresso pode ser circular;
- sem barra esquerda em avisos, citações ou respostas geradas;
- seções da home são painéis brancos sobre papel, com gap de 40 px;
- campo + botão de cada modo vêm antes de filtros e exemplos;
- filtros de Buscar abaixo do envio, em recuo interno;
- no estado focado, o modo ativo não usa fundo primário sólido; os botões dos outros modos são secundários;
- ações de resultado quebram em duas linhas no celular;
- metadados do resultado cabem em uma linha, com quebra natural se o espaço acabar;
- cartões de código: 72–88 px, enunciado de uma linha, contexto `ano · componente`;
- barra de seleção: rodapé no celular, abaixo do campo no desktop;
- comparação: blocos empilhados, nunca tabela larga;
- leitores de tela: `Habilidade EF05MA03`, sem soletração letra a letra.

---

## 19. Referências

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [W3C — Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)
- [W3C — Focus Appearance](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance)
- [Design System do Governo Federal](https://www.gov.br/governodigital/pt-br/estrategias-e-governanca-digital/transformacao-digital/ferramentas/design-system/design-system)
- [GOVBR-DS — Acessibilidade](https://govbr-ds.gitlab.io/tools/govbr-ds-wiki/desenvolvimento/acessibilidade/)
- [Web Vitals](https://web.dev/articles/vitals)
