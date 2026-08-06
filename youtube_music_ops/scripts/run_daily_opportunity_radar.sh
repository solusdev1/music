#!/usr/bin/env bash
set -euo pipefail
PY=${PYTHON:-/usr/bin/python3}
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
OPS_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
SCRIPT="$OPS_ROOT/scripts/run_daily_opportunity_radar.py"
OUT=$(MUSIC_OPS_ROOT="$OPS_ROOT" "$PY" "$SCRIPT" --limit "${DAILY_OPPORTUNITY_LIMIT:-4}")
echo "$OUT" | "$PY" -c 'import json,sys; d=json.load(sys.stdin); print("Radar diário de oportunidades musicais concluído"); print("Vídeos únicos: {}".format(d.get("rows"))); print("Erros finais: {}".format(d.get("final_errors"))); print("Relatório: {}".format(d.get("report"))); print("CSV: {}".format(d.get("csv"))); print("Raw JSON: {}".format(d.get("raw"))); print("Erros/retries: {}".format(d.get("errors")))'
