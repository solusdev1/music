# Análise + Radar — 2026-08-12

Coleta VIDIQ de hoje (4 canais, 24 vídeos, 2 varreduras de outliers) cruzada
com os relatórios do `music-factory` sobre o banco real. A coleta anterior é de
07/08, então tudo aqui é o que mudou em 5 dias.

Custo: 30 créditos VIDIQ de 1.696 disponíveis. (O `music-factory/README.md`
ainda assume teto de 150/semana — a conta hoje tem folga de 2.000/ciclo.)

---

## 1. Os quatro canais medidos

| Canal | Idade | Inscritos | Views | Vídeos | Views/dia agora | Veredito |
|---|---:|---:|---:|---:|---:|---|
| **Country Blues e Fé** | 29 d | 309 | 26.624 | 29 | **~470** | vivo, estabilizado |
| Estrada da Fé | 7,4 anos | 7.720 | 52.307 | 102 | ~7 | dormente desde 31/07 |
| Faith Road (EN) | 125 d | 818 | 42.126 | 72 | ~2,5 | **perdendo inscritos** |
| Southern Grace Roads | 13 d | 0 | 22 | 4 | 0 | parado desde 07/08 |

### A queda do Country Blues e Fé parou

O `DIAGNOSTICO-ENTREGA-2026-08-07` registrou a curva caindo de 1.986 views/dia
(31/07) para 467 (06/08). Os seis dias seguintes:

| Data | Views no dia | Inscritos no dia |
|---|---:|---:|
| 07/08 | 394 | +4 |
| 08/08 | 408 | +2 |
| 09/08 | 486 | +7 |
| 10/08 | 553 | +7 |
| 11/08 | 587 | +6 |
| 12/08 | 401 | +1 |

**A queda livre acabou; a recuperação não começou.** O canal encontrou piso em
~400–590 views/dia e voltou a subir de leve entre 08 e 11/08. A aquisição de
inscritos está em 4,5/dia contra os 11,8/dia da média de vida e os 27/dia do
pico de 30/07.

### O que a comparação por faixa de idade mostra

Comparar julho com agosto direto é a armadilha que o próprio README descreve:
views são front-loaded, então vídeo novo sempre parece melhor. Dentro da mesma
faixa de idade:

| Faixa | Vídeos | v/dia mediano |
|---|---:|---:|
| 0–7 dias | 5 | 67 |
| 8–15 dias | 8 | **43** |
| 16–30 dias | 11 | 49 |

A faixa de 8–15 dias entrega **menos** que a de 16–30, apesar de ser mais nova.
Como v/dia decai com a idade, o esperado seria o contrário. É sinal de que a
safra da virada do mês entregou pior que a do lançamento — pequeno, com amostra
de 8 vídeos, mas na direção que o diagnóstico previa.

Nenhum vídeo desde 15/07 chegou perto dos 8.752 views do primeiro.

---

## 2. A rotação de gancho aconteceu — com dois furos

Desde 01/08 nenhum título **abre** com «DEUS CONHECE SUA DOR». Mas:

| Data | Título | Views | v/dia |
|---|---|---:|---:|
| 01/08 | VOCÊ ESTÁ CANSADO DE ESPERAR? \| **DEUS CONHECE SUA DOR** | 1.112 | 101 |
| 05/08 | **DEUS CONHECE SUAS LÁGRIMAS** 🙏 \| 1H10 de Country Gospel | 198 | 28 |

O de 01/08 manteve o gancho queimado na segunda metade e mesmo assim foi o
melhor vídeo de agosto. O de 05/08 é o gancho queimado com a última palavra
trocada — e fez 28 v/dia, dos piores da janela.

**Isto corrigiu o código.** O `filter_retired` que entrou ontem usava semelhança
de palavras com limiar 0,6 e **não pegava** esse gêmeo (ficava em 0,5). Ao
investigar, apareceram dois erros opostos:

- comparar palavra funcional dava colisão falsa — «WHEN THE HARVEST FAILED» e
  «WHEN THE WELL RAN DRY» dividem só `when` e `the`;
- comparar a palavra-tema do canal também — aposentar «DEUS CONHECE SUA DOR»
  derrubava «DEUS TE TROUXE ATÉ AQUI», que não disputa nada com ele.

A comparação agora ignora palavra funcional e exige **duas** palavras de
conteúdo em comum (o mesmo critério que `quality.title_collisions` já usava).
Resultado nos seis bancos de gancho reais: o gêmeo é pego, zero falso positivo.

---

## 3. Radar — o que está estourando no nicho

13 outliers ingeridos (`breakout-ingest`), ranqueados por multiplicador ×
velocidade × recência:

| Score | Mult. | Views | Vídeo / canal | Duração |
|---:|---:|---:|---|---:|
| 86 | 38,8x | 238.521 | CURA PARA UMA ALMA CANSADA — *KAMARGO NO LOUVOR* (6.150 subs) | **26 min** |
| 81 | 37,0x | 65.491 | QUANDO O FORTE TAMBÉM CHORA \| Samuel Riviers — *Blues Gospel \| Louvores de Fé* (1.770 subs) | **26 min** |
| 72 | 41,8x | 451.272 | Melhores Louvores 2026 — *Luz de Fé* (10.800 subs) | 2h10 |
| 70 | 13,4x | 236.161 | FILHO DA FÉ \| EU SOBREVIVI — *Gabriel Batista Filho* (17.600 subs) | 18 min |
| 62 | 48,9x | 388.873 | Guarânia Gospel Para Curar a Alma — *Guarânia com Cristo* (7.950 subs) | 55 min |

**Embalagem recorrente entre os que estouraram:** gospel (12x), guarânia (6x),
coração (5x), alma (4x), levam (4x), adoração (3x), cura (2x), precisa (2x).

### Três leituras

**1. O concorrente mais parecido com você está estourando agora.**
*Blues Gospel | Louvores de Fé* tem 1.770 inscritos, faz blues gospel em
português com nome de artista na capa (Samuel Riviers) — o mesmo modelo do
Elias Montenegro — e o vídeo «QUANDO O FORTE TAMBÉM CHORA» está em **1.507
views/hora**, 37x o tamanho do canal, com 12 dias. É o canal a estudar título
por título.

**2. Os dois maiores multiplicadores são vídeos de ~26 minutos, não playlists
de 1 hora.** Seu canal faz quase só 1h+. O formato de 26–30 min de tema único
está entregando multiplicador maior no mesmo nicho. Vale como teste — não como
troca de formato, porque a playlist longa é o que sustenta watch time.

**3. A Guarânia Gospel continua aberta, 5 dias depois.** *Guarânia com Cristo*
(7.950 subs) ocupa 6 das 13 posições, com 43k a 389k views por vídeo e fórmula
de título rígida:

```
Guarânia Gospel Para [público em dor] | Louvores Que [benefício]
```

Nenhum canal grande entrou no espaço desde a coleta de 07/08. É a mesma
produção que você já faz, com outro ritmo regional.

---

## 4. Qualidade do acervo (5 letras analisadas)

`cheiro` em 5 de 5 letras; `devagar`, `altar`, `peito`, `chuva`, `chão`,
`lágrima`, `noite`, `coração`, `vergonha`, `escuro`, `vale` em 3 de 5.
Terminações `-nho` e `-rar` em 4 de 5.

A amostra ainda é pequena (< 8 letras), então isso é indicativo. O bloco de
anti-repetição da pauta diária já carrega essa lista automaticamente.

---

## 5. Cache VIDIQ vence em 1 dia

As 19 keywords do `country_blues_fe` são da coleta de 30/07 — 13 dias. Aos 14
o cache expira e a pauta cai no rodízio simples de tema. Espaço aberto ainda
válido: `christian country music` (38k buscas, concorrência 16,8),
`country gospel music` (66k / 24,1), `viola caipira gospel` (8,1k / 22,8).

---

## 6. O que fazer, em ordem

1. **Aposentar a família inteira do gancho queimado**, não só a frase exata —
   já está no config e o detector agora pega os gêmeos.
2. **Estudar `Blues Gospel | Louvores de Fé`** (@ canal de 1.770 subs, vídeo em
   1.507 v/h). É o concorrente mais próximo e está no pico agora.
3. **Testar 3 vídeos de 26–30 min de tema único**, o formato dos dois maiores
   multiplicadores da coleta.
4. **Testar 3 vídeos no molde Guarânia** — a aposta segue de pé e continua sem
   canal grande ocupando.
5. **Decidir sobre Faith Road e Southern Grace Roads.** Um perde inscritos há
   30 dias, o outro tem 22 views em 13 dias. São os dois candidatos naturais a
   encerramento; `migrate-tracks` leva o acervo para o canal que ficar.
6. **Recoletar VIDIQ esta semana** antes do cache expirar.

---

## Nota metodológica

O `published` tinha 15 linhas da coleta de 30/07 com título abreviado; a coleta
de hoje trouxe os mesmos vídeos com título completo e entrou como linha nova,
duplicando 14 vídeos. As linhas velhas foram removidas e o banco ficou com os
24 longos reais.

Isso expõe uma lacuna: **o esquema guarda um retrato, não uma série.**
`UNIQUE(niche, title, published_at)` significa uma linha por vídeo, então cada
coleta sobrescreve a anterior e a comparação entre datas depende de alguém ter
guardado o número antigo num documento — foi o que permitiu a tabela da §1,
mas não escala. Para tendência de verdade falta uma tabela de snapshots
(`video_id`, `coletado_em`, `views`), que é o que tornaria o veredito de saúde
capaz de dizer "subindo" ou "caindo" em vez de "em janela".
