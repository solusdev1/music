# Radar YouTube Country Blues Gospel - 2026-07-30

## Execução

Pedido: radar normal do YouTube focando em country blues para novas ideias de músicas que estão dando certo.

Comando tentado no radar local:

```bash
bash run_radar.sh 5 2 --urls-file /tmp/empty_radar_urls.txt --notebooklm-file /tmp/empty_radar_notebook.md
```

Queries usadas:
- country blues gospel
- country gospel blues

Resultado do script padrão: bloqueado pelo YouTube/yt-dlp com “Sign in to confirm you’re not a bot”. Nenhum vídeo foi coletado pelo pipeline padrão.

Fallback usado para não parar a análise:
1. Busca web por vídeos/canais YouTube relacionados.
2. Busca yt-dlp em modo `extract_flat=True`, que conseguiu listar títulos/canais/URLs sem enriquecer views/likes/datas.

## Qualidade dos dados

- Dados de views vieram apenas quando apareceram nos snippets da busca web.
- O modo flat do yt-dlp trouxe bons sinais de títulos, canais e posicionamento, mas sem métricas completas.
- Este relatório é direcional/criativo, não um ranking estatístico completo.

## Sinais com métricas nos snippets

### 1. Country Gospel Blues | Soulful Worship Songs with Acoustic Guitar (4K)
- URL: https://www.youtube.com/watch?v=l6GrA58V634
- Canal: Gospel Blues Revival Official
- Views no snippet: 87K
- Duração: 2:51:13
- Sinal: playlist longa, worship acústico, promessa espiritual ampla.

### 2. Triumph Woven in Tears – Dark Country Gospel Blues | Emotional Faith Song
- URL: https://www.youtube.com/watch?v=pwD77tqqjBU
- Views no snippet: 32K
- Duração: 2:15:19
- Sinal: “dark country gospel blues” + lágrimas/triunfo = storytelling emocional forte.

### 3. Country Blues Gospel – Trust in the Lord
- URL: https://www.youtube.com/watch?v=W-owFq7O9ck
- Canal: Oldies Gospel Radio
- Views no snippet: 12K
- Sinal: título simples baseado em confiança em Deus; estética “oldies/timeless gospel”.

### 4. Southern Country Gospel Blues | 3 Hours of Acoustic Faith & Soulful ...
- URL: https://www.youtube.com/watch?v=7AoOU_5LwT4
- Views no snippet: 10K
- Duração: 3:01:19
- Sinal: formato 3 horas, fé acústica, soul sulista.

### 5. Country Gospel Blues
- URL: https://www.youtube.com/watch?v=pR6MYLQTD08
- Views no snippet: 6K
- Duração: 11:37
- Sinal: instrumental/slide guitar ainda tem busca, mas menor que playlists longas.

### 6. Lord, I'm Tired to Be Strong — Otis Walker | Emotional Country Gospel Blues
- Canal: Open Road Gospel
- Views no snippet: 1.9K
- Sinal: frase de dor direta (“tired to be strong”) com vocal/persona nomeada.

## Vídeos/títulos relevantes encontrados pelo modo flat

### Query: country blues gospel
- ✨Gospel Blues - Everlasting Grace – a heartfelt blend of Christian Blues and soulful | Gospel Blues Escape | https://www.youtube.com/watch?v=a9tzDeDdWBQ
- Powerful Christian Blues Worship | Faith That Lifts You Up | Gospel Blues Room | https://www.youtube.com/watch?v=YCBv44crM8w
- Raw Christian Music Playlist | Songs of Faith, Redemption & Regret [Country/Folk/Blues] | Holy Fire Warriors | https://www.youtube.com/watch?v=tl6NQwgL1QQ
- Everlasting Grace | Christian Blues | Soulful Worship | ChristianSoulBlues | https://www.youtube.com/watch?v=3qkImqieGrQ
- Psalm and Blues Vintage Gospel Playlist | Vintage Blues Prayers Gospel Songs | Vintage Gospel VGX | https://www.youtube.com/watch?v=4QG5FOARzHk
- Country Blues Gospel – Trust in the Lord | Oldies Gospel Radio | https://www.youtube.com/watch?v=W-owFq7O9ck
- Bless Me Jesus 🙏🏾 Deep Gospel Blues Prayer | Emotional Testimony Song | Christian Blues Haven | https://www.youtube.com/watch?v=ULRtxzbxidE
- Aliento de Tu Verdad ✝️ Mi Cristo – Blues Gospel Profundo | Cruz & Blues Worship Música Cristiana | https://www.youtube.com/watch?v=4jaZELF4gVQ
- The Psalms In Blues Hit So Deep It’s Unreal | RIVERS AND REVIVAL | https://www.youtube.com/watch?v=1UItx9upywQ
- Gospel Soul Blues – A Spirit-Filled Journey of Redemption and Heavenly Comfort | Gospel Blues Corner | https://www.youtube.com/watch?v=jG0gkFipotg

### Query: country gospel blues
- Timeless Appalachian Hymns | Old Mountain Folk Gospel (Full Album) | Appalachian Soul Hymns | https://www.youtube.com/watch?v=KjdtlUhCVhI
- This Psalm Sounds Like It Was Born in the Blues | Holy Groove | https://www.youtube.com/watch?v=6rz6D787n0U
- 【Country Gospel 2】 Calm Playlist / for Relax / Hope / Strength / Encouragement | Country Gospel Spirit | https://www.youtube.com/watch?v=3A1nymotVL0

### Query: southern gospel blues
- Southern Soul Gospel | Through The Storm: A Southern Soul Testimony | Oldies Gospel Radio | https://www.youtube.com/watch?v=HQhllDe_aHc
- Classic Blues Gospel | Soulful 1960s Vintage Sound | Timeless Spirit | Oldies Gospel Radio | https://www.youtube.com/watch?v=jnf7oWsFpQw
- Delta Blues Gospel Classics | Soulful Oldies from the Deep South | Oldies Gospel Radio | https://www.youtube.com/watch?v=PkjL9LaE1QI
- Psalm 91 ✝️: He Will Cover You With His Feathers 🙏 DEEP Southern DELTA Blues | The King's Blues Club | https://www.youtube.com/watch?v=SUiyYZ_2Rpc

### Query: christian country blues
- Raw Christian Outlaw Country Playlist - Songs of Faith, Redemption & Regret | Holy Fire Warriors | https://www.youtube.com/watch?v=U8xFlxJix6U
- Christian Outlaw Country Playlist - Raw, Honest and Unfiltered | Holy Fire Warriors | https://www.youtube.com/watch?v=KLgeYc5kApM
- Country Gospel Playlist | Dark Country/Outlaw Country/Blues Mix | RAW & HONEST | Outlaw Gospel | Holy Fire Warriors | https://www.youtube.com/watch?v=z9dEaUfixQo

## Padrões que estão aparecendo bem

### 1. Playlists longas dominam
Formatos de 2h, 3h e “full album” aparecem melhor que single curto em vários resultados.

### 2. Dor direta + promessa de fé
Títulos fortes usam dor sem rodeio:
- Tired
- Tears
- Broken
- Regret
- Prayer
- Redemption
- Trust
- Faith

### 3. “Psalms in Blues” é um ângulo forte
Vários sinais apontam para Salmos + blues:
- Psalm and Blues Vintage Gospel Playlist
- The Psalms In Blues Hit So Deep It’s Unreal
- This Psalm Sounds Like It Was Born in the Blues
- Psalm 91: He Will Cover You With His Feathers

### 4. Vintage / oldies / 1960s gospel
A estética “timeless”, “oldies”, “classic”, “1960s vintage sound” aparece bastante.

### 5. Appalachian / Southern / Delta
Subnichos que podem diferenciar o canal:
- Appalachian hymns
- Southern soul gospel
- Delta blues gospel
- Old mountain folk gospel

### 6. Outlaw / raw / honest
A vertente “raw Christian outlaw country” parece útil para títulos mais dramáticos e masculinos.

## Direção para Country Blues e Fé

Para o canal em português, vale tropicalizar os sinais em vez de copiar:

- “Lord, I'm Tired to Be Strong” → “Senhor, Cansei de Ser Forte”
- “Trust in the Lord” → “Eu Ainda Confio no Senhor”
- “Psalms in the Heartland” → “Salmos na Estrada de Terra”
- “Through The Storm” → “Passei Pela Tempestade com Deus”
- “Triumph Woven in Tears” → “Minha Vitória Foi Costurada em Lágrimas”
- “Raw, Honest and Unfiltered” → “Louvor Cru, Sincero e de Alma Aberta”

## Ideias novas recomendadas

1. Senhor, Cansei de Ser Forte
- Tema: homem quebrado que finalmente admite cansaço diante de Deus.
- Hook: “Cansei de ser forte / preciso de Ti”.
- Estilo: Country blues gospel BR, slide guitar, voz rouca, órgão suave, warm analog mix.

2. Salmo na Estrada de Terra
- Tema: oração inspirada em Salmos, sem citar versículo específico.
- Hook: “Tua sombra me cobre / Teu amor me guia”.
- Estilo: Gospel blues BR, viola caipira, slide guitar, estrada rural, coral final, warm mix.

3. Lágrimas Viraram Louvor
- Tema: dor transformada em adoração.
- Hook: “Minha dor virou louvor”.
- Estilo: Dark country gospel BR, piano baixo, resonator guitar, barítono rasgado, vintage mix.

4. Depois da Tempestade, Deus Ficou
- Tema: atravessar crise, chuva e lama com Deus.
- Hook: “A chuva passou / Deus ficou”.
- Estilo: Southern gospel blues BR, chuva, órgão, slide guitar, vocal íntimo, analog warmth.

5. Louvor Cru de Alma Aberta
- Tema: confissão honesta, sem performance religiosa.
- Hook: “Eu vim como estou”.
- Estilo: Outlaw country gospel BR, violão seco, stomp lento, vocal rasgado, raw warm mix.

6. Velho Banco da Igreja
- Tema: retorno à fé pela memória de uma igreja pequena.
- Hook: “No banco velho / Deus me achou”.
- Estilo: Vintage gospel blues BR, órgão antigo, guitarra limpa, coral distante, warm tape mix.

7. Deus Me Cobriu no Vale
- Tema: proteção espiritual no vale escuro.
- Hook: “No vale escuro / Deus me cobriu”.
- Estilo: Delta gospel blues BR, dobro, baixo acústico, voz grave, coral final, dusty warm mix.

## Próximo teste recomendado

Criar uma playlist de 5 faixas em português com estes papéis:

1. Abertura com inscrição: “Senhor, Cansei de Ser Forte”
2. Retenção/devocional: “Salmo na Estrada de Terra”
3. Dor transformada: “Lágrimas Viraram Louvor”
4. Chuva/esperança: “Depois da Tempestade, Deus Ficou”
5. Fechamento emocional: “Velho Banco da Igreja”

Título-mãe sugerido:

SENHOR, CANSEI DE SER FORTE 🙏 | 1 Hora de Country Blues Gospel Para Acalmar o Coração

Hipótese:
O título combina o padrão internacional “tired/strong” com o padrão já validado no canal “acalmar o coração”.
