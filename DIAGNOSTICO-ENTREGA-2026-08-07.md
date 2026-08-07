# Por que a entrega do Country Blues e Fé caiu

Análise de 20 vídeos publicados entre 14/07 e 05/08/2026, com dados reais do
YouTube via VIDIQ (canal `UCMg75Rr0g5wh6huDM4ri2yQ`).

---

## A queda

| Período | Mediana de views |
|---|---:|
| 14–21/07 | 528 |
| 23–30/07 | 779 |
| 31/07–05/08 | **186** |

O vídeo de 05/08 está com 21 views e 0,8 views/hora.

## O engajamento subiu

Likes/views passou de **2,39%** (1ª semana) para **3,69%** (última).

Este é o dado que define o diagnóstico. Se o conteúdo tivesse piorado, o
engajamento cairia junto com o alcance. Ele subindo enquanto as views caem
significa que quem vê está gostando mais do que antes: **o problema é
distribuição, não qualidade da música.**

---

## Causa: o canal está competindo consigo mesmo

**"DEUS CONHECE SUA DOR" aparece em 8 dos 20 títulos (40%).**

| # | Data | Views |
|---:|---|---:|
| 1 | 15/07 | **8.629** |
| 2 | 16/07 | 1.306 |
| 3 | 20/07 | 186 |
| 4 | 26/07 | 2.920 |
| 5 | 28/07 | 209 |
| 6 | 28/07 | 759 |
| 7 | 29/07 | 779 |
| 8 | 01/08 | 1.088 |

O primeiro fez 8.629; a mediana dos sete seguintes é 779 — queda de 91%. Em
pares consecutivos, quatro colisões ficaram com **16%, 17%, 28% e 31%** do
desempenho do vídeo anterior.

22 dos 105 pares de títulos compartilham ≥50% das palavras, vários a 89%.

Oito vídeos disputam a mesma consulta; o YouTube mostra um e os outros ficam
sem ar. É por isso que os vídeos deixaram de entregar nos próprios títulos e
hashtags que miram.

---

## Por que a proteção do sistema não funcionou

O `music-factory` tem `cooldown_gancho_dias: 30` e `learn.hook_collisions()`
exatamente para isto. Dois motivos independentes para ter falhado:

### 1. `hook_usage` está vazia para este nicho

As 11 linhas existentes são todas de `southern_grace_roads`. Sem histórico, o
cooldown não tem contra o que comparar — o sistema acredita que nenhum gancho
foi usado e libera todos, sempre.

A causa disso: os ganchos publicados **não estão na lista `ganchos` do config**
(o config tem "DEUS VIU SUA DOR"; o publicado é "DEUS CONHECE SUA DOR"). Os
títulos estão sendo escritos fora do `daily-brief`, que é o único caminho que
chama `catalog.register_hook()`. Contornar o pipeline desliga a proteção.

### 2. Bug no detector (corrigido)

`learn.extract_hook()` cortava o título no primeiro emoji. Quando o título
**começa** com 🙏 — metade deles — o primeiro pedaço vinha vazio e o fallback
devolvia o *título inteiro* como gancho. Então `🙏 DEUS CONHECE SUA DOR | ...`
nunca casava com `DEUS CONHECE SUA DOR 🙏 ...`.

O detector via 5 colisões, atribuindo a maior ao título inteiro. Corrigido, vê
6, todas sob o mesmo gancho. Ver commit `a5ae462` e
`tests/test_learn.py::test_extract_hook_ignora_emoji_no_inicio`.

---

## Fatores secundários

| Fator | Evidência |
|---|---|
| **Formato misturado** | 2 vídeos de 4 min num canal de playlist de 1 h. Mediana deles 174 views, contra 644 dos longos. Ensinam sinal de sessão errado. |
| **Horário disperso** | 9 horários distintos em 20 vídeos, de 0h a 21h UTC. Música de oração/descanso é consumo habitual; sem slot fixo, o ciclo notificação→sessão não se forma. |
| **Hashtags fixas** | `brief.py` faz `" ".join(cfg["hashtags"])` — as mesmas 11 hashtags em todo vídeo, sem variação. Somado a títulos quase idênticos, reforça o sinal de duplicata. |

---

## Ações

1. **Aposentar "DEUS CONHECE SUA DOR" por 60 dias.** Está queimado; não é falta
   de força do gancho. O config tem 10 alternativos quase não usados.
2. **Titular via `daily-brief`.** É o que alimenta `hook_usage` e faz o cooldown
   existir na prática. Hoje o pipeline está sendo contornado.
3. **Retroalimentar o `published` real** e usar `cli.py learn --niche
   country_blues_fe` como painel contínuo — com o fix, ele agora mostra as
   colisões corretamente.
4. **Fixar um horário de publicação** e manter o canal só em long-form.
5. **Variar hashtags por vídeo**, derivando do tema em vez da lista fixa.
