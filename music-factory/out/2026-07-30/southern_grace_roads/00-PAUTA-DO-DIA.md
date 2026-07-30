# PAUTA DO DIA — Southern Grace Roads — 2026-07-30

## Tema do lote
**Psalm 23 — the Lord is my shepherd**
_Critério: rodízio — não usado nos últimos 60 dias._

## As 5 faixas
| # | papel | ângulo | cor sonora |
|---|-------|--------|------------|
| 1 | retenção (andamento médio, | someone who failed, felt shame, and was take | weathered low vocal, dobro leading, upri |
| 2 | narrativa (testemunho de v | the person praying at 3am because sleep won' | fiddle carrying the melody, upright bass |
| 3 | hino antigo (lento, quase  | someone caring for the sick while holding th | voice and guitar almost alone, pedal ste |
| 4 | renovação (colheita, virad | the young one who almost quit and stayed one | family harmony on the chorus, hand claps |
| 5 | descanso (fecho calmo, qua | someone starting over with nothing left | very slow hymn feel, close harmony, almo |

## O que fazer
1. Cole `01-PROMPT-LETRAS.md` no Claude → recebe as 5 letras
2. Salve cada uma em `musicas/NN-*/03-lyrics-suno.txt` (style e exclude já estão prontos)
3. Gere no Suno e registre: `cli.py add-song --niche southern_grace_roads ...`

## Avisos
- ⚠️ cooldown de tema compartilhado com 4 canal(is) irmão(s): El Camino de la Fé, Blues & Praises, Country Blues e Fé, Estrada da Fé
- ⚠️ tema por rodízio simples (sem dado de oportunidade: nenhuma coleta de oportunidade registrada)
- ⚠️ apenas 1 faixa(s) 'calm' disponível(is) para o fecho (ideal: 2). Marque faixas com mood='calm'.
- ⚠️ acervo insuficiente: faltam 13:42 para o alvo de 1:05:00 (~4 faixa(s)). A playlist sai mais curta.
- ⚠️ 5 de 10 faixas com duração ESTIMADA. Os timestamps só ficam corretos após 'set-audio' com a duração real.
- ⚠️ 5 imagem(ns) saturada(s) no acervo (room, youre, thats, somethin, hands…) — a pauta já manda evitar.
