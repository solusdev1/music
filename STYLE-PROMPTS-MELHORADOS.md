# Style Prompts Melhorados — Suno (Priorizar Vocals)

## Problema Identificado
Suno estava gerando **apenas instrumental** porque os prompts eram ambíguos sobre a presença de voz.

## Solução: Estrutura de Prompt Otimizada

### Fórmula Correta de Style Prompt
```
[VOCALISTA] + [TIPO DE VOZ] + [ESTILO/GÊNERO] + [INSTRUMENTOS SUPORTE] + [EFEITOS/QUALIDADE]
```

---

## 1. El Camino de la Fé — Style Prompt Otimizado

### ❌ ANTERIOR (Gerou Instrumental)
```
Blues gospel latino, voz profunda, slide guitar, órgano cálido, oración nocturna, mezcla vintage
```

### ✅ NOVO (Garante Vocal)
```
Male deep baritone vocals, spanish gospel blues with powerful chorus hook, slide guitar accompaniment, 
warm organ harmony, intimate late-night prayer style, analog recording warmth, clear vocals in front
```

**Quebra:**
- **Male deep baritone vocals** — VOZ É O ELEMENTO PRINCIPAL
- **powerful chorus hook** — refrão precisa ser forte/cantável
- **slide guitar accompaniment** — guitarra SUPORTA, não lidera
- **warm organ harmony** — órgão em segundo plano
- **intimate late-night prayer style** — tom emocional
- **analog recording warmth** — qualidade vintage
- **clear vocals in front** — VOZ ESTÁ À FRENTE

---

## 2. Southern Grace Roads (en-US) — Style Prompt Otimizado

### ❌ ANTERIOR (Risco de Instrumental)
```
Southern country gospel blues, dobro guitar, modest organ, warm baritone, dry vintage recording, back-porch intimacy
```

### ✅ NOVO (Garante Vocal Claro)
```
Warm American baritone vocals, country gospel with memorable chorus, dobro guitar as rhythmic support,
subtle organ underneath, intimate back-porch storytelling, vintage dry recording, male lead vocal prominent,
clear diction on every lyric, sing-along chorus hook
```

**Quebra:**
- **Warm American baritone vocals** — VOZ NO INÍCIO
- **memorable chorus** — refrão memorável e cantável
- **dobro guitar as rhythmic support** — guitarra suporta ritmo
- **subtle organ underneath** — órgão em background
- **male lead vocal prominent** — VOZ PROEMINENTE (explícito)
- **clear diction on every lyric** — clareza de letra
- **sing-along chorus hook** — refrão participativo

---

## 3. Variações para Diferentes Ênfases

### Quando quer **VOZ SOLO** (lamento, intimidade)
```
Lead male baritone vocals, intimate and vulnerable delivery, minimal instrumentation,
sparse guitar, soft organ pad, focus on emotional vocal performance, analog warmth,
lyrics clear and front-center, conversational and personal tone
```

### Quando quer **VOZ + REFRÃO POTENTE** (celebração, esperança)
```
Strong male baritone vocals, powerful gospel chorus with full vocal delivery,
slide guitar propelling rhythm, warm organ swells, dynamic vocal range,
memorable hook-driven chorus, vintage gospel recording style, vocals lead the mix
```

### Quando quer **DUETO ou CORAL SUPORTE** (climax final)
```
Lead male baritone vocals, supported by gospel choir response, call-and-response structure,
slide guitar, organ harmony, powerful group chorus ending, vintage recording warmth,
vocal harmony layers, inspirational gospel arrangement, clear lead vocal over ensemble
```

---

## 4. Template Genérico Melhorado

Use este template para ANY música gospel/christian:

```
[GENDER + VOICE TYPE] vocals, [SONG TYPE/GENRE] with [EMOTIONAL TONE],
[MAIN INSTRUMENT] as [ROLE], [SECONDARY INSTRUMENT] [ROLE], 
[TERTIARY INSTRUMENT] in background, [VOCAL TECHNIQUE/DELIVERY],
[RECORDING STYLE], [EMPHASIS: "vocals lead the mix" OR "clear vocal in front"],
[CULTURAL/REGIONAL STYLE], [FINAL QUALITY NOTE]
```

**Exemplo Completo:**
```
Deep male baritone vocals, spanish gospel blues with intimate storytelling,
slide guitar as rhythmic companion, warm organ providing harmonic support,
subtle percussion in background, emotional vocal delivery with vulnerable moments,
analog vintage recording warmth, vocals prominent and leading the mix,
late-night prayer room atmosphere, clear lyrical presence throughout
```

---

## 5. Palavras-Chave Críticas para VOZ

### ✅ USE SEMPRE:
- "vocals lead the mix"
- "clear vocal in front"
- "vocal prominent"
- "[GENDER] [VOICE TYPE] vocals"
- "memorable chorus hook"
- "lead vocal delivery"
- "vocal-forward arrangement"

### ❌ EVITE:
- "instrumental gospel" (gera 100% instrumental)
- "guitar-driven" (sem "vocals")
- "minimalist" (sem clareza sobre voz)
- "ambient" (pode ser só ambiente)
- "backing vocals only" (reduz lead)

---

## 6. Exclude Styles — IMPORTANTE

Para evitar que Suno coloque efeitos vocais demais ou mude o estilo:

### ✅ RECOMENDADO
```
EDM, trap, reggaetón, rap, pop worship brillante, autotune pesado, 
metal, bateria electrónica, voces infantiles, Auto-Tune heavy effect,
vocal processing, reverb overdrive, upbeat pop
```

### Adicione para Gospel:
```
..., gospel choir only, instrumental only, background vocals only,
overly produced, contemporary worship pop, upbeat contemporary, 
electronic gospel, modern pop Christian
```

---

## 7. Atualizar Configs no Music-Factory

### El Camino de la Fé (niches/camino_de_la_fe.json)
```json
"style_prompt": "Male deep baritone vocals, spanish gospel blues with powerful chorus hook, slide guitar accompaniment, warm organ harmony, intimate late-night prayer style, analog recording warmth, clear vocals in front"
```

### Southern Grace Roads (niches/southern_grace_roads.json)
```json
"style_prompt": "Warm American baritone vocals, country gospel with memorable chorus, dobro guitar as rhythmic support, subtle organ underneath, intimate back-porch storytelling, vintage dry recording, male lead vocal prominent, clear diction on every lyric, sing-along chorus hook"
```

### Country Blues e Fé (niches/country_blues_fe.json)
```json
"style_prompt": "Male deep baritone vocals, country blues gospel brasileiro with powerful chorus, slide guitar accompaniment, warm organ harmony, late-night prayer feel, analog recording warmth, clear vocals leading the mix, emotional delivery"
```

---

## 8. Checklist para Testar no Suno

Antes de gerar, verifique:

- [ ] **Vocals mencionadas no início?** (não no meio)
- [ ] **[GENDER + VOICE TYPE]** explícito? (não "voz" vaga)
- [ ] **"vocals lead the mix" ou "vocal prominent"?** (obrigatório)
- [ ] **Chorus/Hook mencionado?** (refrão precisa ser claro)
- [ ] **Instrumentos = "support" ou "accompaniment"?** (não "guitar-driven")
- [ ] **Exclude styles contém "instrumental only"?** (evita confusão)
- [ ] **Sem palavras ambíguas?** (evita "ambient", "minimalist")

---

## 9. Exemplo Completo para Suno (Copy-Paste Pronto)

### El Camino de la Fé — Semana 1
**STYLE:**
```
Male deep baritone vocals, spanish gospel blues with powerful chorus hook, slide guitar accompaniment, 
warm organ harmony, intimate late-night prayer style, analog recording warmth, clear vocals in front, 
emotional vocal delivery, memorable chorus for sing-along, vocals-forward arrangement
```

**EXCLUDE:**
```
EDM, trap, reggaetón, rap, pop worship brillante, autotune pesado, metal, bateria electrónica, 
voces infantiles, instrumental only, gospel choir only, auto-tune heavy, vocal processing overdrive, 
upbeat contemporary, electronic gospel, reverb overdrive
```

**LYRICS:**
[Cole o arquivo 03-lyrics-suno.txt com [Spoken Intro] + musica completa]

---

## 10. Se Ainda Gerar Instrumental

**Tente adicionar ao style:**
```
ADD: "this is a vocal song, not instrumental, strong male voice singing every verse and chorus"
```

Ou use este prompt super explícito:
```
VOCALS ONLY - Male baritone singing gospel blues, chorus is sung not instrumental, every verse has vocals,
slide guitar backup only, organ harmony only, vocals must be the main element, clear singing throughout,
spanish lyrics sung with emotion, memorable vocal melody, this is NOT instrumental
```

---

**Documento preparado por:** Claude (Music Factory — Suno Optimization)  
**Data:** 2026-07-31  
**Status:** Pronto para implementar em próximas gerações
