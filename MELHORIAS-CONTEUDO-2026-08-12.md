# Agentes de conteúdo → music-factory (2026-08-12)

O que as skills de criação de conteúdo do operador (`gospel-blues-channel`,
`musica-ia`, `youtube-channel-analyst`, `vintage-soul-blues-pipeline`) sabem
que o `music-factory` ainda não aplicava — e o que passou a ser código.

A regra de corte foi uma só: **entra o que a operação real dos canais mediu ou
o que corrige um modo de falha documentado neste repositório.** Fórmula de
skill que não tem correspondência no que é operado hoje ficou de fora, e está
listada no fim com o motivo.

---

## O que mudou

### 1. A voz vem antes do gênero no style prompt

**Origem:** `STYLE-PROMPTS-MELHORADOS.md` (2026-07-31, escrito e nunca
aplicado) + style tag base da `gospel-blues-channel` §2.

O diagnóstico já existia no repositório: prompts que abrem pelo gênero e citam
a voz no fim (`"Country blues gospel BR, slide guitar, órgão suave, barítono
rouco"`) fazem o Suno devolver faixa quase instrumental. O documento propunha a
fórmula correta, mas ela nunca chegou aos configs — os seis canais seguiam com
o prompt antigo.

Virou `core/style.py`, com a ordem `[VOZ] + [identidade] + [instrumentação] +
[âncoras]`, o campo `voz` nos cinco canais de canção, e as guardas
`instrumental only, backing vocals only, no lead vocals` no exclude.

O canal instrumental (`peaceful_deep_sleep`) é excluído de toda essa lógica por
construção, e há teste garantindo que nenhuma âncora vocal chegue lá.

### 2. Ofício da letra separado das regras do canal

**Origem:** `gospel-blues-channel` §2 (estrutura lírica, regras de refrão) e
`musica-ia` (acentuação emocional, call & response).

`regras_extra` dizia o que é *daquele canal*. Faltava o que vale para qualquer
letra que vai virar áudio: gancho na primeira linha cantada, refrão de no
máximo 8 palavras por linha, call & response marcado, acentuação emocional
limitada a 2 por verso, ponte que traz o tema de forma reconhecível.

Virou `core/lyriccraft.py`, num lugar só — repetir isso em seis configs
garantiria que os seis divergissem na primeira edição. Canal instrumental
recebe o bloco equivalente para direção sonora.

### 3. Score 0–100 da letra antes de gerar o áudio

**Origem:** `youtube-channel-analyst` §3D (Score de Viralidade).

A skill pontua por BPM, instrumentação, duração, ganchos e fórmula de título —
critérios pensados para analisar canal alheio. Adaptados para o que este
sistema tem sob a mão na hora certa (a letra recém-saída do modelo):
estrutura, refrão cantável, gancho em 3s, título dentro da fórmula e
originalidade contra o acervo, esta última reaproveitando o `quality` que já
existia.

`cli.py score`. Em canal instrumental recusa em vez de devolver número
inventado.

### 4. Titular pelo pipeline

**Origem:** `DIAGNOSTICO-ENTREGA-2026-08-07.md` §"Por que a proteção do sistema
não funcionou" — não é fórmula de skill, é a causa-raiz medida.

O `cooldown_gancho_dias` existia e estava desligado na prática: os títulos
eram escritos fora do `daily-brief`, único caminho que chamava
`register_hook()`. `hook_usage` ficava vazia e o cooldown liberava tudo,
sempre. Resultado medido: mesmo gancho em 8 de 20 títulos, primeiro vídeo com
8.629 views e mediana de 779 nos sete seguintes.

`cli.py titulo --registrar` titula um vídeo avulso sem rodar a pauta inteira, e
é o que alimenta o histórico.

Junto veio `ganchos_aposentados`: aposentar «DEUS CONHECE SUA DOR» tira do
banco também «DEUS VIU SUA DOR», que divide 3 de 4 palavras e disputa a mesma
busca. Já aplicado no config do `country_blues_fe`.

### 5. Hashtags e keywords por vídeo

**Origem:** `gospel-blues-channel` §3.3/3.5 (keywords nos primeiros 500 chars,
banco de hashtags) + `IDEIAS-VIRALIZACAO-2026-08-07.md` §8.

`brief.py` fazia `" ".join(cfg["hashtags"])` — as mesmas 11 hashtags em todo
vídeo. Somado a títulos que dividiam o gancho, é sinal de duplicata.

`core/seo.py` monta marca fixa + tags derivadas do tema (`Salmo 91 — proteção
na estrada escura` → `#Salmo91 #Proteção #Estrada`) + rotação determinística do
resto do banco. A descrição ganhou a linha de keywords sob o título, e o pacote
de playlist saiu com `checklist-publicacao.txt`.

---

## O que ficou de fora, e por quê

| Da skill | Por que não entrou |
|---|---|
| **Funil de Shorts** (`gospel-blues-channel` §4, o modo que a skill chama de mais importante) | Decisão do operador registrada no repositório: `"shorts_policy": "nenhum"` nos 6 canais. Reintroduzir contra decisão explícita não é melhoria. |
| **DistroKid, roadmap de monetização, calendário** | São processo do operador fora do sistema; o `music-factory` não publica nem distribui. Entrariam como documento, não como código. |
| **Prompts visuais / DNA visual** (`vintage-soul-blues-pipeline`) | Os configs já têm `prompt_thumbnail` por canal, calibrado para cada nicho. Substituir por prompt genérico de outro projeto pioraria. |
| **Compilação de 1–2h** (§8B) | Já é o que `playlist.build` faz, com `target_sec` por nicho. Não há lacuna. |
| **CPM / receita estimada** (`youtube-channel-analyst` §3B) | Depende de coleta VIDIQ recorrente que hoje é semanal e manual; estimar receita sobre cache velho produziria número com aparência de dado. |

### Correção pendente, fora deste repositório

A skill `gospel-blues-channel` §0 mapeia `UCxHLI0_emNO7uHao-oXnpXQ` como
"Blues & Louvores" e `UC88Z-g2rq8bo0sasKDveB-Q` como "Blues & Praises". A
coleta VIDIQ de 07/08 mostra que os canais foram renomeados — são **Estrada da
Fé** e **Faith Road**. A skill vive em `~/.claude/skills/`, fora do repositório,
então a correção precisa ser feita lá; enquanto não for, toda análise que ela
gerar sai apontando nome errado.

---

## Próximo passo mensurável

O ciclo curto que fecha o que foi mudado aqui:

1. Titular os próximos vídeos com `cli.py titulo --registrar` (sem isso, nada
   do item 4 tem efeito).
2. Rodar `cli.py score` em cada letra antes de mandar para o Suno e anotar o
   score junto com o vídeo publicado.
3. Depois de ~10 vídeos, cruzar score com views/dia via `cli.py learn`. Se não
   houver correlação, os pesos dos critérios estão errados e devem mudar — o
   score é uma hipótese testável, não uma verdade.
