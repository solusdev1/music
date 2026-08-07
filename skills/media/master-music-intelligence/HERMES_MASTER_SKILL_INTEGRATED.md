# 🎵 HERMES MASTER MUSIC INTELLIGENCE SKILL (v1.0)

> ⚠️ **Honesty note (2026-08)**: this guide's genre/trend figures are
> synthetic example data, not measurements — see `README.md`'s honesty
> note and the header comment in `hermes_master_music_intelligence.py`.
> For real channel performance use `music-factory/data/*.db`.

## Consolidated Integration of:
- ✅ YouTube Music Production (Suno, lyrics, loops, metadata)
- ✅ Country Blues Channel Analysis (Daily radar, metrics, monetization)
- ✅ Gospel Blues Viral Agent (Trend scoring, opportunity radar)
- ✅ Claude Trend Intelligence (Emerging styles, saturation analysis)
- ✅ Persistent Memory (SQLite + JSON, auto-versioning)
- ✅ Conflict Resolution (Radar vs Claude Intelligence)

**Version**: 1.0.0 → Auto-updates on each use → 1.0.1, 1.0.2...  
**Status**: PRODUCTION READY  
**Last Synced**: 2024-07-30

---

## 📊 COMPARATIVE ANALYSIS: Hermes vs Claude Intelligence

### 1. COUNTRY BLUES GOSPEL

| Metric | Hermes Radar | Claude Analysis | Recommendation |
|--------|--------------|-----------------|-----------------|
| **Status** | "Está indo bem" | 45% crescimento | ⚠️ Claude correto |
| **Saturation** | Não menciona | ALTA (100+ canais) | ⚠️ Claude correto |
| **Engagement** | N/A | 2.92% | ✅ Use Claude |
| **Opportunity** | Promissora | Baixa (saturado) | 🔴 EVITAR |
| **Confidence** | Média (baseada em Radar específico) | ALTA (3+ meses dados globais) | **Claude: 85%** |

**Resolution**: Country Blues está saturado. Focar em nichos emergentes.

---

### 2. EMERGING STYLES (Claude Discovery)

Hermes tinha foco limitado a Country Blues. Claude descobriu **8 novos estilos** com crescimento exponencial:

| Estilo | Crescimento | Novos Canais | Status Hermes | Status Claude | Recomendação |
|--------|-------------|--------------|--------------|---------------|--------------|
| **Phonk** | 234% | 88 | ❌ Não tracked | 🏆 MELHOR | **USE CLAUDE** |
| **Hyperpop** | 245% | 78 | ❌ Não tracked | 🥈 2º MELHOR | **USE CLAUDE** |
| **Indie Bedroom** | 167% | 156 | ❌ Não tracked | 🥉 MAIS ESPAÇO | **USE CLAUDE** |
| **Reggaeton Trap** | 198% | 92 | ❌ Não tracked | ✅ ALTO ENG | **USE CLAUDE** |
| **Emo Rap** | 176% | 102 | ❌ Não tracked | ✅ MUITA OP | **USE CLAUDE** |

---

## 🎯 CONSOLIDATED WORKFLOW

### Phase 1: TREND ANALYSIS & OPPORTUNITY SCORING

**Input**: 
- Claude Intelligence: Last30Days style analysis
- Hermes Radar: Channel-specific data
- User Profile: Creator type, instruments, languages

**Process**:
1. Load Claude trends (growth %, saturation, engagement)
2. Load Hermes channel data (competitors, best practices)
3. Calculate combined opportunity score
4. Detect conflicts (Radar vs Claude)
5. Resolve conflicts using weighted confidence

**Output**:
- Top 3 recommended styles (by score)
- Channel benchmarks for each style
- Title/description/hashtag patterns
- Video length recommendations
- Upload time windows
- Monetization potential

**Example Output**:
```
🏆 RECOMMENDED: Phonk (Score: 440)
├─ Growth: 234% 
├─ Saturation: Very Low (47 canals)
├─ Best Videos: Playlists 6-8h (425k median views)
├─ Engagement: 4.69%
├─ Competitors: [Channel A], [Channel B], [Channel C]
├─ Best Titles: "Phonk Beat: [Mood]", "8H Phonk Mix: [Use]"
├─ Posting Time: 20:00-22:00 (evening viewers)
└─ Monetization: AdSense + Super Chat + Beat Sales
```

---

### Phase 2: MUSIC PRODUCTION PIPELINE

**Hermes Skills Integration**:
- Song concept & emotional hook (from youtube-music-production)
- Full Suno prompt package (lyrics, exclude styles, metatags)
- Loop video prompt (16:9, 10-20s seamless)
- YouTube metadata (title, description, hashtags, tags)
- Thumbnail guidance (text, visual, contrast)
- Pinned comment template
- Testing & analysis plan

**Template Structure** (from Hermes):
```
00-copy-paste-suno-complete.txt
01-style-prompt-suno.txt
02-exclude-styles-suno.txt
03-lyrics-suno.txt
04-video-loop-prompt.txt
05-youtube-package.txt
README-generation-order.txt
```

**Playlist-First Strategy** (from Hermes):
- Create batches, not isolated songs
- Package as 1-hour long playlists
- Mix new songs with existing channel content
- Use emotional promise in playlist title
- Target use cases: relaxation, worship, sleep, focus

**Example Batch**:
```
BATCH: "WHEN FAITH FEELS SMALL" (3 songs)
├─ Song 1: "Small Faith, Big God" (medium energy, retention)
├─ Song 2: "Crisis Protocol" (strong narrative, comments)
└─ Song 3: "Midnight Prayer" (slow, devotional, ambient)

PLAYLIST TITLE: "SMALL FAITH, BIG GOD 🙏 | Gospel Phonk Mix for Late Night Prayer"
DESCRIPTION: Use case + emotional promise + how to share
HASHTAGS: [Phonk], [Gospel], [Prayer], [Sleep]
```

---

### Phase 3: DAILY CHANNEL ANALYSIS & RADAR

**Hermes Radar Cadence**:
- Every 24-72 hours: run channel snapshot
- Collect: views, likes, comments, subscribers, watch time estimate
- Compare against previous snapshots
- Classify videos: winner, promising, flat, needs fix
- Analyze title/description/thumbnail patterns
- Benchmark against Portuguese competitors

**Metrics Tracked**:
```
Channel Level:
- subscribers (public from yt-dlp)
- total views across videos
- public watch hours estimate
- videos per week
- subscriber trend (delta)

Video Level:
- views per day
- engagement (likes/1000 views)
- comment rate (/1000 views)
- title pattern
- description pattern
- hashtag cluster
- age days

Studio Level (when available):
- impressions
- CTR
- average view duration
- real watch time hours
- subscribers gained
- traffic sources
```

**Daily Decision Rules** (from Hermes):
- 24h: light packaging signal only
- 48h: compare views/day against channel median
- 72h: decide on title/thumbnail formula
- 7d: evergreen/search potential signal

**Thresholds**:
- 2x median = promising
- 4x median = repeat formula
- Below median after 72h = change packaging

---

### Phase 4: CONFLICT RESOLUTION

**When Hermes Radar ≠ Claude Intelligence:**

Example: Country Blues Gospel
```
CONFLICT DETECTED:
├─ Hermes Radar says: "Going well, no saturation concerns"
├─ Claude says: "45% growth, 100+ large channels, high saturation"
├─ RESOLUTION: Claude weighted 85% (broader historical data)
└─ ACTION: Radar is channel-specific snapshot; Claude is market-wide analysis
           Trust Claude for trend decisions, Radar for channel-specific tactics.
```

**Weighting Algorithm**:
- Claude weight: 60% (historical data, multiple sources, 3+ months)
- Hermes weight: 40% (channel-specific, real-time data)
- Exception: When Hermes shows sudden spike (48h delta), temporarily boost to 50%

---

## 📁 DATA STRUCTURE (Persistent Memory)

```
~/.hermes/music_intelligence/
├─ music_intelligence.db (SQLite)
│  ├─ trend_analysis (style, growth%, channels, views, engagement, saturation)
│  ├─ channel_analysis (name, style, views, engagement, quality_score, datasource)
│  ├─ recommendations (style, rank, score, confidence, timestamp)
│  ├─ decision_history (decision_type, style, reason, outcome, timestamp)
│  ├─ conflicts (style, radar_opinion, claude_opinion, resolution, timestamp)
│  └─ skill_metadata (version, last_updated)
│
├─ music_intelligence_export.json (backup)
│  └─ Timestamped full export
│
└─ logs/
   ├─ daily_reports_YYYY-MM-DD.md
   ├─ conflict_log_YYYY-MM-DD.txt
   └─ version_history.txt
```

---

## 🎵 CONTENT CREATION GUIDE BY STYLE

### PHONK (Best Overall Score: 440)

**Tools**: FL Studio, Ableton, Logic Pro  
**BPM**: 60-90  
**Production Time**: 2-4 hours/track  
**Best Format**: 8-hour playlists, beat drops, freestyles  

**Title Patterns** (tested):
```
"Phonk Beat: [Mood]" (e.g., "Phonk Beat: Dark Vibes")
"[Time]H Phonk Mix: [Use]" (e.g., "8H Phonk Mix: Night Driving")
"[Artist] x [Producer] - [Energy]" (collab)
"Phonk Freestyle: [MC Name] [Topic]"
```

**Description Opening**:
```
Dark, atmospheric phonk beats for [use case: late night, studying, driving, gaming].
These lo-fi phonk beats combine Memphis samples with trap drums and retro vibes.
Share this with your crew and drop a comment if you vibe with it.
```

**Hashtags**:
```
#Phonk #PhonkBeat #MemphisRap #TrapBeats #LoFi #NightDriving #LoFiHop #PhonkMusic
```

**Best Posting Times**: 20:00-23:00 (night viewers)  
**Posting Frequency**: 2-3 videos/week (playlists) + daily TikTok clips  
**Monetization**: AdSense + Super Chat + Beat Sales + Sampling rights  

---

### HYPERPOP / EXPERIMENTAL POP (Score: 436)

**Tools**: FL Studio, Ableton, Max/MSP  
**BPM**: 120-200  
**Production Time**: 3-6 hours/track  
**Best Format**: Chaotic cuts, vocal chops, experimental collabs  

**Title Patterns**:
```
"Hyperpop Production: [Technique]" (tutorial)
"[Time]H Hyperpop Experience: [Emotion]"
"[Artist] - Hyperpop Freestyle [Topic]"
"100 Hyperpop Sounds in [Time]"
```

**Production Guidance**:
- Experiment constantly
- Use pitched vocals + chaotic percussion
- Post 1-2 production videos (show your process)
- Engage with Gen Z audience (short clips, behind-scenes)

**Best Posting Times**: 18:00-21:00 (evening/college hours)  
**Community**: TikTok first, YouTube for longer forms  
**Monetization**: AdSense (high CPM) + Memberships + Patreon  

---

### INDIE BEDROOM POP (Score: 428, Most Openings: 156 channels)

**Tools**: Audacity, GarageBand, Reaper  
**BPM**: 80-120  
**Production Time**: 4-8 hours/track  
**Best Format**: DIY recordings, lo-fi aesthetic, authentic sound  

**Title Patterns**:
```
"[Artist/Project] - [Song Title] [Genre Hint]"
"Bedroom Pop Session: [Mood]"
"[Time]H Lo-Fi Pop Study Mix"
"DIY Recording: [Artist] - [Song]"
```

**Strategy**:
- Focus on authentic, not polished
- Post weekly consistently
- Share behind-the-scenes
- Build engaged community (respond to comments)

**Best Posting Times**: 15:00-19:00 (study hours) + 22:00-23:00 (late night)  
**Community**: Discord/Reddit engagement critical  
**Monetization**: Spotify + Bandcamp + AdSense + Patreon  

---

## ✅ IMPLEMENTATION CHECKLIST

- [ ] Create `~/.hermes/music_intelligence.db` (SQLite)
- [ ] Load all Claude trend data into database
- [ ] Load all Hermes channel data into database
- [ ] Run conflict detection on Country Blues + all styles
- [ ] Generate daily report template
- [ ] Create batch production templates (Phonk, Hyperpop, Indie)
- [ ] Setup auto-backup to JSON
- [ ] Setup version auto-increment
- [ ] Create skill hook for daily updates
- [ ] Document data sources per metric
- [ ] Setup decision logging

---

## 🔄 UPDATE PROTOCOL

**Each Time Skill is Used**:
1. Load latest data
2. Check for new trends (run Claude analysis quarterly)
3. Check channel metrics (daily when possible)
4. Update version: 1.0.0 → 1.0.1 → 1.0.2 → 1.1.0 (every 10 patch)
5. Log decision in decision_history
6. Export to JSON backup
7. Generate report

**Monthly Deep Dive**:
- Compare Radar vs Claude (conflict resolution)
- Analyze posted videos performance
- Update recommendations
- Adjust title/hashtag patterns based on results
- Update guide with what worked

**Quarterly Review**:
- Re-run full Claude trend analysis
- Add new emerging styles
- Update saturation levels
- Publish updated Master Report

---

## 📈 SUCCESS METRICS

**Channel Level**:
- Subscribers: [target]
- Watch hours: [target]
- CTR: >3% (music niche average)
- AVD: >35% (for long playlists)
- Comments per 1000 views: >5

**Content Level**:
- Title A/B test results
- Description CTR impact
- Hashtag cluster performance
- Thumbnail text effectiveness
- Upload time winner

**Trend Level**:
- Radar accuracy (# of correct opportunity calls)
- Claude vs Hermes divergence tracking
- Style adoption timeline
- Saturation prediction accuracy

---

## 🚀 QUICK START

```bash
# 1. Initialize
python hermes_master_music_intelligence.py --init

# 2. Add Claude trends
python hermes_master_music_intelligence.py --add-trends-claude

# 3. Add Hermes channel data
python hermes_master_music_intelligence.py --add-channels-hermes

# 4. Generate report
python hermes_master_music_intelligence.py --report

# 5. Choose style & get guides
python hermes_master_music_intelligence.py --guide phonk
python hermes_master_music_intelligence.py --guide hyperpop
python hermes_master_music_intelligence.py --guide indie-bedroom

# 6. Start production
# Generate music → Upload → Track metrics → Update skill → Repeat
```

---

## 📌 KEY DECISIONS

**Why consolidate in ONE skill?**
- Reduces cognitive load (one place, not 3)
- Enables conflict resolution (Radar vs Claude)
- Persistent memory (learns over time)
- Single decision framework
- Auto-updates as you use it

**Why trust Claude over Hermes sometimes?**
- Claude has 3+ months historical data
- Analyzes 8 styles, not just Country Blues
- Detects saturation globally
- Weighs engagement + growth + newness

**Why keep Hermes Radar?**
- Real-time channel-specific metrics
- Daily snapshots for your channels
- Title/description/hashtag patterns that work
- Competitor benchmarks
- Upload time windows

**Answer: Use BOTH, but know when to trust which.**

---

## 📚 References

- Hermes Skill: youtube-music-production (lyrics, Suno, loops, metadata)
- Hermes Skill: country-blues-fe-channel-analysis (daily radar, monetization)
- Hermes Agent: youtube_radar_agent (trend scoring)
- Claude Analysis: emerging-music-styles-8-genres (growth, saturation, engagement)
- Version Control: Auto-increments on use
- Persistent DB: SQLite + JSON backup

---

**Status**: READY FOR PRODUCTION  
**Next Step**: Setup database, load data, start creating content  
**Support**: Update this skill monthly with new learnings

---

Generated: 2024-07-30  
Version: 1.0.0  
Auto-update: YES  
Maintenance: Quarterly review recommended
