#!/usr/bin/env bash
# Gera a pauta do dia para todos os nichos configurados.
# Chamado pelo systemd timer (ou cron) no VPS.
set -uo pipefail

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${MUSIC_FACTORY_OUT:-$BASE/out}"
DB="${MUSIC_FACTORY_DB:-$HOME/.music-factory/factory.db}"
LOG="${MUSIC_FACTORY_LOG:-$HOME/.music-factory/logs}"

mkdir -p "$LOG"
STAMP="$(date +%F)"
falhas=0

for cfg in "$BASE"/niches/*.json; do
    [ -e "$cfg" ] || { echo "nenhum nicho configurado em $BASE/niches"; exit 1; }
    niche="$(basename "$cfg" .json)"
    echo "── $niche ──"
    if python3 "$BASE/cli.py" --db-path "$DB" daily-brief \
            --niche "$niche" --out "$OUT" 2>&1 | tee -a "$LOG/$STAMP.log"; then
        :
    else
        echo "FALHA no nicho $niche" | tee -a "$LOG/$STAMP.log"
        falhas=$((falhas + 1))
    fi
done

# Um nicho quebrado não pode impedir os outros de rodar; o exit code
# diferente de zero faz o systemd registrar a falha no journal.
exit $((falhas > 0))
