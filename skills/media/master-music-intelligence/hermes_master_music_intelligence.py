#!/usr/bin/env python3
"""
🎵 HERMES MASTER MUSIC INTELLIGENCE SKILL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Integração completa de:
  ✅ Last30Days Trend Analysis (estilos emergentes)
  ✅ Radar Channel Intelligence (análise competidora)
  ✅ Music Creation Pipeline (guia de produção)
  ✅ Saturation Detection (detecção de saturação)
  ✅ Persistent Memory (memória com histórico)
  ✅ Auto-versioning (v1.0 → v1.1 → v1.2...)
  ✅ Conflict Resolution (Radar vs Claude)

Version: 1.0.0 (Auto-updated on each use)
Last Updated: 2024-07-30
Memory: SQLite + JSON Backup

⚠️ HONESTY NOTE (2026-08): `CLAUDE_TRENDS` and `add_default_recommendations()`
below are a SYNTHETIC/ILLUSTRATIVE example dataset seeded when this skill was
first written — the growth %, engagement and "confidence" figures are not
measured from any API or scrape. They are not kept in sync with reality and
must not be treated as market intelligence. The only real, measured
performance data for this project's actual channels (Country Blues e Fé,
Estrada da Fé, Southern Grace Roads, etc.) lives in
`music-factory/data/*.db` (see `music-factory/core/learn.py` and
`core/opportunity.py`) and in `youtube_music_ops/radar/` (real TranscriptAPI/
yt-dlp scrapes). Prefer those sources over this file's seed data for any
real decision.
"""

import argparse
import csv
import json
import sqlite3
import os
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Any, Optional


def _fmt_num(value, decimals: int = 2) -> str:
    """Format a possibly-missing numeric DB value without crashing.

    Real ingested rows (not the synthetic seed) can legitimately have
    NULL growth/engagement columns; ``f"{None:.2f}"`` raises TypeError.
    """
    if value is None:
        return "—"
    return f"{value:.{decimals}f}"


class HermesmasterMusicIntelligence:
    """Master Music Intelligence Platform para Hermes."""

    def __init__(self, db_path: str = "~/.hermes/music_intelligence.db"):
        """Initialize the master intelligence system."""
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.version = "1.0.0"
        self.last_updated = datetime.now(UTC).isoformat()
        self._init_db()
        self._load_all_data()

    def _init_db(self):
        """Initialize SQLite database with all necessary tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabela 1: Análise de Tendências (Last30Days)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trend_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                style TEXT UNIQUE,
                growth_percentage REAL,
                new_channels INTEGER,
                total_views INTEGER,
                avg_engagement REAL,
                saturation_level TEXT,
                timestamp TEXT,
                data_source TEXT
            )
        """)

        # Tabela 2: Análise de Canais (Radar)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channel_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT,
                style TEXT,
                views INTEGER,
                subscribers INTEGER,
                engagement_rate REAL,
                posting_frequency TEXT,
                quality_score REAL,
                data_source TEXT,
                timestamp TEXT
            )
        """)

        # Tabela 3: Recomendações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                style TEXT,
                rank INTEGER,
                score REAL,
                reasoning TEXT,
                confidence_level TEXT,
                timestamp TEXT
            )
        """)

        # Tabela 4: Histórico de Decisões
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decision_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_type TEXT,
                style_chosen TEXT,
                reason TEXT,
                outcome TEXT,
                timestamp TEXT
            )
        """)

        # Tabela 5: Conflitos (Radar vs Claude)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conflicts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                style TEXT,
                radar_opinion TEXT,
                claude_opinion TEXT,
                divergence_level TEXT,
                resolution TEXT,
                timestamp TEXT
            )
        """)

        # Tabela 6: Metadata da Skill
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skill_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        conn.commit()
        conn.close()

    def _load_all_data(self):
        """Load all existing data into memory."""
        self.trends = self._load_trends()
        self.channels = self._load_channels()
        self.recommendations = self._load_recommendations()
        self.conflicts = self._load_conflicts()

    def _load_trends(self) -> Dict:
        """Load trend analysis data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trend_analysis")
        cols = [description[0] for description in cursor.description]
        trends = {row[1]: dict(zip(cols, row)) for row in cursor.fetchall()}
        conn.close()
        return trends

    def _load_channels(self) -> List[Dict]:
        """Load channel analysis data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM channel_analysis")
        cols = [description[0] for description in cursor.description]
        channels = [dict(zip(cols, row)) for row in cursor.fetchall()]
        conn.close()
        return channels

    def _load_recommendations(self) -> List[Dict]:
        """Load recommendations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recommendations ORDER BY rank")
        cols = [description[0] for description in cursor.description]
        recs = [dict(zip(cols, row)) for row in cursor.fetchall()]
        conn.close()
        return recs

    def _load_conflicts(self) -> List[Dict]:
        """Load conflicts between Radar and Claude."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conflicts")
        cols = [description[0] for description in cursor.description]
        conflicts = [dict(zip(cols, row)) for row in cursor.fetchall()]
        conn.close()
        return conflicts

    # ═══════════════════════════════════════════════════════════════════════════════
    # MÓDULO 1: LAST30DAYS TREND ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════════════

    def add_trend_analysis(self, style: str, data: Dict[str, Any], source: str = "claude"):
        """Add or update trend analysis data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO trend_analysis
            (style, growth_percentage, new_channels, total_views, avg_engagement, saturation_level, timestamp, data_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            style,
            data.get('growth_percentage'),
            data.get('new_channels'),
            data.get('total_views'),
            data.get('avg_engagement'),
            data.get('saturation_level'),
            datetime.now(UTC).isoformat(),
            source
        ))

        conn.commit()
        conn.close()
        self.trends = self._load_trends()

    def get_trend_analysis(self, style: Optional[str] = None) -> Dict:
        """Get trend analysis data."""
        if style:
            return self.trends.get(style, {})
        return self.trends

    # ═══════════════════════════════════════════════════════════════════════════════
    # MÓDULO 2: RADAR CHANNEL INTELLIGENCE
    # ═══════════════════════════════════════════════════════════════════════════════

    def add_channel(self, channel_data: Dict[str, Any], source: str = "radar"):
        """Add channel analysis data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO channel_analysis
            (channel_name, style, views, subscribers, engagement_rate, posting_frequency, quality_score, data_source, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            channel_data.get('name'),
            channel_data.get('style'),
            channel_data.get('views'),
            channel_data.get('subscribers'),
            channel_data.get('engagement_rate'),
            channel_data.get('posting_frequency'),
            channel_data.get('quality_score'),
            source,
            datetime.now(UTC).isoformat()
        ))

        conn.commit()
        conn.close()
        self.channels = self._load_channels()

    def get_channels_by_style(self, style: str) -> List[Dict]:
        """Get all channels for a specific style."""
        return [c for c in self.channels if c.get('style') == style]

    def get_channel_stats(self, style: str) -> Dict:
        """Get aggregated stats for channels in a style."""
        channels = self.get_channels_by_style(style)
        if not channels:
            return {}

        avg_engagement = sum(c.get('engagement_rate', 0) for c in channels) / len(channels)
        total_subs = sum(c.get('subscribers', 0) for c in channels)
        avg_quality = sum(c.get('quality_score', 0) for c in channels) / len(channels)

        return {
            'style': style,
            'channel_count': len(channels),
            'avg_engagement': avg_engagement,
            'total_subscribers': total_subs,
            'avg_quality_score': avg_quality,
            'data_source': 'radar'
        }

    # ═══════════════════════════════════════════════════════════════════════════════
    # MÓDULO 3: CONFLICT RESOLUTION (Radar vs Claude)
    # ═══════════════════════════════════════════════════════════════════════════════

    def detect_conflict(self, style: str, radar_data: Dict, claude_data: Dict) -> Optional[Dict]:
        """Detect conflicts between Radar and Claude analysis."""
        conflicts = []

        # Comparar saturação
        radar_saturation = radar_data.get('saturation_level', '').lower()
        claude_saturation = claude_data.get('saturation_level', '').lower()

        if radar_saturation != claude_saturation:
            conflicts.append({
                'metric': 'saturation',
                'radar': radar_saturation,
                'claude': claude_saturation,
                'divergence': 'HIGH' if 'low' in radar_saturation and 'high' in claude_saturation else 'MEDIUM'
            })

        # Comparar crescimento
        radar_growth = radar_data.get('growth_percentage', 0)
        claude_growth = claude_data.get('growth_percentage', 0)
        if abs(radar_growth - claude_growth) > 50:  # Diferença > 50%
            conflicts.append({
                'metric': 'growth',
                'radar': radar_growth,
                'claude': claude_growth,
                'divergence': 'HIGH'
            })

        if conflicts:
            return {
                'style': style,
                'conflicts': conflicts,
                'resolution': self._resolve_conflict(style, radar_data, claude_data)
            }
        return None

    def _resolve_conflict(self, style: str, radar_data: Dict, claude_data: Dict) -> str:
        """Resolve conflicts using weighted scoring.

        CAVEAT: the "Claude" side of this comparison is, for most styles,
        the synthetic `CLAUDE_TRENDS` seed table (see module docstring) —
        not a live analysis. Do not read "Claude está correto" below as a
        real verdict; it is this function's original hardcoded example.
        """
        # Claude tem mais dados históricos e análise profunda
        claude_weight = 0.6
        radar_weight = 0.4

        # Exemplo original (2024): Country Blues
        # Radar diz: "Indo bem, sem saturação"
        # Claude (seed sintético) diz: "100+ canais, crescimento lento 45%, saturado"
        #
        # Esse exemplo envelheceu mal: o acervo real do projeto (music-factory)
        # mede Country Blues e Fé como o canal de MELHOR desempenho medido
        # (ver ANALISE-2026-07-30.md e music-factory/data/*.db), contradizendo
        # o placeholder "saturado" abaixo. Mantido apenas como amostra de
        # como o resolvedor de conflito funciona — não use para decidir nada.
        if style.lower() == "country blues gospel":
            return (
                "⚠️ EXEMPLO ILUSTRATIVO (não é veredito real):\n"
                "  Radar: Country Blues está indo bem\n"
                "  Claude (seed sintético): Country Blues está saturado (100+ canais, 45% crescimento)\n"
                "  Dado real medido no próprio projeto: Country Blues e Fé é o canal com "
                "melhor desempenho medido — o placeholder 'saturado' está desatualizado/incorreto.\n"
                "  → Confie em music-factory/data/*.db, não nesta amostra."
            )

        # Padrão geral: nota de exemplo, não recomendação
        return (
            f"Exemplo de resolução ponderada (Claude peso {claude_weight}, Radar peso "
            f"{radar_weight}) — placeholder ilustrativo, sem dado real por trás para "
            f"'{style}'."
        )

    def log_conflict(self, style: str, radar_opinion: str, claude_opinion: str, resolution: str):
        """Log conflict for future reference."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        divergence = "HIGH" if "Country Blues" in style else "MEDIUM"

        cursor.execute("""
            INSERT INTO conflicts (style, radar_opinion, claude_opinion, divergence_level, resolution, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (style, radar_opinion, claude_opinion, divergence, resolution, datetime.now(UTC).isoformat()))

        conn.commit()
        conn.close()
        self.conflicts = self._load_conflicts()

    # ═══════════════════════════════════════════════════════════════════════════════
    # MÓDULO 4: RECOMENDAÇÕES INTELIGENTES
    # ═══════════════════════════════════════════════════════════════════════════════

    def add_recommendation(self, style: str, rank: int, score: float, reasoning: str, confidence: str = "HIGH"):
        """Add recommendation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO recommendations (style, rank, score, reasoning, confidence_level, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (style, rank, score, reasoning, confidence, datetime.now(UTC).isoformat()))

        conn.commit()
        conn.close()
        self.recommendations = self._load_recommendations()

    def get_recommendations(self, limit: int = 5) -> List[Dict]:
        """Get top recommendations."""
        return self.recommendations[:limit]

    def get_recommendations_for_profile(self, profile: str) -> List[Dict]:
        """Get recommendations based on creator profile."""
        profiles = {
            'electronic_producer': ['Hyperpop', 'Amapiano', 'Synthwave'],
            'rapper_mc': ['Phonk', 'Emo Rap', 'Reggaeton Trap'],
            'independent_musician': ['Indie Bedroom Pop', 'Hyperpunk', 'Emo Rap'],
            'global_creator': ['Amapiano', 'Reggaeton Trap', 'Phonk']
        }

        recommended_styles = profiles.get(profile, [])
        return [r for r in self.recommendations if r.get('style') in recommended_styles]

    # ═══════════════════════════════════════════════════════════════════════════════
    # MÓDULO 5: MÚSICA CREATION PIPELINE
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_creation_guide(self, style: str) -> Dict:
        """Get step-by-step guide for creating music in a style."""
        guides = {
            "Phonk": {
                "tools": ["Ableton Live", "FL Studio", "Logic Pro"],
                "bpm_range": "60-90 BPM",
                "key_elements": ["Dark samples", "Lo-fi drums", "Vintage vibes"],
                "production_time": "2-4 hours per track",
                "monetization": ["AdSense", "Super Chat", "Beat sales", "Battles"],
                "best_practices": [
                    "Create 2-3 beats per week",
                    "Use trending samples",
                    "Collaborate with rappers",
                    "Post on TikTok/Reels daily"
                ]
            },
            "Hyperpop": {
                "tools": ["FL Studio", "Ableton", "Max/MSP"],
                "bpm_range": "120-200 BPM",
                "key_elements": ["Pitched vocals", "Chaotic percussion", "Digital synths"],
                "production_time": "3-6 hours per track",
                "monetization": ["AdSense", "Memberships", "Patreon"],
                "best_practices": [
                    "Experiment constantly",
                    "Follow global trends",
                    "Share production process",
                    "Engage with Gen Z audience"
                ]
            },
            "Indie Bedroom Pop": {
                "tools": ["Audacity", "GarageBand", "Reaper"],
                "bpm_range": "80-120 BPM",
                "key_elements": ["Acoustic instruments", "Lo-fi recordings", "Emotional vocals"],
                "production_time": "4-8 hours per track",
                "monetization": ["AdSense", "Spotify", "Bandcamp"],
                "best_practices": [
                    "Focus on authentic sound",
                    "Post consistently (weekly)",
                    "Share behind-the-scenes",
                    "Build engaged community"
                ]
            },
            "Reggaeton Trap": {
                "tools": ["FL Studio", "Logic Pro", "Ableton"],
                "bpm_range": "85-105 BPM",
                "key_elements": ["Reggaeton rhythm", "Trap drums", "Latin samples"],
                "production_time": "2-4 hours per track",
                "monetization": ["AdSense", "Shows", "Streaming", "Collaborations"],
                "best_practices": [
                    "Study reggaeton patterns",
                    "Collaborate with latin artists",
                    "Post 2x per week",
                    "Target latino audience"
                ]
            }
        }

        return guides.get(style, self._default_guide())

    def _default_guide(self) -> Dict:
        """Default creation guide."""
        return {
            "tools": ["FL Studio", "Ableton Live"],
            "production_time": "3-5 hours per track",
            "best_practices": [
                "Post consistently (2-3 videos/week)",
                "Engage with community",
                "Use trending sounds",
                "Create playlists",
                "Collaborate with other artists"
            ]
        }

    # ═══════════════════════════════════════════════════════════════════════════════
    # MÓDULO 6: ANÁLISE PERSISTENTE E VERSIONAMENTO
    # ═══════════════════════════════════════════════════════════════════════════════

    def export_to_json(self, filepath: str = "~/.hermes/music_intelligence_export.json"):
        """Export all data to JSON backup."""
        filepath = Path(filepath).expanduser()
        data = {
            'version': self.version,
            'last_updated': self.last_updated,
            'timestamp': datetime.now(UTC).isoformat(),
            'trends': self.trends,
            'channels': self.channels,
            'recommendations': self.recommendations,
            'conflicts': self.conflicts
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        return filepath

    def generate_report(self) -> str:
        """Generate comprehensive analysis report."""
        synthetic_n = sum(1 for d in self.trends.values() if d.get('data_source') == 'claude+repo-seed')
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           🎵 HERMES MASTER MUSIC INTELLIGENCE REPORT                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 VERSION: {self.version}
📅 LAST UPDATED: {self.last_updated}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 TREND ANALYSIS ({len(self.trends)} styles tracked):
"""
        if synthetic_n:
            report += (
                f"⚠️  {synthetic_n} of {len(self.trends)} records are SYNTHETIC seed data "
                "(illustrative, not measured — see module docstring).\n"
                "   Real measured performance for this project's channels lives in "
                "music-factory/data/*.db.\n"
            )

        if self.trends:
            for style, data in sorted(self.trends.items(), key=lambda x: x[1].get('growth_percentage') or 0, reverse=True)[:5]:
                report += f"\n  ✅ {style}"
                report += f"\n     • Growth: {_fmt_num(data.get('growth_percentage'))}%"
                report += f"\n     • Saturation: {data.get('saturation_level') or '—'}"
                report += f"\n     • Engagement: {_fmt_num(data.get('avg_engagement'))}%"

        report += f"\n\n📺 CHANNEL ANALYSIS ({len(self.channels)} channels tracked):"
        if self.channels:
            channels_by_style = {}
            for ch in self.channels:
                style = ch.get('style')
                if style not in channels_by_style:
                    channels_by_style[style] = []
                channels_by_style[style].append(ch)

            for style, channels in sorted(channels_by_style.items())[:5]:
                vals = [c.get('engagement_rate') or 0 for c in channels]
                avg_eng = sum(vals) / len(vals)
                report += f"\n  ✅ {style}: {len(channels)} channels, avg engagement {avg_eng:.2f}%"

        report += f"\n\n⚠️  CONFLICTS DETECTED ({len(self.conflicts)}):"
        if self.conflicts:
            for conflict in self.conflicts[-3:]:  # Últimos 3
                report += f"\n  ⚠️  {conflict.get('style')}: {conflict.get('divergence_level')} divergence"
                report += f"\n     → Resolution: {(conflict.get('resolution') or '')[:80]}..."

        report += f"\n\n✅ TOP RECOMMENDATIONS:"
        for rec in self.get_recommendations(3):
            report += f"\n  {rec.get('rank')}. {rec.get('style')} (Score: {rec.get('score')})"
            report += f"\n     → {(rec.get('reasoning') or '')[:60]}..."

        report += f"\n\n💾 MEMORY STATUS: {len(self.trends)} trends + {len(self.channels)} channels + {len(self.conflicts)} conflicts"
        report += f"\n📁 DATABASE: {self.db_path}"
        report += f"\n\n{'═' * 80}\n"

        return report

    def auto_update(self):
        """Auto-update version on each use."""
        # Incrementar versão: v1.0.0 → v1.0.1 → v1.1.0
        parts = self.version.split('.')
        patch = int(parts[2]) + 1

        # Reset patch a cada 10 atualizações
        if patch >= 10:
            minor = int(parts[1]) + 1
            patch = 0
            self.version = f"{parts[0]}.{minor}.{patch}"
        else:
            self.version = f"{parts[0]}.{parts[1]}.{patch}"

        self.last_updated = datetime.now(UTC).isoformat()

        # Atualizar metadata
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM skill_metadata WHERE key='version'")
        cursor.execute("DELETE FROM skill_metadata WHERE key='last_updated'")
        cursor.execute("INSERT INTO skill_metadata VALUES (?, ?)", ('version', self.version))
        cursor.execute("INSERT INTO skill_metadata VALUES (?, ?)", ('last_updated', self.last_updated))
        conn.commit()
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════════
# CLI + SEEDS DO REPOSITÓRIO
# ═══════════════════════════════════════════════════════════════════════════════

SKILL_DIR = Path(__file__).resolve().parent
RADAR_REFERENCE_DIR = SKILL_DIR / "references" / "youtube_radar_agent"


# ⚠️ SYNTHETIC EXAMPLE DATA — not measured, not sourced, not kept up to date.
# Written as illustrative seed data when this skill was first built. None of
# these genres correspond to a channel this project actually operates (all
# real channels are Country/Gospel Blues PT/EN/ES — see music-factory/niches/).
# Growth %, engagement and saturation here are invented numbers for demoing
# the trend-analysis/conflict-resolution code paths. For real numbers, load
# `add_radar_channels()` (real yt-dlp scrapes) or read music-factory's
# `data/*.db` directly.
CLAUDE_TRENDS = {
    "Phonk": {"growth_percentage": 234, "new_channels": 88, "total_views": 4281000, "avg_engagement": 4.69, "saturation_level": "Very Low"},
    "Hyperpop": {"growth_percentage": 245, "new_channels": 74, "total_views": 3920000, "avg_engagement": 4.42, "saturation_level": "Very Low"},
    "Indie Bedroom Pop": {"growth_percentage": 167, "new_channels": 156, "total_views": 3580000, "avg_engagement": 4.31, "saturation_level": "Low"},
    "Reggaeton Trap": {"growth_percentage": 198, "new_channels": 63, "total_views": 4410000, "avg_engagement": 5.11, "saturation_level": "Low"},
    "Emo Rap": {"growth_percentage": 176, "new_channels": 69, "total_views": 3370000, "avg_engagement": 4.08, "saturation_level": "Low"},
    "Amapiano": {"growth_percentage": 212, "new_channels": 58, "total_views": 4010000, "avg_engagement": 4.22, "saturation_level": "Emerging"},
    "Hyperpunk": {"growth_percentage": 223, "new_channels": 47, "total_views": 2860000, "avg_engagement": 3.92, "saturation_level": "Low"},
    "Synthwave": {"growth_percentage": 189, "new_channels": 51, "total_views": 3190000, "avg_engagement": 3.87, "saturation_level": "Low"},
    "Trap Gospel": {"growth_percentage": 180, "new_channels": 44, "total_views": 3250000, "avg_engagement": 4.26, "saturation_level": "Emerging"},
    "Sertanejo Trap Gospel": {"growth_percentage": 162, "new_channels": 52, "total_views": 2810000, "avg_engagement": 4.10, "saturation_level": "Emerging"},
    "Funk Gospel": {"growth_percentage": 145, "new_channels": 39, "total_views": 2600000, "avg_engagement": 4.15, "saturation_level": "Growing"},
    "Afrobeat Gospel": {"growth_percentage": 138, "new_channels": 34, "total_views": 2100000, "avg_engagement": 3.98, "saturation_level": "Emerging"},
    "Pagode Gospel": {"growth_percentage": 72, "new_channels": 18, "total_views": 1960000, "avg_engagement": 3.20, "saturation_level": "Medium-High"},
    "Country Blues Gospel": {"growth_percentage": 45, "new_channels": 12, "total_views": 3177000, "avg_engagement": 2.92, "saturation_level": "High"},
}


def _infer_style(row: Dict[str, str]) -> str:
    text = " ".join([row.get("query", ""), row.get("title", ""), row.get("detected_themes", "")]).lower()
    if "sertanejo" in text and "trap" in text:
        return "Sertanejo Trap Gospel"
    if "sertanejo" in text:
        return "Sertanejo Gospel"
    if "country" in text or "blues" in text or "outlaw" in text:
        return "Country Blues Gospel"
    if "funk" in text:
        return "Funk Gospel"
    if "afrobeat" in text:
        return "Afrobeat Gospel"
    if "trap" in text:
        return "Trap Gospel"
    return "Gospel Music"


def add_claude_trends(hermes: HermesmasterMusicIntelligence) -> None:
    for style, data in CLAUDE_TRENDS.items():
        hermes.add_trend_analysis(style, data, source="claude+repo-seed")


def add_radar_channels(hermes: HermesmasterMusicIntelligence, radar_dir: Path = RADAR_REFERENCE_DIR) -> int:
    processed_dir = radar_dir / "data_processed"
    csv_files = sorted(processed_dir.glob("videos_ranked_*.csv"))
    conn = sqlite3.connect(hermes.db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM channel_analysis WHERE data_source = ?", ("youtube-radar-agent",))
    conn.commit()
    conn.close()
    added = 0
    seen = set()
    for csv_file in csv_files:
        with csv_file.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                key = (row.get("url"), csv_file.name)
                if not row.get("title") or key in seen:
                    continue
                seen.add(key)
                views = int(float(row.get("view_count") or 0))
                likes_per_1000 = float(row.get("likes_per_1000") or 0)
                comments_per_1000 = float(row.get("comments_per_1000") or 0)
                quality = float(row.get("viral_score") or 0)
                hermes.add_channel({
                    "name": row.get("channel") or "Unknown channel",
                    "style": _infer_style(row),
                    "views": views,
                    "subscribers": 0,
                    "engagement_rate": likes_per_1000 + comments_per_1000,
                    "posting_frequency": f"snapshot:{csv_file.stem}",
                    "quality_score": quality,
                }, source="youtube-radar-agent")
                added += 1
    return added


def add_default_recommendations(hermes: HermesmasterMusicIntelligence) -> None:
    """Seed illustrative example recommendations — SYNTHETIC, not real scoring.

    None of these ranks/scores come from measurement; they demo the
    ``recommendations`` table shape. Ironically, rank #4 here ("já
    concorrido"/crowded) is this project's actual best-performing real
    channel (Country Blues e Fé — see music-factory/data/*.db), and ranks
    1-3 correspond to genres with zero production infrastructure in this
    repo. Do not use this seed to steer real channel strategy.
    """
    recommendations = [
        ("Sertanejo Trap Gospel", 1, 452, "[SYNTHETIC] Maior janela estratégica gospel BR: 52 novos canais e público rural/interior claro", "SYNTHETIC-DEMO"),
        ("Trap Gospel", 2, 445, "[SYNTHETIC] Crescimento forte e engajamento alto com baixa saturação relativa", "SYNTHETIC-DEMO"),
        ("Phonk", 3, 440, "[SYNTHETIC] Score global alto para beats dark, shorts e colaborações com rappers", "SYNTHETIC-DEMO"),
        ("Country Blues Gospel", 4, 365, "[SYNTHETIC score, but the REAL channel is this project's top performer per music-factory/data/*.db — treat this rank as wrong]", "SYNTHETIC-DEMO"),
    ]
    conn = sqlite3.connect(hermes.db_path)
    cursor = conn.cursor()
    cursor.executemany("DELETE FROM recommendations WHERE style = ?", [(rec[0],) for rec in recommendations])
    conn.commit()
    conn.close()
    for style, rank, score, reasoning, confidence in recommendations:
        hermes.add_recommendation(style, rank, score, reasoning, confidence)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hermes Master Music Intelligence")
    parser.add_argument("--db-path", default="~/.hermes/music_intelligence.db", help="SQLite database path")
    parser.add_argument("--init", action="store_true", help="Initialize the SQLite database")
    parser.add_argument("--add-trends-claude", action="store_true", help="Seed Claude/global + gospel trend analysis")
    parser.add_argument("--add-channels-hermes", action="store_true", help="Seed channel/video snapshots from references/youtube_radar_agent")
    parser.add_argument("--add-recommendations", action="store_true", help="Seed default recommendations")
    parser.add_argument("--report", action="store_true", help="Print the current intelligence report")
    parser.add_argument("--guide", help="Print a creation guide for a style, e.g. 'Phonk'")
    parser.add_argument("--export", help="Export the current database to a JSON file")
    parser.add_argument("--demo", action="store_true", help="Run the original demo")
    return parser


def main(argv: Optional[List[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    if args.demo:
        demo()
        return

    hermes = HermesmasterMusicIntelligence(db_path=args.db_path)
    if args.init:
        print(f"Initialized database: {hermes.db_path}")
    if args.add_trends_claude:
        add_claude_trends(hermes)
        print(f"Seeded {len(CLAUDE_TRENDS)} trend records")
    if args.add_channels_hermes:
        added = add_radar_channels(hermes)
        print(f"Seeded {added} radar channel/video records")
    if args.add_recommendations:
        add_default_recommendations(hermes)
        print("Seeded default recommendations")
    if args.guide:
        print(json.dumps(hermes.get_creation_guide(args.guide), indent=2, ensure_ascii=False))
    if args.export:
        filepath = hermes.export_to_json(args.export)
        print(f"Exported data to: {filepath}")
    if args.report or not any(vars(args).values()):
        print(hermes.generate_report())


# ═══════════════════════════════════════════════════════════════════════════════
# INSTÂNCIA GLOBAL + EXEMPLOS DE USO
# ═══════════════════════════════════════════════════════════════════════════════

def demo():
    """Demo usage of Hermes Master Music Intelligence."""

    print("🎵 Inicializando Hermes Master Music Intelligence...\n")

    # Inicializar
    hermes = HermesmasterMusicIntelligence()
    hermes.auto_update()

    # Adicionar dados de análise de tendências (Claude)
    claude_trends = {
        'Phonk': {
            'growth_percentage': 234,
            'new_channels': 88,
            'total_views': 4281000,
            'avg_engagement': 4.69,
            'saturation_level': 'Very Low'
        },
        'Country Blues Gospel': {
            'growth_percentage': 45,
            'new_channels': 12,
            'total_views': 3177000,
            'avg_engagement': 2.92,
            'saturation_level': 'High'
        }
    }

    for style, data in claude_trends.items():
        hermes.add_trend_analysis(style, data, source='claude')

    # Adicionar dados de Radar (simulado)
    radar_data = {
        'Country Blues Gospel': {
            'growth_percentage': 60,  # Mais alto que Claude
            'saturation_level': 'Medium'  # Menos saturado que Claude diz
        }
    }

    # Detectar conflitos
    for style, radar in radar_data.items():
        claude = hermes.get_trend_analysis(style)
        if claude:
            conflict = hermes.detect_conflict(style, radar, claude)
            if conflict:
                print(f"🚨 {conflict['resolution']}\n")
                hermes.log_conflict(
                    style,
                    f"Growth: {radar.get('growth_percentage')}%, Sat: {radar.get('saturation_level')}",
                    f"Growth: {claude.get('growth_percentage')}%, Sat: {claude.get('saturation_level')}",
                    conflict['resolution']
                )

    # Adicionar recomendações
    recommendations = [
        ('Phonk', 1, 440, 'Score mais alto: crescimento + novos canais', 'HIGH'),
        ('Hyperpop', 2, 436, 'Crescimento 245% (maior)', 'HIGH'),
        ('Indie Bedroom Pop', 3, 428, '156 novos canais (mais espaço)', 'HIGH'),
        ('Reggaeton Trap', 4, 380, 'Engajamento 5.11% (segundo maior)', 'HIGH'),
    ]

    for style, rank, score, reasoning, confidence in recommendations:
        hermes.add_recommendation(style, rank, score, reasoning, confidence)

    # Mostrar relatório
    print(hermes.generate_report())

    # Mostrar guia de criação
    print("\n🎨 GUIA DE CRIAÇÃO - PHONK:")
    guide = hermes.get_creation_guide('Phonk')
    print(json.dumps(guide, indent=2))

    # Mostrar recomendações por perfil
    print("\n\n🎯 RECOMENDAÇÕES PARA RAPPER/MC:")
    for rec in hermes.get_recommendations_for_profile('rapper_mc'):
        print(f"  • {rec['style']} (Score: {rec['score']})")

    # Exportar dados
    filepath = hermes.export_to_json()
    print(f"\n💾 Dados exportados para: {filepath}")

    # Info versão
    print(f"\n📦 Skill Version: {hermes.version}")


if __name__ == "__main__":
    main()
