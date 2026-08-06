---
name: master-music-intelligence
description: "Music intelligence skill: real ingested YouTube radar data + a SYNTHETIC example trend table (8 genres, not measured — see honesty note), conflict-resolution demo, production-pipeline templates, and channel-analytics storage. Prefer music-factory/data/*.db for real, current channel performance."
version: 1.1.0
author: Claude Code Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [youtube, music, trends, analytics, suno, production, intelligence, ai-generated]
    related_skills: [youtube-music-production, country-blues-fe-channel-analysis, dark-music-youtube-niche-strategy]
    integration: consolidated
---

# Master Music Intelligence Skill (v1.1)

> ⚠️ **Honesty note (2026-08):** the "8 Emerging Genres" table and default
> recommendations in this skill are **synthetic example data**, not measured
> trends — see the header comment in `hermes_master_music_intelligence.py`
> and the caveat in `README.md`. "Auto-updates" below refers to code that
> exists (`auto_update()`) but is **never called** from any CLI path — the
> version number is bumped by hand. For real channel performance, use
> `music-factory/data/*.db`, not this file's genre table.

**Status**: Real ingestion (`--add-channels-hermes`) + synthetic demo data (`--add-trends-claude`, `--add-recommendations`) — see note above  
**Auto-updates**: code exists, not wired to any CLI path (see note above)  
**Persistent Memory**: SQLite + JSON backups

---

## Overview

Consolidated integration of YouTube music production, channel analysis, trend intelligence, and persistent memory with auto-versioning.

- ✅ **YouTube Music Production** (Suno prompts, lyrics, loops, metadata)
- ✅ **Country Blues Channel Analysis** (Daily radar, metrics, monetization)
- ✅ **Gospel Blues Viral Agent** (Trend scoring, opportunity radar)
- ✅ **Claude Trend Intelligence** (8 emerging genres, saturation analysis)
- ✅ **Conflict Resolution** (Radar vs Claude weighted scoring)
- ✅ **Persistent Memory** (SQLite database + auto-versioning)
- ✅ **Seed Alimentado** (radar histórico Country Blues e Fé + pacotes Suno 2026-07-30)

---

## Quick Start

```bash
# 1. Initialize database
python hermes_master_music_intelligence.py --init

# 2. Load trend data bundled in this repo
python hermes_master_music_intelligence.py --add-trends-claude

# 3. Load Hermes/YouTube radar snapshots copied from the previous repo
python hermes_master_music_intelligence.py --add-channels-hermes

# 4. Load default recommendations and generate report
python hermes_master_music_intelligence.py --add-recommendations --report

# 5. Get production guides
python hermes_master_music_intelligence.py --guide phonk
```

---

## 8 Emerging Genres (⚠️ synthetic example data, not measured — see note above)

| Genre | Growth | Saturation | Score |
|-------|--------|-----------|-------|
| **Phonk** | 234% | Very Low | 440 |
| **Hyperpop** | 245% | Very Low | 436 |
| **Indie Bedroom Pop** | 167% | Low | 428 |
| **Reggaeton Trap** | 198% | Low | 425 |
| **Emo Rap** | 176% | Low | 420 |
| **Amapiano** | 212% | Emerging | 418 |
| **Hyperpunk** | 223% | Low | 415 |
| **Synthwave** | 189% | Low | 412 |

---

## Core Features

### 1. Comprehensive Trend Analysis
8 emerging music genres analyzed across YouTube, TikTok, Reddit, and other platforms

### 2. Saturation Detection
Identifies whether a style is emerging, growing, or saturated

### 3. Conflict Resolution
Intelligent weighting of Radar vs Claude Analysis (Claude 60%, Hermes 40%)

### 4. Production Pipeline
Generates complete Suno + YouTube metadata packages per style

### 5. Daily Channel Analysis
Tracks views, engagement, patterns, competitors, upload times

### 6. Persistent Memory
SQLite database with auto-versioning (1.0.0 → 1.0.1 → 1.1.0)

---

## Documentation

- **README.md** - Quick start and overview
- **HERMES_MASTER_SKILL_INTEGRATED.md** - Complete technical guide
- **COMPARATIVO_E_CONSOLIDACAO.md** - Comparison & consolidation strategy
- **ANALISE_ABRANGENTE_ESTILOS_MUSICAIS.md** - Detailed genre analysis
- **SUMARIO_EXECUTIVO.md** - Executive summary
- **data/music_intelligence_seed.json** - Seed export with 14 trend records, 90 radar records, and recommendations
- **data/music_intelligence_seed.db** - SQLite seed generated from the same data
- **references/youtube_radar_agent/** - Full migrated radar agent, reports, CSV/JSONL snapshots, scripts, configs, and Suno packages

---

## Migrated Data Feed (2026-07-30)

This repository is now fed with the previously generated Hermes radar assets:

- Radar reports from 2026-07-17, 2026-07-22, and 2026-07-30
- Raw YouTube JSONL snapshots and ranked CSV files
- Country Blues e Fé input URL configuration
- Five-song PT-BR Country Blues Gospel Suno package
- Production idea reports and YouTube metadata packages

Use the bundled seed without touching the user's live memory:

```bash
python hermes_master_music_intelligence.py \
  --db-path data/music_intelligence_seed.db \
  --add-trends-claude \
  --add-channels-hermes \
  --add-recommendations \
  --report \
  --export data/music_intelligence_seed.json
```

---

## Status

✅ **Real radar ingestion** (`--add-channels-hermes`) and persistent storage (SQLite + JSON backups)  
⚠️ **Trend table & default recommendations are synthetic demo data** — see honesty note above  
⚠️ **"Auto-updates"/"Continuous Learning"**: `auto_update()` exists but is dead code (never invoked)

---

Generated by Claude Code Agent
