# Music Factory

**Foco: criação de músicas para os canais.** Tudo o mais — playlist, métricas,
saúde de canal, migração — existe como comando avulso, fora do caminho diário.
Renderização e upload são manuais.

Zero dependências externas: Python 3 puro.

---

## O que roda todo dia

Só duas coisas:

1. **A pauta de criação** — um lote de músicas por canal, cada faixa
   especificada individualmente
2. **O radar** — ideias novas de tema, porque o banco se esgota com 5
   músicas/dia

```bash
python3 cli.py daily-brief --niche country_blues_fe   # o systemd chama isto
python3 cli.py radar --niche country_blues_fe
```

## Por que cada faixa é especificada individualmente

A primeira versão gerava **um prompt pedindo "5 letras no mesmo tema"**, com o
mesmo style prompt para todas. Cinco músicas assim saem como cinco variações
da mesma: iguais na letra e iguais no som.

Agora cada faixa do lote recebe:

| Dimensão | Por quê |
|---|---|
| **ângulo narrativo próprio** | de quem é a história — "quem está no meio da luta agora" ≠ "quem já atravessou e olha pra trás" |
| **cor sonora própria** | senão o Suno devolve a mesma faixa 5x |
| **papel no lote** | retenção, narrativa, oração, renovação, descanso |
| **o que está gasto** | imagens e rimas já saturadas no acervo |

Os ângulos rotacionam por uso histórico: o lote de amanhã não repete o de hoje.

### `style_base` separado da instrumentação

Concatenar a variação ao style prompt completo criava **contradição** — a base
afirmava "slide guitar, coral final" enquanto a variação pedia "quase acústico,
sem coral". O Suno responde mal a prompt que se contradiz.

Por isso `style_base` carrega só a identidade que nunca muda (gênero, idioma,
caráter da gravação) e `variacoes_estilo` carrega a instrumentação:

```
FAIXA 1: <base>, barítono rouco, slide em primeiro plano, bateria com vassourinha
FAIXA 3: <base>, quase acústico: violão e voz, slide só no último refrão, sem bateria
FAIXA 5: <base>, muito lento e íntimo, voz sussurrada, cordas ao fundo, sem percussão
```

## O que a pauta entrega

```
out/2026-07-31/country_blues_fe/
├── 00-PAUTA-DO-DIA.md          tema do lote + tabela das faixas
├── 01-PROMPT-LETRAS.md         as N faixas especificadas uma a uma
└── musicas/
    ├── 01-retencao/
    │   ├── 00-BRIEFING.txt              ângulo, papel, cor sonora, mood
    │   ├── 01-style-prompt-suno.txt     ← pronto, com a variação da faixa
    │   ├── 02-exclude-styles-suno.txt   ← pronto
    │   └── 03-lyrics-suno.txt           ← cole a letra aqui
    └── 02-narrativa/ …
```

Style e exclude saem prontos porque são determinísticos. A letra é do modelo —
o sistema entrega o prompt em vez de fingir que gera letra boa em template.

Para o pacote de playlist (título, descrição, hashtags, chapters), passe
`--com-playlist`. Fora do caminho diário por decisão.

## VIDIQ — demanda real por keyword

```bash
python3 cli.py vidiq --niche country_blues_fe
python3 cli.py vidiq-ingest --niche X --file coleta.json --tipo keywords --pais BR
```

Cada consulta ao VIDIQ custa 5 créditos, então a coleta é **semanal** e vai
para cache; a pauta diária lê só o banco. O módulo não chama o MCP — recebe o
JSON e normaliza, o que o mantém testável sem rede e sem gastar crédito.

O relatório separa **espaço aberto** (concorrência ≤30 com ≥3k buscas/mês) de
**maior volume**, porque são decisões diferentes: uma é onde dá para entrar,
a outra é onde está o público.

Coleta de 2026-07-30 em `data/vidiq/` e `data/radar.db`.

## Radar — ideias novas de música

```bash
python3 cli.py radar-add --niche country_blues_fe \
    --ideia "Lamentações 3:23 — as misericórdias se renovam a cada manhã" --score 88
python3 cli.py radar --niche country_blues_fe
python3 cli.py radar-approve --niche country_blues_fe --ideia "..."
```

Avisa quando o banco de temas cai abaixo de 30 — com 5 músicas/dia e descanso
de 60 dias, abaixo disso o rodízio esgota e passa a reaproveitar tema antigo.

---

## Uso

### Backfill do acervo existente (uma vez)

```bash
python3 cli.py import-acervo --niche country_blues_fe \
  --folder ../skills/media/master-music-intelligence/references/youtube_radar_agent/generated_songs/country_blues_ptbr_5_songs_new_prompt_2026-07-30
```

### Ciclo diário

```bash
# 1. pauta do dia (é o que o systemd chama)
python3 cli.py daily-brief --niche country_blues_fe

# 2. cole out/AAAA-MM-DD/<nicho>/01-PROMPT-PARA-CLAUDE-LETRAS.md no Claude
#    → recebe as 5 letras do tema escolhido

# 3. registre cada letra
python3 cli.py add-song --niche country_blues_fe \
  --title "Deus Ouviu Seu Choro" --mood calm --lyrics letras/01.txt

# 4. gere no Suno, baixe o áudio e registre a duração REAL
python3 cli.py set-audio --slug country_blues_fe-deus-ouviu-seu-choro \
  --file /audio/01.mp3 --duration 265

# 5. remonte a playlist com timestamps corretos
python3 cli.py build-playlist --niche country_blues_fe --save minha-playlist
```

### Inspeção

```bash
python3 cli.py status                      # visão geral por nicho
python3 cli.py catalog --niche country_blues_fe
```

---

## Saída da pauta diária

```
out/2026-07-31/country_blues_fe/
├── 00-RESUMO-DO-DIA.md              tema, playlist planejada, avisos, próximos passos
├── 01-PROMPT-PARA-CLAUDE-LETRAS.md  pronto para colar → gera as 5 letras
└── playlist/
    ├── titulo-variacoes.txt         3 variações para A/B (ganchos não repetidos)
    ├── descricao.txt                com tracklist e AI disclosure
    ├── tracklist-chapters.txt       timestamps para os chapters
    ├── hashtags.txt
    ├── tags-youtube.txt
    ├── comentario-fixado.txt
    └── prompt-thumbnail.txt
```

**Divisão de responsabilidade:** o Python cuida de estado e montagem (o que já
foi usado, o que entra hoje, em que ordem, com que timestamp). A escrita das
letras continua sendo do modelo — o job entrega o prompt pronto em vez de
fingir que gera letra boa em template.

---

## Instalação no VPS

```bash
sudo cp -r music-factory /opt/
sudo mkdir -p /var/music-factory
sudo cp systemd/music-factory-brief.* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now music-factory-brief.timer
systemctl list-timers music-factory-brief.timer   # confirmar
```

Ajuste `User=` no `.service` e as variáveis `MUSIC_FACTORY_*` conforme o VPS.
Para usar cron em vez de systemd:

```cron
0 6 * * * /usr/bin/env bash /opt/music-factory/jobs/run_all_niches.sh
```

---

## Os 6 canais

| Canal | Idioma | Subgênero | Formato | Status |
|---|---|---|---|---|
| Country Blues e Fé | pt-BR | country/sertanejo raiz | canção | **244 v/dia** |
| Estrada da Fé | pt-BR | gospel blues soul urbano | canção | 21 v/dia |
| El Camino de la Fé | es-419 | gospel blues | canção | 22 v/dia |
| Blues & Praises | en-US | gospel blues de igreja | canção | novo |
| Southern Country Blues Gospel | en-US | country gospel Appalachian | canção | novo |
| Peaceful Deep Sleep Music | en-US | ambient/healing | **instrumental** | novo |

### O par mais perigoso são os dois em português

`country_blues_fe` e `estrada_da_fe` são o mesmo idioma, país e público —
risco de colisão maior que qualquer par entre idiomas. Separados por
subgênero e por cenário:

- **Country Blues e Fé** → campo: sertão, roça, viola caipira, poeira da estrada
- **Estrada da Fé** → cidade: turno, ônibus, asfalto, hospital de madrugada

Cada um proíbe o repertório do outro, e o `exclude_styles` do Estrada da Fé
lista `country, sertanejo, viola caipira` para o Suno não aproximar os dois.

### Como os canais ficam diferentes entre si

Três mecanismos, porque só traduzir não resolve:

**1. Duas janelas de descanso de tema.** Dentro do canal, 60 dias (o mesmo
público voltaria a ver o mesmo assunto). Entre canais irmãos, 14 dias — basta
não saírem na mesma semana. Com janela única, 4 canais consumindo 1 tema/dia
esgotariam qualquer banco em dias.

**2. Bloco de cultura por canal.** Cada config declara o repertório de imagens
nativas e o que é **transposição proibida**. Os dois canais em inglês não
compartilham nenhuma imagem:

- *Blues & Praises* → revival tent, church pew, choir loft, river baptism
- *Southern* → Appalachian hollow, tobacco barn, coal town, grandmother's hymnbook

E cada um proíbe explicitamente o repertório do outro. O PT proíbe "front
porch"; o ES proíbe "sertão" e "front porch"; o Southern proíbe "church pew".

**3. Aviso de canal irmão no prompt.** Quando o tema pode ter saído noutro
idioma, o prompt manda mudar ângulo narrativo, cenário e personagem —
"mesma verdade, outra história" — em vez de traduzir.

A identidade sonora também separa: *Blues & Praises* é órgão Hammond de
igreja; *Southern* é dobro, pedal steel e fiddle de varanda, com
`Hammond organ church gospel` na lista de exclude.

### Canal instrumental

`peaceful_deep_sleep` usa `"formato": "instrumental"`. O prompt muda sozinho:
pede **direção sonora** (instrumentação, andamento, arco dinâmico) em vez de
letra, o banco de temas é sensorial em vez de bíblico, as faixas são longas
(15 min) e há regra explícita de **nunca prometer efeito médico**.

## Novo nicho

Copie `niches/country_blues_fe.json` e ajuste. Campos que importam:

- `ganchos` / `beneficios` — alimentam a fórmula de título (rotacionados por uso)
- `temas` — banco de temas do dia. **Mantenha ≥ 30 itens**: com poucos temas o
  rodízio esgota e o sistema passa a reaproveitar o mais antigo, avisando.
- `cooldown_*_dias` — janelas de descanso de faixa, tema e gancho
- `style_prompt` / `exclude_styles` — idênticos aos que já funcionam no Suno

O `daily-brief` roda para todo `.json` em `niches/`, sem alterar código.

---

## Testado

Todos os cenários abaixo foram executados, incluindo os de borda:

- catálogo vazio → erro com instrução, sem stack trace
- import do acervo real (5 músicas) → idempotente por slug
- acervo sem áudio → 4 avisos precisos, playlist ainda sai
- dia 2 → tema e gancho rotacionam, abertura pega a de maior VPH
- cooldown 21d → 0 elegíveis; 0d → 5 elegíveis
- banco de temas esgotado → rodízio justo do menos-recentemente-usado
- `mood` inválido → rejeitado com a lista de valores válidos
- `run_all_niches.sh` → ponta a ponta, exit 0, 9 arquivos entregues

---

## Qualidade — o que só é possível tendo o catálogo

Com 5 músicas/dia, a ameaça à qualidade não é a letra isolada sair ruim: é o
acervo inteiro convergir para as mesmas imagens e as mesmas rimas. Nas 5
primeiras letras do canal, **"cheiro" aparece em 5 de 5** e as terminações
`-nho` e `-rar` em 4 de 5.

```bash
python3 cli.py quality --niche country_blues_fe
```

Detecta:
- **Imagens saturadas** — por presença por música, não contagem bruta (uma
  palavra 20x numa letra é estilo; em 8 de 10 letras é vício)
- **Terminações de verso viciadas** — rimas que fecham todo verso igual
- **Colisão de títulos** — músicas que canibalizam a busca uma da outra

Três filtros evitam ruído: `palavras_protegidas` do nicho (num canal gospel,
repetir "Deus" é o assunto, não defeito), stopwords com verbos conjugados
("quis", "veio" são gramática, não cenário) e mínimo de 3 músicas para entrar
na lista (2 de 5 é coincidência). Abaixo de 8 letras o relatório se declara
indicativo em vez de diagnóstico.

**O resultado entra sozinho no prompt do dia**, como bloco de anti-repetição.

## Oportunidade — tema por demanda, não por rodízio

A conta VIDIQ tem teto de **150 créditos/semana** e cada consulta custa 5 —
cerca de 30 consultas semanais no total. Um job diário que consultasse a API
queimaria a cota em dois dias.

Por isso a coleta é **semanal e vai para cache**; a pauta diária lê só o cache
e **nunca gasta crédito**. Sem cache válido (>14 dias ou vazio), o sistema cai
no rodízio simples e **diz isso em voz alta** em vez de fingir que tem dado.

```bash
python3 cli.py opportunity --niche country_blues_fe        # ranking atual
python3 cli.py set-theme-score --niche country_blues_fe \
    --theme "Salmo 91 — proteção na estrada escura" --score 87
```

O tema do dia passa a ser **o de maior score que esteja fora do descanso** —
demanda e anti-repetição combinadas. O `00-RESUMO-DO-DIA.md` sempre declara
qual critério foi usado.

## Aprendizado com desempenho real

```bash
python3 cli.py add-published --niche country_blues_fe \
    --title "DEUS CONHECE SUA DOR 🙏 1H55 | Os Melhores Louvores" \
    --date 2026-07-15 --views 8207 --comments 7 --duration "1:54:49"

python3 cli.py learn --niche country_blues_fe --sync-vph
```

Ordena por **views/dia** (normaliza a idade do vídeo) e detecta ganchos
reaproveitados cedo demais. Carregado com os dados reais dos canais, o
primeiro relatório já mostrou o padrão:

```
⚠️  GANCHOS REAPROVEITADOS CEDO DEMAIS
  «DEUS CONHECE SUA DOR» — 1d de intervalo: 547 → 86 v/dia (16% do primeiro)
  «FÉ QUE ACALMA A ALMA» — 3d de intervalo:  40 → 21 v/dia (52% do primeiro)
```

Dois canais, mesmo padrão: repetir o gancho em poucos dias derruba o segundo
vídeo. É o que o `cooldown_gancho_dias` (30) impede.

`--sync-vph` copia views/dia para o catálogo, fazendo a regra "abrir a
playlist pela faixa de maior VPH" usar desempenho real em vez de zero.

## Shorts — fora da operação

**Decisão do operador: não postar mais Shorts.** `shorts_policy` está em
`"nenhum"` nos 6 canais e a pauta diária não cobra cadência.

O rastreio continua no código (`cadence`, `--formato short`) porque canais
antigos têm Shorts no histórico e eles não podem contaminar a medição dos
longos — a colisão de gancho, por exemplo, é calculada **só entre longos**.

## Abandonar canal e recomeçar

Estratégia do operador: canal que não entrega é abandonado, cria-se outro.
O sistema torna essa decisão **datada e comparável**.

```bash
python3 cli.py health --janela 60            # todos os canais
python3 cli.py migrate-tracks --origem estrada_da_fe --destino canal_novo
```

```
  canal                          vídeos  idade  s/ postar vs melhor    veredito
  camino_de_la_fe                     3    31d        20d      100%   EM JANELA
  country_blues_fe                    5    15d         6d      100%   EM JANELA
  estrada_da_fe                       5    33d        12d       47%      ABAIXO

  COMPARAÇÃO POR FAIXA DE IDADE (v/dia mediano)
    8-15d    country_blues_fe: 159 · estrada_da_fe: 22
    16-30d   camino_de_la_fe: 45 · estrada_da_fe: 21
```

### Duas correções metodológicas que mudam a leitura

**1. views/dia decai com a idade do vídeo.** Views são front-loaded, então um
vídeo de 6 dias sempre parece melhor que um de 33. Toda comparação entre
canais é feita **dentro da mesma faixa de idade** — comparar direto inflava a
diferença entre canais em cerca de 40%.

**2. Um snapshot único não mede tendência.** A primeira versão deste relatório
dizia "Estrada da Fé: CRESCENDO" — o oposto do observado — porque comparava
vídeos antigos (v/dia já decaído) com recentes. Qualquer canal ativo pareceria
crescer. O veredito agora só usa o que é apurável de um retrato: dias sem
postar e desempenho relativo por faixa. Para tendência real é preciso série
temporal: rode `add-published` periodicamente sobre os mesmos vídeos.

### O acervo sobrevive ao canal

`migrate-tracks` copia as faixas com áudio pronto para o canal novo. O canal
antigo fica intacto para consulta, e as faixas chegam **sem histórico de uso**
— no canal novo o público é outro, então o descanso de 21 dias não se herda e
elas já podem entrar na primeira playlist.

É o que torna a estratégia de troca barata: o canal morre, o catálogo não.

## Próximas fases

| Fase | Entrega |
|---|---|
| 3 | Coleta automática de oportunidade (VIDIQ semanal dentro da cota) |
| 4 | Ingestão automática de métricas (yt-dlp/API) alimentando `learn` |

Renderização de vídeo e upload **não estão no roadmap** — feitos manualmente.
