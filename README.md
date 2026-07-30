# 🎵 Master Music Intelligence

**Consolidated Music Intelligence System for YouTube Creators**

A production-ready skill that combines music production expertise with comprehensive trend analysis, featuring persistent memory, auto-versioning, and intelligent conflict resolution.

## Quick Overview

```
✅ 8 Emerging Music Genres  - Phonk, Hyperpop, Indie Bedroom Pop, Reggaeton Trap, Emo Rap, Amapiano, Hyperpunk, Synthwave
✅ Saturation Detection     - Identifies emerging, growing, or saturated styles
✅ Conflict Resolution      - Intelligently weighs Radar vs Claude data
✅ Production Pipeline      - Complete Suno + YouTube metadata packages
✅ Daily Analytics          - Track views, engagement, patterns, benchmarks
✅ Persistent Memory        - SQLite database with auto-versioning
✅ Fed with Hermes Assets   - Country Blues e Fé radar history + Suno packages
✅ Continuous Learning      - Improves recommendations on each use
```

## Getting Started

```bash
# Initialize
python skills/media/master-music-intelligence/hermes_master_music_intelligence.py --init

# Load data bundled in the repository
python skills/media/master-music-intelligence/hermes_master_music_intelligence.py --add-trends-claude
python skills/media/master-music-intelligence/hermes_master_music_intelligence.py --add-channels-hermes
python skills/media/master-music-intelligence/hermes_master_music_intelligence.py --add-recommendations

# Get recommendations
python skills/media/master-music-intelligence/hermes_master_music_intelligence.py --report

# Get production guides
python skills/media/master-music-intelligence/hermes_master_music_intelligence.py --guide phonk
```

## The 8 Opportunities

| Genre | Growth | Saturation | Best For |
|-------|--------|-----------|----------|
| **Phonk** | 234% | Very Low | Rappers, beat producers |
| **Hyperpop** | 245% | Very Low | Electronic producers, Gen Z |
| **Indie Bedroom Pop** | 167% | Low | Singer-songwriters, lo-fi |
| **Reggaeton Trap** | 198% | Low | Rappers, Latin creators |
| **Emo Rap** | 176% | Low | Rappers, emotional artists |
| **Amapiano** | 212% | Emerging | Global producers |
| **Hyperpunk** | 223% | Low | Experimental musicians |
| **Synthwave** | 189% | Low | Retro-electronic, gaming |

## Files

```
skills/media/master-music-intelligence/
├── hermes_master_music_intelligence.py     # Main Python implementation
├── SKILL.md                                # Skill metadata
├── README.md                               # This overview
├── HERMES_MASTER_SKILL_INTEGRATED.md      # Complete technical guide
├── COMPARATIVO_E_CONSOLIDACAO.md          # Comparison & consolidation
├── ANALISE_ABRANGENTE_ESTILOS_MUSICAIS.md # 8 genres analysis
├── SUMARIO_EXECUTIVO.md                   # Executive summary
├── data/                                  # Seed SQLite + JSON export
├── references/youtube_radar_agent/         # Migrated radar agent and outputs
├── config/                                 # Configuration files
├── scripts/                                # Automation scripts
├── templates/                              # Production templates
└── references/                             # Reference materials
```

## Key Features

### Trend Analysis
Analyzes 8 emerging music genres across YouTube, TikTok, Reddit, and other platforms with growth metrics, saturation levels, and engagement data.

### Conflict Resolution
When real-time Radar data conflicts with historical Claude Analysis, uses intelligent weighted scoring (Claude 60%, Hermes 40%) to determine the best recommendation.

### Production Pipeline
Generates complete production packages including Suno style prompts, lyrics, video loop prompts, YouTube metadata (titles, descriptions, hashtags), thumbnail guidance, and pinned comments.

### Channel Analytics
Daily tracking of views, engagement rates, subscriber growth, posting frequency, title/description/hashtag patterns, and competitor benchmarking.

### Persistent Memory
SQLite database stores all trends, channels, recommendations, decisions, and conflicts. Auto-versioning system tracks improvements over time (1.0.0 → 1.0.1 → 1.1.0...).

## Migrated Hermes Feed

This repo was populated with the assets previously generated under the Hermes YouTube radar agent:

- 14 seeded trend records combining Claude/global intelligence and Gospel BR niches
- 90 radar channel/video records from ranked CSV snapshots
- 2026-07-17, 2026-07-22, and 2026-07-30 reports and JSONL raw data
- Country Blues e Fé input configuration
- Complete 5-song PT-BR Country Blues Gospel Suno package for 2026-07-30

Seed files now included:

- `skills/media/master-music-intelligence/data/music_intelligence_seed.db`
- `skills/media/master-music-intelligence/data/music_intelligence_seed.json`
- `skills/media/master-music-intelligence/references/youtube_radar_agent/`

## Workflow

**Daily**: Run analysis → Load Radar data → Resolve conflicts → Choose style  
**Weekly**: Generate prompts → Create videos → Prepare metadata  
**Monthly**: Deep dive on conflicts → Update recommendations → Publish report  
**Quarterly**: Re-run full analysis → Add new styles → Update saturation levels

## Documentation

- **HERMES_MASTER_SKILL_INTEGRATED.md** - Full technical guide (500+ lines)
- **COMPARATIVO_E_CONSOLIDACAO.md** - Strategic comparison & roadmap
- **ANALISE_ABRANGENTE_ESTILOS_MUSICAIS.md** - Detailed genre analysis
- **SUMARIO_EXECUTIVO.md** - Executive summary

## Status

✅ **Production Ready**  
✅ **Auto-updates** (version increments on each use)  
✅ **Persistent Memory** (SQLite + JSON backups)  
✅ **Continuous Learning** (improves over time)  
📅 **Maintenance**: Quarterly review recommended

## Version

**Current**: 1.1.0 (2026-07-30)  
**Auto-increments**: 1.0.0 → 1.0.1 → 1.0.2 → 1.1.0  
**Status**: Ready for production use

---

Generated by Claude Code Agent  
For questions, see HERMES_MASTER_SKILL_INTEGRATED.md
