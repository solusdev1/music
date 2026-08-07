# Ideias de melhoria — todos os canais

Baseado em coleta real (VIDIQ, 07/08/2026): 20 vídeos do Country Blues e Fé,
stats de Estrada da Fé e Faith Road, 47 vídeos de outliers e 38 canais
concorrentes em 4 nichos.

---

## 0. Correção: o mapa de canais da skill está errado

A skill `gospel-blues-channel` diz:

| Skill diz | Realidade (VIDIQ) |
|---|---|
| `UCxHLI0_emNO7uHao-oXnpXQ` = "Blues & Louvores" | **Estrada da Fé** |
| `UC88Z-g2rq8bo0sasKDveB-Q` = "Blues & Praises" | **Faith Road** |

Os canais foram renomeados. Corrigir na skill, senão toda análise futura sai
apontando para nome errado.

---

## 1. Onde está o esforço e onde está o resultado

Os 6 canais, medidos no mesmo dia (07/08/2026):

| Canal | Idade | Inscritos | Views | Vídeos | Views/vídeo | **Subs/dia** |
|---|---:|---:|---:|---:|---:|---:|
| **Country Blues e Fé** | 24 d | 284 | 23.795 | 23 | **1.035** | **11,83** |
| Faith Road (EN) | 120 d | 820 | 42.110 | 72 | 585 | 6,83 |
| Estrada da Fé | 7,4 anos | 7.720 | 52.238 | 102 | 512 | 2,86 |
| Noir Pulse | 7 d | 2 | 328 | 6 | 55 | 0,29 |
| **Goku's Jazz Lounge** | 102 d | **4** | **193** | 22 | **9** | **0,04** |
| Southern Grace Roads | 8 d | 0 | 22 | 4 | 6 | 0,00 |

**O Country Blues e Fé é o melhor canal do portfólio por larga margem.** Em 24
dias fez 284 inscritos e 23.795 views — mais views que o Estrada da Fé acumulou
em boa parte dos seus 7 anos, com um quinto dos vídeos. São 1.035 views por
vídeo contra 512 do segundo colocado.

**O Goku's Jazz Lounge é o oposto:** 102 dias de vida, 22 vídeos publicados,
**193 views no total e 4 inscritos**. Nove views por vídeo. É produção
integralmente perdida, e o radar explica: jazz foi o nicho com menor teto
medido (só 2 de 12 vídeos passaram de 60 pontos) e maior exigência de volume
(mediana de 163 min por vídeo, 24 vídeos/mês entre os que crescem).

**O Noir Pulse corrobora o radar.** Com 7 dias de vida já faz 55 views/vídeo —
**6x o que o Goku's Jazz Lounge faz em 102 dias.** É consistente com o achado de
que deep house tem multiplicador mediano de 42,6x contra 4,8x do gospel PT.

### A correção que a idade do canal impõe

Eu apresentei antes a queda do Country Blues e Fé sem saber que o canal tinha
24 dias. Isso muda a leitura: **o canal não está morrendo, está desacelerando.**
Os inscritos seguem subindo (3 → 284) e nunca caíram.

O que caiu, e caiu forte, é a velocidade diária de views:

| Data | Views/dia |
|---|---:|
| 31/07 | **1.986** |
| 03/08 | 810 |
| 04/08 | 415 |
| 05/08 | 394 |
| 06/08 | 467 |

**Queda de ~77% em 6 dias.** A aquisição de inscritos seguiu o mesmo caminho: 27
por dia em 30/07, 2 a 9 por dia em agosto.

O diagnóstico de canibalização continua de pé — ele explica exatamente isto:
por que um canal que estava acelerando parou de acelerar. Mas a moldura correta
é "lançamento forte perdendo tração", não "canal em colapso".

> ⚠️ **Ressalva de dado:** nos dias 01–03/08 vários canais aparecem com views
> congeladas em valores idênticos. Dois canais independentes com o mesmo
> comportamento na mesma janela é mais compatível com o VIDIQ não ter
> atualizado do que com entrega zero real. Não tratar como queda.

---

## 2. As ideias, por ordem de impacto

### ★ 1. Concentrar produção no Country Blues e Fé

É a maior alavanca disponível e não custa nada além de decisão. O canal faz
**11,83 inscritos/dia**; o Estrada da Fé faz 2,86 e o Goku's Jazz Lounge faz
0,04. A mesma produção redirecionada para o canal que já demonstrou capacidade
de 8.629 views num único vídeo muda o patamar.

O YouTube julga o canal inteiro, não vídeos isolados (a própria skill diz isso
na §5). Seis canais rasos competem entre si por atenção de produção e nenhum
acumula sinal suficiente.

**Ação:** encerrar o Goku's Jazz Lounge (102 dias, 193 views, 4 inscritos — o
nicho de jazz é o de menor teto e maior exigência de volume no radar). Pausar
Estrada da Fé e Faith Road por 60 dias. Manter o Noir Pulse com cadência
mínima, porque em 7 dias já rende 6x o Goku's e confirma o achado do radar.
Todo o resto da cadência vai para o Country Blues e Fé.

---

### ★ 2. Rotação forçada de gancho

`DEUS CONHECE SUA DOR` está em 8 dos 20 títulos. O primeiro fez 8.629 views; a
mediana dos sete seguintes foi 779. Ver `DIAGNOSTICO-ENTREGA-2026-08-07.md`.

**Ação:** aposentar o gancho por 60 dias e usar os 10 alternativos que já estão
no `config/country_blues_fe.json` e nunca foram usados. Um por vídeo, sem
repetir. Titular via `daily-brief`, que é o que alimenta o `hook_usage` e faz o
cooldown existir de fato.

---

### ★ 3. Guarânia Gospel — a descoberta do radar

Achado da coleta de hoje: o canal **Guarânia com Cristo** (7.290 inscritos)
ocupa **6 das 24 posições** do radar PT-BR, com multiplicadores de **5x a 47x**
os próprios inscritos. Um vídeo fez 340.164 views.

Guarânia é ritmo regional (Paraguai/Sul) cruzado com gospel. A fórmula de
título é rígida e repetível:

```
Guarânia Gospel Para [público em dor específica] | Louvores Que [benefício]
```

Exemplos reais: *Para Curar a Alma*, *Para Quem Precisa de Deus*, *Para Quem
Está Sofrendo*, *Para Quem Precisa de um Milagre*, *Para Agradecer a Deus*.

Nenhum canal grande ocupou o espaço. É o nicho adjacente mais barato de testar,
porque a produção é a mesma que você já faz.

**Ação:** produzir 3 vídeos nesse molde e medir. Se o multiplicador replicar,
vira série.

---

### ★ 4. Estudar o Country de Fé título por título

Canal de 3.660 inscritos, **+88% de inscritos e +137% de views em 30 dias**,
publicando **25 vídeos longos por mês com média de 77 minutos**. É exatamente o
seu formato, rodando em cadência alta e crescendo.

**Ação:** rodar `vidiq_channel_videos` no `@countrydefe-c9m` e mapear os
títulos dos 25 vídeos. É o concorrente mais parecido e mais bem-sucedido.

---

### 5. Converter os vídeos de 4 minutos em Shorts de verdade

O canal tem dois vídeos de 4 min (23/07 e 31/07) que fizeram 293 e 56 views —
mediana de 174, contra 644 dos longos. Não são playlist nem Short: caem no vão.

A skill (§4) mostra que os Shorts campeões do nicho têm **60–150 segundos**,
começam no refrão e trazem a letra na tela. Still Worship fez 2,4M views assim.

**Ação:** parar de publicar 4 min. Ou vira Short de 60–150s vertical, ou entra
numa compilação.

---

### 6. Compilação semanal de 1–2 horas

A skill (§8B) aponta como a maior alavanca para watch hours, e seus vídeos já
têm ~60 min. Uma compilação de 1h a 40% de retenção = ~24 min de watch time por
view.

No radar de jazz, os canais que crescem 68–237%/mês publicam com **mediana de
163 minutos** — o mercado de long-form suporta muito mais que 1h.

**Ação:** 1 compilação de 2h por semana, com capítulos (timestamps aumentam
retenção e SEO).

---

### 7. Fixar horário de publicação

9 horários distintos em 20 vídeos, de 0h a 21h UTC. Música de oração e descanso
é consumo habitual; sem slot fixo o ciclo notificação→sessão não se forma.

**Ação:** um horário só. A skill sugere ter/qui 19h–21h BRT.

---

### 8. Variar hashtags por vídeo

`brief.py` faz `" ".join(cfg["hashtags"])` — as mesmas 11 hashtags em todo
vídeo. Somado a títulos quase idênticos, reforça o sinal de duplicata.

**Ação:** derivar 5–7 hashtags do tema do vídeo + 3 fixas de marca, em vez da
lista fixa de 11.

---

### 9. Conferir o AI disclosure

A skill (§3.4) afirma que sem o disclaimer o YouTube suprime ~73% do alcance de
conteúdo IA nas primeiras 48h. Não consegui verificar isso pela API — as
descrições não vêm no endpoint.

**Ação:** conferir manualmente em 3 vídeos recentes se o disclosure está na
descrição **e** no card de informações. Se estiver faltando, é candidato forte a
causa adicional da queda.

---

### 10. Noir Pulse / Dark Deep House — o nicho mais aberto medido

Do radar de hoje: deep house tem **multiplicador mediano de 42,6x**, contra 4,8x
do gospel PT. Nove dos dez canais mapeados foram criados em **2026, a maioria em
maio** — corrida de ~3 meses, ainda aberta.

E há uma brecha dentro dela: 6 canais fazem faixa curta (5–8 min) e só 4 fazem
long-form (36–74 min) — e os de long-form são os **menores** do grupo. O
formato que você já domina é o menos disputado ali.

**Ação:** tratar como aposta separada, depois que o Country Blues e Fé estiver
recuperado. Não dividir foco agora.

---

## 3. Ordem sugerida

| Semana | O quê |
|---|---|
| 1 | Ideias 1, 2, 7 — concentrar, rotacionar gancho, fixar horário |
| 1 | Ideia 9 — conferir AI disclosure (é rápido e pode ser causa) |
| 2 | Ideia 4 — mapear Country de Fé; Ideia 3 — 3 vídeos Guarânia |
| 3 | Ideias 5, 6 — Shorts corretos + primeira compilação de 2h |
| 4 | Medir. Só depois considerar a Ideia 10. |

O único jeito de saber se a ideia 3 funciona é publicar 3 vídeos e medir o
multiplicador. Todo o resto acima é correção de erro conhecido; essa é aposta.
