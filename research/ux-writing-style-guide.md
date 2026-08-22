# Guia de escrita para a experiência do Busca Base

**Status:** guia editorial inicial  
**Data:** 2026-08-20  
**Escopo:** todo texto visto ou ouvido por quem usa o produto  
**Idioma:** português brasileiro (`pt-BR`)  
**Documento relacionado:** [ui-ux-frontend.md](./ui-ux-frontend.md)

Este guia orienta interface, resultados, conversa, metadados, exportações, e-mails transacionais futuros e textos acessíveis. O Busca Base deve permitir que pessoas com diferentes níveis de escolaridade encontrem, entendam e usem informações da BNCC sem perder a precisão curricular.

A Política Nacional de Linguagem Simples define uma comunicação em que palavras, estrutura e leiaute ajudam a pessoa a **encontrar, entender e usar** a informação. O Busca Base adota esse princípio como referência de qualidade, embora não se apresente como órgão público.

---

## 1. Personalidade verbal

### Clara

Diz primeiro o que a pessoa precisa saber. Frases curtas, ordem direta e palavras conhecidas.

> **Prefira:** Não encontramos esse código na Base.  
> **Evite:** Não foi possível proceder à localização do identificador informado.

### Precisa

Não troca termos curriculares por sinônimos imprecisos. Explica o termo quando ele for necessário.

> **Prefira:** Esta é uma habilidade de Matemática do 5º ano.  
> **Evite:** Este é um conteúdo de Matemática para crianças de 10 anos.

### Acolhedora

Ajuda sem culpar, mandar ou infantilizar.

> **Prefira:** Tente buscar pelo tema, como “frações no 5º ano”.  
> **Evite:** Digite um código válido.  
> **Evite:** Opa! Parece que você se confundiu.

### Sóbria

O tema é educação pública e o conteúdo é normativo. Evitar entusiasmo artificial, humor em erros e linguagem de marketing.

> **Prefira:** 4 habilidades encontradas.  
> **Evite:** Incrível! Encontramos 4 resultados perfeitos para você!

### Transparente

Distingue texto oficial, organização própria e resposta gerada. Assume limites.

> **Prefira:** A BNCC não traz uma metodologia para essa situação.  
> **Evite:** Com base na BNCC, recomendamos este método…

---

## 2. Regra central: escreva para a tarefa

Antes de publicar qualquer texto, responda:

1. Quem lê isso?
2. O que essa pessoa está tentando fazer?
3. Qual informação permite o próximo passo?
4. O que pode ser removido sem causar dúvida?
5. Um termo da BNCC precisa ser usado? Se sim, foi explicado?

Comece pela conclusão ou ação. Contexto vem depois.

> **Antes:** Para que seja possível realizar uma busca no conjunto de dados da Base Nacional Comum Curricular, é necessário informar algum termo relacionado ao objeto pretendido.  
> **Depois:** Digite um tema, ano ou componente para buscar na BNCC.

---

## 3. Relação com quem usa

- Trate a pessoa por **você** quando o pronome for necessário.
- Prefira verbos diretos sem pronome: **Busque**, **Compare**, **Copie**.
- O produto fala como **Busca Base** ou em primeira pessoa do plural apenas em operações: “Não encontramos”.
- Não dê personalidade humana ao sistema: ele não “pensa”, “lembra”, “fica feliz” ou “entende você”.
- Não chame a pessoa de “usuário” na interface.
- Não presuma profissão, gênero, idade ou relação familiar.
- Não use “leigo”, “iniciante”, “básico” ou “avançado” para classificar pessoas.
- Não use diminutivos para tornar uma instrução “amigável”.

### Linguagem inclusiva

Prefira construções neutras e naturais:

- `quem ensina` em vez de `o professor`;
- `equipe docente` em vez de `os professores`;
- `responsáveis` em vez de `pais`, quando a relação específica não importar;
- `a pessoa` em vez de `o usuário`.

Não usar `x`, `@` ou flexões que prejudiquem leitura e tecnologias assistivas. Quando gênero for relevante, reescreva a frase ou use formas completas com moderação.

---

## 4. Vocabulário fixo do produto

### 4.1 Nome e domínio

- Nome: **Busca Base**
- Endereço: **www.buscabase.com.br**
- Não escrever `BuscaBase`, `Busca base` ou `buscabase` como marca.
- Não abreviar a marca.

### 4.2 Modos

Os nomes na interface são fixos:

| Nome na interface | Use para | Não usar como nome |
|---|---|---|
| **Pesquisa por código** | abrir um código conhecido | Busca exata, Consulta, Lookup, Por código |
| **Pesquisa por filtros** | recortar etapa, ano, campo, área, componente ou documento | Filtros avançados |
| **Pesquisa simples** | encontrar itens por tema | Busca semântica, Pesquisa |
| **Pesquisa conversacional** | explicar, comparar e conversar com fontes | IA, Chatbot, Assistente, Perguntar |

Textos de apoio (subtítulos dos painéis):

- **Pesquisa por código:** `Quando você sabe o código, ou ao menos o começo dele.`
- **Pesquisa por filtros:** `Quando você quer escolher a etapa, o ano, o componente ou o documento.`
- **Pesquisa simples:** `Quando você sabe o que quer achar, mas não o código.`
- **Pesquisa conversacional:** `Quando você quer entender melhor a BNCC interagindo com uma IA.`

Título da home: **Encontre o que você precisa na Base Nacional Comum Curricular**  
Subtítulo: **Busque por código, por filtros ou por tema. Se quiser, também pode perguntar.**  
Título do navegador: **Encontre o que você precisa na BNCC \| Busca Base**

Ordem na página: Pesquisa por código, Pesquisa por filtros, Pesquisa simples, Pesquisa conversacional. Não numerar os modos. Não chamar de abas.

Depois da consulta, os modos não usados são botões com o próprio nome. O controle para voltar ao estado inicial é **Nova consulta**.

### 4.3 BNCC e Base

Na primeira menção de uma página institucional:

> Base Nacional Comum Curricular (BNCC)

Depois, use **BNCC** ou **Base**. Na interface de consulta, “Base” pode ser usado quando o contexto já estiver claro.

Não usar:

- Base Nacional do Currículo Comum;
- currículo nacional, como sinônimo exato;
- grade curricular;
- conteúdo obrigatório, quando o registro é uma habilidade;
- Base Comum, isoladamente.

### 4.4 Termos curriculares

| Termo | Como usar |
|---|---|
| **habilidade** | Para registros identificados assim na fonte, especialmente EF e EM |
| **objetivo de aprendizagem e desenvolvimento** | Para Educação Infantil; não chamar automaticamente de habilidade |
| **aprendizagem** | Termo guarda-chuva quando diferentes documentos/tipos aparecem juntos |
| **competência** | Manter distinção entre geral e específica |
| **etapa** | Educação Infantil, Ensino Fundamental ou Ensino Médio |
| **ano** | Ano escolar; use `5º ano`, não `quinta série` |
| **faixa etária** | Educação Infantil quando a fonte organiza dessa forma |
| **área do conhecimento** | Não reduzir a “área” na primeira ocorrência fora de filtros |
| **componente curricular** | Ex.: Matemática, História; “disciplina” só na pergunta original ou em explicação |
| **unidade temática** | Manter o termo oficial e explicar no contexto, se necessário |
| **objeto de conhecimento** | Manter o termo oficial; não substituir por “conteúdo” no registro |
| **campo de experiências** | Usar para Educação Infantil |
| **documento** | Distingue BNCC 2018, Computação e futuros complementos |
| **texto oficial** | Texto vindo do snapshot, sem edição |
| **explicação** | Reformulação produzida pelo Busca Base; nunca rotular como texto oficial |
| **fonte** | Documento oficial, página/localizador, versão e permalink |
| **recorte dos dados** | Versão fixada do `bncc-dados` usada pelo site |

Quando a tela mistura tipos, escreva “itens da Base” ou “aprendizagens”, não “habilidades” para tudo.

---

## 5. Ortografia, gramática e formato

### 5.1 Padrão

- português brasileiro;
- Acordo Ortográfico vigente;
- ordem direta: sujeito, verbo, complemento;
- voz ativa;
- uma ideia principal por frase;
- parágrafos curtos;
- listas quando houver três ou mais itens;
- contrações naturais: `na`, `pela`, `do`;
- evitar nominalizações: `buscar` em vez de `realizar a busca`.

### 5.2 Maiúsculas

Use **sentence case**:

- `Mais filtros`
- `Copiar texto e referência`
- `Ensino Fundamental`

Não usar caixa alta para dar ênfase. Códigos oficiais permanecem em maiúsculas:

- `EF05MA03`
- `EI03EO01`
- `EM13CNT101`

### 5.3 Pontuação

- Botões e rótulos curtos não levam ponto.
- Textos de ajuda e mensagens completas levam ponto.
- Evite exclamações.
- Evite reticências, exceto em estados de processamento: `Procurando trechos na Base…`
- Use dois-pontos para introduzir exemplo: `Exemplo: EF05MA03`.
- Não use barras para economizar palavras quando isso reduzir a leitura.

### 5.4 Números, anos e datas

- `5º ano`, `6º e 7º anos`;
- `0 a 1 ano e 6 meses`, conforme a nomenclatura oficial da faixa;
- `20 de agosto de 2026`;
- `1.721 aprendizagens`, com ponto de milhar;
- `2,5 segundos`, com vírgula decimal em texto;
- códigos nunca ganham espaços no resultado, mesmo que o campo aceite `EF 05 MA 03`.

### 5.5 Abreviações e siglas

- explique na primeira ocorrência de textos longos;
- BNCC pode aparecer sem expansão em campos estreitos se a página já explicou o termo;
- não exponha RAG, LLM, BM25, GPU, API, SSR ou nomes de modelos na interface;
- quando “inteligência artificial” for necessário em Sobre ou Privacidade, escreva por extenso na primeira menção.

---

## 6. Hierarquia e escaneabilidade

Uma pessoa deve entender a tela lendo apenas:

1. título;
2. subtítulos;
3. rótulos;
4. botões;
5. primeiras frases.

Regras:

- título descreve a informação ou tarefa, não a seção interna;
- subtítulo acrescenta contexto;
- primeira frase traz a conclusão;
- texto do link descreve o destino;
- não usar “clique aqui”, “saiba mais” ou “ver mais” sem objeto;
- colocar condições antes da ação quando evitam erro: `Para comparar, escolha pelo menos dois itens.`

---

## 7. Campos, instruções e exemplos

### 7.1 Rótulos

Rótulo fica visível durante o preenchimento:

- `Digite o código`
- `O que você quer encontrar na BNCC?`
- `O que você quer entender ou comparar?`

Não usar o placeholder como rótulo.

### 7.2 Placeholders

O placeholder mostra formato, não uma instrução indispensável:

- `EF05MA03`
- `Ex.: frações no 5º ano`
- `Ex.: compare leitura no 2º e no 3º ano`

Evitar:

- `Digite aqui`
- `Pesquisar…`
- parágrafos dentro do campo.

### 7.3 Ajuda

Ajuda fica perto do campo e explica apenas o necessário:

> Você pode buscar com palavras do dia a dia.

> Habilidade é o que a Base diz que deve ser aprendido em cada etapa.

> O código começa com EI, EF ou EM. Exemplo: EF05MA03

Não antecipar todos os erros possíveis.

### 7.4 Filtros

- visíveis: `Etapa`, `Ano ou faixa`, `Campo de experiências`, `Área do conhecimento`, `Componente curricular`, `Documento`, `Tipo de item`
- bloco: `Filtros da Base`
- etapa: recomendada, não obrigatória. Ajuda: `A etapa refina as listas abaixo. Você também pode buscar só por componente, documento ou tipo.`
- dependência: `Depende da etapa. Sem etapa, as opções aparecem agrupadas.`
- recuo: `Definidos pela etapa`
- documento: `Independente da etapa.` — faceta de primeira classe, não escondida em “mais filtros”
- campo: `Campo de experiências` — eixo da Educação Infantil, no lugar de componente
- depois da consulta: `Alterar filtros`
- contador: `2 filtros aplicados`
- limpar: `Limpar filtros`
- vazio honesto: `Retirar última escolha` quando o recorte não tem itens
- remover um: valor visível + **Remover**; nome acessível `Remover filtro 5º ano`
- vigência: `Incluir itens revogados`

Não usar `Filtrar resultados` como porta de entrada dos filtros principais.

---

## 8. Botões e links

### 8.1 Botões

Comece com verbo e descreva o resultado:

- `Buscar`
- `Perguntar`
- `Nova consulta`
- `Mais filtros`
- `Ver mais códigos`
- `Abrir habilidade`
- `Copiar texto`
- `Copiar texto e referência`
- `Copiar resposta`
- `Copiar resposta e fontes`
- `Compartilhar`
- `Baixar .txt`
- `Cancelar pergunta`
- `Tentar novamente`
- `Usar esta busca`

Evitar:

- `OK`;
- `Enviar`, quando pode ser mais específico;
- `Continuar`, sem dizer para onde;
- `Sim` e `Não` quando a ação pode ser nomeada;
- dois botões com o mesmo texto e destinos diferentes.

### 8.2 Links

O texto precisa fazer sentido fora do parágrafo:

- `Ver todas as habilidades de Matemática`
- `Ler como os dados são atualizados`
- `Buscar esta habilidade na Base`

Evitar:

- `Clique aqui`
- `Leia mais`
- URL completa como texto, salvo quando a pessoa precisa copiá-la.

---

## 9. Resultados

### 9.1 Rótulos

- `Texto da BNCC`
- `Explicação do Busca Base`
- `Etapa`
- `Ano`
- `Faixa etária`
- `Componente curricular`
- `Área do conhecimento`
- `Unidade temática`
- `Objeto de conhecimento`
- `Campo de experiências`
- `Documento`
- `Fonte`
- `Vigência`
- `Recorte dos dados`

### 9.2 Quantidade

- `1 resultado`
- `12 resultados`
- `Mais de 100 resultados. Use os filtros para reduzir a lista.`

Não dizer `12 resultados encontrados com sucesso`; sucesso já está evidente.

### 9.3 Ações concluídas

- `Texto copiado.`
- `Texto e referência copiados.`
- `Link copiado.`
- `Arquivo baixado.`
- `3 itens selecionados.`

Confirmações somem automaticamente, mas permanecem tempo suficiente para leitura e não movem o foco.

### 9.4 Referência copiada

Modelo:

> EF05MA03 — [texto oficial]  
> Matemática · 5º ano · Ensino Fundamental  
> Fonte: Base Nacional Comum Curricular, p. [número]. Recorte [versão].  
> https://www.buscabase.com.br/habilidade/EF05MA03

Não creditar o `bncc.dev` em cada cópia de resultado. A atribuição da compilação fica no rodapé, em Sobre e nos metadados de exportação quando necessário.

---

## 10. Sugestões de código

Mensagem para leitor de tela:

- `3 sugestões de código.`
- `Nenhuma sugestão para este início de código.`

Conteúdo visual de cada cartão:

> **EF05MA03**  
> Identificar e representar frações…  
> 5º · Matemática

Não escrever:

- `Talvez você queira dizer…` a cada tecla;
- `Autocompletar`;
- `Resultado inteligente`;
- `Sugestão da IA`.

O item abre o registro. Ele não deve parecer uma correção do que foi digitado.

---

## 11. Espera e processamento

### 11.1 Busca rápida

- `Buscando na Base…`
- `Carregando mais resultados…`

### 11.2 Perguntar

Sequência aprovada:

1. `Procurando trechos na Base…`
2. `Conferindo códigos e fontes…`
3. `Preparando a resposta…`
4. `Resposta em andamento`

Fila:

> Há outras perguntas na fila. A sua será respondida em seguida.

Só mostrar tempo ou posição quando o sistema tiver uma estimativa confiável.

### 11.3 Evitar

- `A IA está pensando…`
- `Raciocinando…`
- `Consultando minha memória…`
- percentuais inventados;
- frases rotativas apenas para distrair;
- `Isso pode demorar um pouquinho`.

### 11.4 Cancelamento

Botão:

> Cancelar pergunta

Depois:

> Pergunta cancelada. O texto continua no campo para você editar ou tentar de novo.

---

## 12. Erros

Uma boa mensagem responde:

1. o que aconteceu;
2. se algum conteúdo foi preservado;
3. o que fazer agora.

Não usar código técnico, culpa ou humor.

### 12.1 Código em formato inválido

> **Esse código não está no formato esperado.**  
> Confira letras e números. Exemplo: EF05MA03. Você também pode buscar pelo tema.

Ações:

- `Tentar outro código`
- `Buscar pelo tema`

### 12.2 Código bem formado, mas inexistente

> **Esse código tem um formato válido, mas não existe no recorte atual da Base.**  
> A numeração oficial pode ter lacunas. Confira o código ou veja opções próximas.

Não escrever `Código inválido`, pois o formato pode estar correto.

### 12.3 Nenhum resultado

> **Não encontramos resultados para “parte-todo”.**  
> Tente outras palavras ou remova um dos filtros.

Ações:

- `Remover filtros`
- `Editar busca`

### 12.4 Falha de conexão

> **A conexão foi interrompida.**  
> Sua busca foi preservada. Verifique a internet e tente novamente.

### 12.5 Erro interno

> **Não foi possível concluir a busca agora.**  
> Sua consulta foi preservada. Tente novamente.

Se houver identificador:

> Código de atendimento: `ABC123`

### 12.6 Limite de perguntas

> **Você atingiu o limite de perguntas deste período.**  
> Pesquisa por código, Pesquisa por filtros e Pesquisa simples continuam disponíveis.

Só informar um horário de liberação se ele for verdadeiro.

### 12.7 Perguntar indisponível

> **Pesquisa conversacional está temporariamente indisponível.**
> Você ainda pode encontrar e copiar itens usando Pesquisa por código, Pesquisa por filtros ou Pesquisa simples.

Evitar `Estamos em manutenção` se o motivo real for fila ou capacidade.

---

## 13. Respostas geradas e limites

### 13.1 Identificação

Antes ou junto da resposta:

> Resposta gerada a partir dos trechos encontrados na Base.

Cada fonte deve ter código e contexto. O rótulo não pode sugerir que a explicação é texto oficial.

### 13.2 Quando há base suficiente

Estrutura:

1. resposta direta;
2. pontos ou comparação, se necessário;
3. limites da interpretação;
4. fontes.

### 13.3 Quando a BNCC não diz

Modelo:

> **A BNCC não traz uma metodologia específica para essa situação.**  
> Ela define [o que foi encontrado]. Posso mostrar as habilidades relacionadas ou ajudar a comparar os anos.

Não completar com conhecimento geral sem marcar outra fonte, que está fora do escopo inicial.

### 13.4 Quando faltam fontes

> **Não encontrei trechos suficientes na Base para responder com segurança.**  
> Tente informar a etapa, o ano, o componente ou um código.

### 13.5 Comparações

Nomeie os critérios:

- `O que muda no texto`
- `Ano e componente`
- `Pontos em comum`
- `O que a Base não define`
- `Fontes usadas`

Não dizer que uma habilidade é “mais avançada” sem uma relação oficial ou uma explicação qualificada.

### 13.6 Percursos

> Esta organização foi sugerida pelo Busca Base com os itens encontrados. A BNCC não define essa ordem como uma progressão oficial.

---

## 14. Páginas de descoberta e metadados

### 14.1 Títulos visíveis

- `EF05MA03: frações no 5º ano`
- `Habilidades da BNCC para o 5º ano`
- `Matemática na BNCC`
- `Competência geral 7: Argumentação`

O complemento depois dos dois-pontos deve ser fiel ao texto e ao contexto. Não transformar toda habilidade em uma palavra-chave genérica.

### 14.2 Títulos do navegador

- `EF05MA03: habilidade de Matemática do 5º ano | Busca Base`
- `Habilidades da BNCC para o 5º ano | Busca Base`
- `Matemática na BNCC: habilidades e anos | Busca Base`

### 14.3 Descriptions

Entre 1 e 2 frases, informativas e sem chamada promocional vazia:

> Consulte o texto da habilidade EF05MA03, seu contexto em Matemática no 5º ano, objetos de conhecimento e fonte na BNCC.

Evitar:

> Descubra tudo o que você precisa saber sobre a incrível habilidade EF05MA03!

### 14.4 Chamada para a home

- `Buscar na Base`
- `Buscar esta habilidade`
- `Fazer uma pergunta sobre este item`

Não usar `Voltar`, pois quem chegou por um buscador pode nunca ter visitado a home.

---

## 15. Acessibilidade do conteúdo

### 15.1 Links e controles

- nomes únicos e descritivos;
- informar formato e tamanho de download: `Baixar .txt (12 kB)`;
- não repetir o mesmo “Ver mais” em uma lista;
- texto acessível de ícone inclui objeto: `Copiar código EF05MA03`.

### 15.2 Texto alternativo

- descrever função e informação, não aparência;
- imagem decorativa tem alternativa vazia;
- não começar com “Imagem de”;
- diagramas precisam de equivalente textual;
- logotipo: `Busca Base`;
- ícone ao lado de rótulo não repete o rótulo no leitor de tela.

### 15.3 Leitores de tela

- status curto em regiões vivas;
- não anunciar toda atualização do streaming;
- em uma resposta em fluxo, anunciar início e conclusão, não token por token;
- códigos podem ter uma versão de pronúncia acessível quando testes mostrarem necessidade;
- evitar símbolos visuais como `/`, `→` e `·` em nomes acessíveis se atrapalharem a leitura.

### 15.4 Compreensão

- explicar jargão no ponto de uso;
- não depender de metáforas;
- evitar dupla negativa;
- manter a mesma palavra para o mesmo objeto;
- usar texto junto de cor e ícone;
- não exigir memorização de instrução exibida em outra tela.

---

## 16. Privacidade e confiança

No campo Perguntar, aviso permanente:

> As respostas usam trechos da Base e mostram as fontes. A BNCC não é um plano de aula.

Também no campo:

> Não inclua nomes ou outros dados pessoais de estudantes.

Em Sobre/Privacidade:

- explicar que as consultas (texto, filtros, códigos) ficam neste servidor, sem cookie e sem IP na mesma linha;
- dizer se uma pergunta é enviada a um serviço externo;
- não usar “100% seguro” ou “totalmente anônimo”;
- não dizer que o produto “conhece a BNCC inteira”; dizer que ele consulta o recorte informado;
- não prometer precisão absoluta; explicar validação de códigos e fontes.

Aviso institucional:

> O Busca Base é um projeto independente e não é um site oficial do MEC.

Atribuição:

> Dados estruturados da BNCC por [bncc.dev](https://bncc.dev) (CC BY 4.0), a partir dos documentos oficiais do MEC e do CNE. Recorte `[versão]`. Adaptações: indexação, busca e interface próprias.

---

## 17. O que nunca escrever

- “resultado garantido”;
- “100% correto”;
- “a BNCC recomenda esta aula”, sem texto que sustente;
- “o aluno deve”, se o enunciado oficial não usa essa formulação;
- “segundo a IA”;
- “nosso algoritmo inteligente”;
- “conteúdo para crianças normais”;
- “pais e mães” quando “responsáveis” resolve;
- “clique”, em instrução que também precisa funcionar por teclado ou toque;
- “fácil”, “simples” ou “óbvio” para julgar uma tarefa;
- “erro do usuário”;
- “código inválido” quando ele é bem formado e apenas inexistente;
- “sem resultados” sem um próximo passo.

---

## 18. Checklist editorial

Antes de aprovar um texto:

- [ ] Está em português brasileiro?
- [ ] A informação principal vem primeiro?
- [ ] A frase está em voz ativa e ordem direta?
- [ ] Há uma palavra mais comum com a mesma precisão?
- [ ] Termos oficiais necessários foram mantidos e explicados?
- [ ] Texto oficial e explicação estão claramente separados?
- [ ] A mensagem ajuda a dar o próximo passo?
- [ ] O texto evita culpar, infantilizar ou presumir conhecimento?
- [ ] Botões começam com verbo e descrevem a ação?
- [ ] Links fazem sentido fora do contexto?
- [ ] Singular, plural, datas, números e códigos estão corretos?
- [ ] O conteúdo continua compreensível sem cor ou ícone?
- [ ] Status de leitor de tela é curto e útil?
- [ ] Metadados correspondem ao conteúdo visível?
- [ ] Limites da BNCC e da geração estão explícitos?
- [ ] O texto foi lido em voz alta e testado no espaço real da interface?

---

## 19. Glossário interno para quem escreve

| Termo interno | O que significa | Aparece para o público? |
|---|---|---|
| RAG | Recuperar trechos antes de gerar resposta | Não |
| reranker | Reordena resultados por relevância | Não |
| LLM | Modelo que redige respostas | Somente explicado em textos técnicos |
| grounding | Resposta sustentada por fontes | Dizer `com fontes` |
| chunk | Unidade indexada | Dizer `trecho` ou o tipo curricular |
| hallucination | Conteúdo inventado pelo modelo | Dizer `informação ou código não confirmado` |
| snapshot | Versão fixada dos dados | Dizer `recorte dos dados` |
| feature flag | Controle de disponibilidade | Não |
| typeahead | Sugestões durante digitação | Dizer `sugestões de código` |
| permalink | URL estável | Dizer `link permanente` quando necessário |

---

## 20. Referências

- [Lei nº 15.263/2025 — Política Nacional de Linguagem Simples](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15263.htm)
- [Design System do Governo Federal](https://www.gov.br/governodigital/pt-br/estrategias-e-governanca-digital/transformacao-digital/ferramentas/design-system/design-system)
- [GOVBR-DS — Acessibilidade](https://govbr-ds.gitlab.io/tools/govbr-ds-wiki/desenvolvimento/acessibilidade/)
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
