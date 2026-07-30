# Radar normal YouTube — Country Blues / Português BR — 2026-07-30

## Execução

Comando rodado:

```bash
cd /opt/data/solusdev1-hermes/agents/youtube_radar_agent
bash run_radar.sh 5
```

Arquivos gerados pelo radar:

- Raw: `/opt/data/solusdev1-hermes/agents/youtube_radar_agent/data_raw/videos_raw_2026-07-30.jsonl`
- Ranking CSV: `/opt/data/solusdev1-hermes/agents/youtube_radar_agent/data_processed/videos_ranked_2026-07-30.csv`
- Relatório: `/opt/data/solusdev1-hermes/agents/youtube_radar_agent/reports/trend_report_2026-07-30.md`
- Ideias completas: `/opt/data/solusdev1-hermes/agents/youtube_radar_agent/generated_songs/production_ideas_2026-07-30.md`

Antes de rodar, os arquivos do mesmo dia foram preservados com sufixo `_pre-normal-20260730-134229`.

## Qualidade dos dados

O radar concluiu, mas o YouTube/yt-dlp retornou muitos bloqueios de anti-bot: `Sign in to confirm you’re not a bot`. Também houve aviso de runtime JavaScript ausente. Por isso, a busca normal não trouxe uma amostra ampla: o CSV final ficou com 11 registros, principalmente do canal Country Blues e Fé, mais um sinal de canal externo (`Outlaw Gospel Music`).

Como complemento de título/sinal de mercado, foram feitas buscas web por termos country gospel/country blues em português. Elas encontraram sinais recentes em títulos como:

- `A Manhã Que Deus Guardou pra Mim | Country Gospel ...`
- `10 Louvores Country para Agradecer | Música Gospel para ...`
- `Louvores Que Trazem Paz Profunda e Renovam o Coração`
- `MIX SERTANEJO GOSPEL 2026 | Esperança na Tormenta`
- `Blues Gospel em Português Que Fortalece a Fé`
- `ESSÊNCIA DO LOUVOR | SALMO 91 | BLUES CRISTÃO`

Esses sinais devem ser usados como padrões de demanda, não como cópia de título, letra, voz, melodia ou thumbnail.

## Top sinais do CSV gerado

1. `DEUS CONHECE SUA DOR` — 1h10, Country Gospel Blues, acalmar o coração — 1.800 views, 4,93 views/dia.
2. `SERTANEJO GOSPEL RAIZ 2026` — 10 louvores, country blues que tocam a alma — 1.800 views, 4,93 views/dia.
3. `DEUS VAI RENOVAR SUAS FORÇAS` — melhores louvores country gospel para acalmar — 1.400 views, 3,84 views/dia.
4. `LOUVORES QUE TOCAM O CORAÇÃO` — 1h10 sertanejo country gospel — 454 views, 1,24 views/dia.
5. `DEUS CONHECE SUA DOR` — 1 hora country gospel para acalmar — 365 views, 1,0 views/dia.

## Padrões que estão funcionando melhor em português BR

1. Promessa emocional direta nos primeiros 35–45 caracteres: `DEUS CONHECE SUA DOR`, `DEUS VAI RENOVAR SUAS FORÇAS`, `QUEM PRECISA DE FORÇA`.
2. Uso claro do vídeo: `acalmar o coração`, `renovar a fé`, `descansar`, `orar`, `recomeçar`.
3. Pacote/playlist acima de música isolada: `1 Hora`, `1H10`, `1H25`, `10 Louvores`, `Playlist Completa`.
4. Mistura de linguagem espiritual + dor humana: coração cansado, dor, força, paz profunda, promessa, Salmo 91.
5. Identidade musical explícita: Country Gospel, Country Blues Gospel, Sertanejo Gospel Raiz, Gospel Blues Brasileiro.

## Novas ideias originais para testar agora

### 1. DEUS VIU O QUE VOCÊ CHOROU EM SILÊNCIO
- Pacote: `DEUS VIU O QUE VOCÊ CHOROU EM SILÊNCIO 🙏 | 1 Hora de Country Blues Gospel Para Acalmar o Coração`
- Música âncora: `Lágrimas na Estrada de Barro`
- Hook: `O céu ouviu o choro que ninguém escutou.`
- Por que testar: combina dor invisível + promessa direta, padrão parecido com os melhores sinais de `dor/coração/acalmar`, mas com frase nova.

### 2. QUANDO A FORÇA ACABA, DEUS COMEÇA
- Pacote: `QUANDO A FORÇA ACABA, DEUS COMEÇA 🙏 | Louvores Country Gospel Para Renovar a Alma`
- Música âncora: `No Último Passo da Estrada`
- Hook: `Quando eu parei, Tua mão me carregou.`
- Por que testar: deriva do sinal `DEUS VAI RENOVAR SUAS FORÇAS`, mas mais dramático e clicável.

### 3. SALMO 91 NA ESTRADA ESCURA
- Pacote: `SALMO 91 NA ESTRADA ESCURA 🙏 | Blues Gospel Brasileiro de Proteção e Fé`
- Música âncora: `Debaixo das Tuas Asas`
- Hook: `Nem a noite me alcança quando Deus me guarda.`
- Por que testar: busca web mostrou sinal de `Salmo 91 / blues cristão`; encaixa muito bem em country blues sombrio com proteção espiritual.

### 4. A MANHÃ QUE DEUS GUARDOU PRA VOCÊ
- Pacote: `A MANHÃ QUE DEUS GUARDOU PRA VOCÊ 🌅 | Country Gospel Para Recomeçar com Fé`
- Música âncora: `Depois da Noite, a Graça`
- Hook: `A noite foi longa, mas Deus guardou a manhã.`
- Por que testar: sinal externo encontrou `A Manhã Que Deus Guardou pra Mim`; adaptar para promessa ao ouvinte aumenta identificação sem copiar.

### 5. ORAÇÃO DA MADRUGADA NA VARANDA
- Pacote: `ORAÇÃO DA MADRUGADA NA VARANDA 🙏 | 1 Hora de Country Blues Gospel Para Dormir em Paz`
- Música âncora: `Banco de Madeira e Bíblia Aberta`
- Hook: `Quando a casa dorme, o céu ainda me ouve.`
- Por que testar: o radar marcou `oração de madrugada` em 10/11 registros e `sono/playlist longa` em 7/11.

### 6. MINHA DOR NÃO VAI SER MEU FIM
- Pacote: `MINHA DOR NÃO VAI SER MEU FIM 🙏 | Country Blues Gospel Para Quem Precisa de Esperança`
- Música âncora: `O Louvor Que Nasceu da Ferida`
- Hook: `Deus transformou minha ferida em altar.`
- Por que testar: conversa com `MINHA DOR VIROU LOUVOR`, mas com promessa mais forte para título/thumbnail.

### 7. 10 LOUVORES PARA AGRADECER DEPOIS DA TEMPESTADE
- Pacote: `10 LOUVORES PARA AGRADECER DEPOIS DA TEMPESTADE 🌧️ | Country Gospel em Português`
- Música âncora: `Gratidão no Telhado de Zinco`
- Hook: `A chuva passou, mas a graça ficou.`
- Por que testar: busca web trouxe `10 Louvores Country para Agradecer`; gratidão pós-luta é um ângulo menos saturado que dor pura.

## Próximos testes recomendados

1. Publicar como playlist longa, não só single isolado: 45–75 minutos ou 10 faixas.
2. Usar promessa emocional no início do título, antes de `Country Gospel`.
3. Thumbnail com 2–4 palavras: `DEUS VIU`, `FORÇA ACABOU?`, `SALMO 91`, `NÃO É O FIM`.
4. Medir 24h/48h/72h: views/dia, comentários por 1.000 views, CTR/retention se houver Studio.
5. Repetir o padrão vencedor trocando apenas a promessa principal, para não confundir o teste.
