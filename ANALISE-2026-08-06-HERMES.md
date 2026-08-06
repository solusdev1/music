# Análise 2026-08-06 — Projeto Hermes (music-factory + radar + skill)

**Data:** 2026-08-06 · **Branch:** `claude/hermes-project-analysis-6qy06j`
**Escopo:** nova auditoria completa do repositório, correções de código,
testes, e pesquisa de mercado externa (políticas do YouTube, Suno, nicho
gospel/country) para embasar recomendações.

---

## 1. Resumo executivo

O repositório contém **três subsistemas** com maturidade muito diferente:

| Subsistema | Estado real |
|---|---|
| `music-factory/` | ✅ Motor de produção real, testado agora (56 testes), rodando via systemd timer diário. Catálogo, 3 cooldowns anti-repetição independentes (faixa/tema/gancho), montagem de playlist, controle de qualidade de letra, oportunidade via cache VIDIQ, analytics reais de desempenho. |
| `youtube_music_ops/` | ✅ Radar externo real (TranscriptAPI + fallback yt-dlp automático), mas **isolado** — não alimenta o `music-factory`. |
| `skills/media/master-music-intelligence/` (a skill "Hermes") | ⚠️ Mistura dados reais ingeridos com uma tabela de "8 gêneros emergentes" **inventada** (Phonk 234%, Hyperpop 245%, etc.) que nunca correspondeu a nenhum canal operado e contradizia o próprio resultado medido do projeto. **Corrigido nesta sessão** — ver §3. |

**O achado mais importante desta rodada não é de código: é de política.** O
YouTube endureceu em 2026 as regras contra "inauthentic content" (nome novo
para o que era "repetitious content"), com sistema de 3 avisos até remoção
do Programa de Parceiros — e o alvo declarado são exatamente canais
"AI slop": templates em massa, sem curadoria humana, sem visual original.
Isso value diretamente a estratégia atual (curadoria humana forte, letras
não repetidas, identidade cultural por canal) e expõe um risco concreto
(nenhuma etapa de vídeo/visual automatizada nem documentada). Ver §4.

---

## 2. O que foi corrigido nesta sessão (código)

1. **Bug de crash reproduzível corrigido** — `generate_report()` em
   `hermes_master_music_intelligence.py` fazia `f"{None:.2f}"` quando uma
   tendência não tinha `avg_engagement`, levantando `TypeError`. Esse bug já
   estava documentado como conhecido em `PROPOSTA_V2_MUSIC_FACTORY.md` desde
   2026-07-30 e nunca tinha sido corrigido. Agora há um helper `_fmt_num()`
   que degrada para `"—"` em vez de quebrar, aplicado também aos outros
   pontos com o mesmo padrão de risco (conflitos, recomendações, engajamento
   de canal).
2. **Dado sintético deixou de se passar por inteligência real** — a tabela
   `CLAUDE_TRENDS` (8 gêneros, taxas de crescimento inventadas),
   `_resolve_conflict()` e `add_default_recommendations()` agora têm
   comentários e textos explícitos marcando os números como ilustrativos,
   não medidos. O caso mais grave: o código dizia literalmente "Claude está
   correto — Country Blues Gospel está saturado, 45% de crescimento,
   confiança 85%" — quando o dado real do próprio projeto (`ANALISE-2026-07-30.md`,
   `music-factory/data/*.db`) mostra Country Blues e Fé como o **canal de
   melhor desempenho medido**. Isso foi corrigido no código e em 6 documentos
   Markdown da skill (`README.md`, `SKILL.md`,
   `HERMES_MASTER_SKILL_INTEGRATED.md`, `COMPARATIVO_E_CONSOLIDACAO.md`,
   `ANALISE_ABRANGENTE_ESTILOS_MUSICAIS.md`, `SUMARIO_EXECUTIVO.md`) com uma
   nota de honestidade no topo de cada um. Motivo: se uma sessão futura do
   Hermes consultar essa skill para decidir estratégia, o dado sintético
   não pode mais ser confundido com medição real.
3. **Referência morta de CLI corrigida** — `core/opportunity.py` instruía o
   operador a rodar `cli.py collect-opportunity`, comando que **não existe**
   em `cli.py`. Trocado pela sequência real (`vidiq-ingest` + `set-theme-score`).
4. **Suite de testes criada do zero** — `music-factory/tests/` (56 testes,
   pytest), cobrindo `catalog`, `playlist`, `learn`, `quality`, `opportunity`,
   `brief`, `vidiq`. Antes desta sessão havia **zero testes automatizados**
   em ~2.600 linhas de lógica que roda todos os dias sem supervisão via
   systemd timer — qualquer edição futura em `catalog.py`/`playlist.py`
   podia quebrar produção em silêncio.
5. **CI adicionado** — `.github/workflows/music-factory-tests.yml` roda a
   suite a cada push/PR que toque `music-factory/`.
6. **Onboarding do radar externo documentado** — `youtube_music_ops/` não
   tinha README nem `.env.example`; a chave `TRANSCRIPT_API_KEY` só existia
   como conhecimento tácito (caminho fixo `/root/.hermes/.env`). Adicionado
   `README.md` e `.env.example` explicando o fallback automático para
   yt-dlp quando a chave falta.
7. **README raiz reescrito** — antes documentava só a skill (incluindo a
   tabela sintética) e nem mencionava `music-factory`, que é o sistema real
   em produção. Agora aponta primeiro para `music-factory/` e resume o
   estado real dos três subsistemas.
8. **Higiene de repositório** — arquivos `.pyc` de `__pycache__` estavam
   versionados (apesar do `.gitignore` já excluir o padrão); removidos do
   índice do git.

Todas as mudanças foram validadas: suite completa (`pytest -q` → 56 passed),
`cli.py daily-brief` rodado ponta a ponta contra um banco limpo, e o script
da skill Hermes rodado com `--report` para confirmar que o crash não ocorre
mais.

---

## 3. O que ficou como está (e por quê)

- **`references/youtube_radar_agent/scripts/radar_gospel_blues_viral.py`**
  tem um bug real (`parse_upload_date()` retorna silenciosamente 365 dias
  quando a data não é parseável, inflando/corrompendo `views_per_day` e
  `viral_score` sem sinalizar isso na saída). Não foi corrigido porque é um
  script de referência migrado/arquivado — o radar ativo hoje é
  `youtube_music_ops/`, não este. Risco baixo por estar fora do caminho de
  produção; registrado aqui para não virar surpresa se alguém reativar esse
  script.
- **Nenhuma ponte de código entre `youtube_music_ops` e `music-factory`** —
  avaliei e decidi não construir uma automaticamente: os "nichos" que o
  radar externo explora (dark deep house, jazz lounge, afrobeat, etc.) são
  candidatos a **canais novos**, não temas dentro dos canais gospel
  existentes — misturar isso no fluxo `radar-add`/`radar-approve` do
  `music-factory` (que é para temas dentro de um nicho já operado) criaria
  confusão de modelo de dados. A decisão de abrir um canal novo continua
  sendo do operador; documentei o gap no README do `youtube_music_ops`.
- **Catálogo do `music-factory/data/radar.db` tem só 2 dos 6 canais com
  faixas** — não é bug: esse banco no repo é de desenvolvimento/exemplo; o
  systemd timer usa `~/.music-factory/factory.db` (fora do repo).

---

## 4. Pesquisa de mercado (2026) e implicações

### 4.1 Política do YouTube contra "inauthentic content" (antiga "repetitious content")

Em julho de 2026 o YouTube renomeou e ampliou a política que cobre "AI
slop": qualquer canal construído sobre templates em massa, clipes
reciclados, slideshows sem narrativa, ou roteiros lidos literalmente de
fonte externa. Em janeiro de 2026, 16 canais grandes (4,7 bilhões de views,
US$10M/ano combinados) saíram do Programa de Parceiros. O sistema é de 3
avisos: aviso → suspensão de 90 dias → remoção permanente.
[TechCrunch — YouTube clarifies policies around AI slop](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/) ·
[ScaleLab — crackdown 2026](https://scalelab.com/en/why-youtube-is-cracking-down-on-ai-generated-content-in-2026)

**Especificamente para música gerada por IA**: "dumps" crus de
Suno/Udio estão mortos; canais precisam de visual original, curadoria
humana visível, e nicho específico para continuar monetizando. RPM
realista em 2026 para nichos premium (sono, lo-fi, cinematic, comentário):
US$3–8.
[OutlierKit — AI-Generated Music on YouTube: Monetization 2026](https://outlierkit.com/resources/ai-generated-music-youtube-monetization-2026/)

**Como isso se aplica aqui:** a estratégia atual do `music-factory` já
acerta boa parte disso por acidente/disciplina prévia — cada lote tem
ângulo narrativo próprio por faixa (`songbrief.py`), identidade cultural por
país (`cultura.referencias`/`proibido` em cada `niches/*.json`), anti-
repetição de vocabulário/rima (`quality.py`), e já inclui o aviso "Música
criada com auxílio de inteligência artificial" nas descrições — ou seja,
divulgação de conteúdo sintético já embutida. **O que falta e é o maior
risco real**: não existe, em nenhum lugar do repositório, uma etapa de
produção de **vídeo/visual** (a pasta `entregas/` confirma isso — só letra e
metadados de texto, o vídeo final é 100% manual e não documentado aqui).
Sem visual original consistente, o "raw dump" continua sendo o formato de
entrega de fato, mesmo com áudio e letra bem cuidados por dentro. Recomendo
que a próxima ação de produto — fora do escopo desta sessão de código — seja
documentar (ou versionar, se for scriptado) o pipeline de vídeo, para que a
disciplina anti-repetição que já existe para letra/tema também cubra o
visual.

### 4.2 Nicho gospel/country: crescimento real, não hype

Busca por "gospel worship songs" teve alta recorde entre final de 2025 e
início de 2026; artistas country e gospel estão cruzando gêneros
ativamente (ex.: Brandon Lake com atos country).
[Voz — Christian/Gospel Music rises](https://voz.us/en/entertainment/250727/27222/matter-of-faith-christian-gospel-music-rises-as-streaming-growth-slows.html)
Isso reforça — com dado independente e real — a escolha de nicho do
projeto, ao contrário do que a tabela sintética da skill Hermes chegou a
sugerir (ver §2).

### 4.3 Suno ainda não tem API pública self-serve

Em julho de 2026 o CPO da Suno confirmou que uma API para desenvolvedores
está em exploração, restrita a parceiros selecionados, sem data pública.
[gptproto — Is There an Official API Yet?](https://gptproto.com/blog/suno-api)
**Implicação prática**: a etapa manual de "colar no Suno" no
`music-factory` não é uma lacuna a ser corrigida agora — é a única opção
disponível hoje sem depender de agregadores de terceiros não oficiais (risco
de ToS). Não recomendo investir em automação de geração de áudio até a Suno
abrir API oficial.

### 4.4 Automação de pipeline (referência de mercado)

Existem pipelines open-source (n8n + Suno via agregador + GPT + Runway/
Creatomate) que automatizam roteiro→música→vídeo→publicação ponta a ponta.
[aimlapi — Suno API Review 2026](https://aimlapi.com/blog/suno-api-review)
Não recomendo copiar esse modelo aqui: ele empurra exatamente para o "raw
dump" que a política de 2026 está mirando (§4.1). O diferencial real deste
projeto é a curadoria humana e a disciplina anti-repetição já construída —
automação total do vídeo removeria isso.

---

## 5. Recomendações priorizadas

**Curto prazo (esta semana), baixo custo:**
1. Rodar a suite de testes nova (`cd music-factory && python -m pytest`)
   antes de qualquer alteração futura em `core/` — é a rede de segurança que
   faltava.
2. Ler as notas de honestidade adicionadas na skill Hermes antes de usá-la
   para qualquer decisão de canal/gênero.

**Médio prazo (próximas semanas):**
3. Documentar (mesmo que fora do repo, num arquivo próprio) a etapa atual
   de produção de vídeo/thumbnail real usada para publicar — hoje ela não
   existe em código nem em texto, e é o ponto mais exposto à política de
   "inauthentic content" de 2026.
4. Diagnosticar e decidir o destino de Estrada da Fé (já sinalizado como
   candidato a abandono em `ANALISE-2026-07-30.md`) usando
   `cli.py health` com dados atualizados.

**Mais adiante:**
5. Se algum nicho prospectado pelo `youtube_music_ops` (ex.: Christian Sleep
   Ambient, que conecta com o canal instrumental já existente,
   `peaceful_deep_sleep`) virar decisão de canal novo, criar o
   `niches/*.json` correspondente manualmente — não há automação nem deveria
   haver, é decisão estratégica do operador.
6. Reavaliar a API da Suno periodicamente — se abrir para o público, a
   etapa manual de geração de áudio passa a ser automatizável com baixo
   risco.

---

## 6. Arquivos alterados nesta sessão

- `skills/media/master-music-intelligence/hermes_master_music_intelligence.py` (bugfix + honestidade)
- `skills/media/master-music-intelligence/{README,SKILL,HERMES_MASTER_SKILL_INTEGRATED,COMPARATIVO_E_CONSOLIDACAO,ANALISE_ABRANGENTE_ESTILOS_MUSICAIS,SUMARIO_EXECUTIVO}.md` (notas de honestidade)
- `music-factory/core/opportunity.py` (referência de CLI corrigida)
- `music-factory/tests/` (novo — 56 testes)
- `music-factory/pytest.ini`, `music-factory/requirements-dev.txt` (novo)
- `.github/workflows/music-factory-tests.yml` (novo — CI)
- `youtube_music_ops/README.md`, `youtube_music_ops/.env.example` (novo)
- `README.md` (reescrito)
- `__pycache__/*.pyc` removidos do controle de versão
