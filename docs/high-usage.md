# Quando a geração na nuvem ficar cara

Embeddings e rerank continuam em API mesmo com tráfego alto: o corpus é pequeno e a conta não escala como conversa. Só **Perguntar** (tokens de entrada + saída) cresce com o uso.

## Quando considerar GPU própria

Meça gerações reais (`/api/health` e a fatura do provedor), não hits de cache nem buscas sem parágrafo.

Ordem de grandeza com `deepseek/deepseek-v4-flash` via OpenRouter (thinking desligado, ~2k tokens de entrada e ~400 de saída):

| Gerações / mês | Conta aproximada (Flash) | vs GPU 24 GB (~US$110–160/mês) |
|---|---|---|
| 10 mil | poucos dólares | API mais barata |
| 50 mil | dezenas | API mais barata |
| ~200–300 mil | ~US$140–250 | **zona de troca** |
| 1 milhão | centenas a mais de mil | GPU costuma ganhar |

Passe para GPU se **duas ou três faturas seguidas** passarem de ~US$160–200, se o provedor limitar taxa, ou se residência dos prompts deixar de ser aceitável. Não troque no primeiro mês “parecido”.

## Plano conciso: RunPod + o mesmo app

A API já é agnóstica de fornecedor. O recurso Coolify na CX23 **não muda**. Só o destino de `GENERATION_*`.

1. Crie um volume de rede de 50–80 GB no RunPod e monte em `/root/.cache/huggingface`.
2. Suba um pod **Community Cloud, 1× RTX 3090 24 GB**, imagem `vllm/vllm-openai:latest`, porta 8000.
3. Comando (um modelo só, o mesmo em todo o tráfego de Perguntar):

```bash
--model Qwen/Qwen3.5-9B \
--max-model-len 8192 \
--dtype float16 \
--gpu-memory-utilization 0.90 \
--enable-prefix-caching \
--api-key 'chave-longa-do-vllm'
```

4. No Environment do recurso Coolify:

```bash
GENERATION_API_URL=https://POD-8000.proxy.runpod.net/v1
GENERATION_API_KEY='chave-longa-do-vllm'
GENERATION_MODEL=Qwen/Qwen3.5-9B
GENERATION_EXTRA_BODY={}
PERGUNTAR_ENABLED=true
```

5. Redeploy do serviço `api`. Confira `/api/health` → `"perguntar": true` e um smoke de Perguntar.
6. Não exponha 8000 sem `--api-key`. Não grave consultas no disco do pod.
7. Se o pod cair: `PERGUNTAR_ENABLED=false`, suba outro 3090 **no mesmo volume**, atualize a URL.

Embeddings e rerank permanecem na OpenRouter (`google/gemini-embedding-001` e `jina/jina-reranker-v3.5`). Não coloque o reranker na GPU do gerador.

Se Community ficar instável, o próximo degrau é RunPod Secure 3090 — ainda só geração, ainda o mesmo recurso Coolify.
