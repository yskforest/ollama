#!/usr/bin/env bash
set -euo pipefail

# modelfile/ 配下の *.Modelfile から Ollama カスタムモデルを一括作成し、
# 作成したモデルのパラメータを logs/create_models.log に記録するスクリプト
# 使い方:
#   ./scripts/create_models.sh                     # modelfile/*.Modelfile をすべて作成
#   ./scripts/create_models.sh bonsai-2:27b-agent  # 指定モデルのみ作成

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MODELFILE_DIR="${REPO_ROOT}/modelfile"
LOG_DIR="${REPO_ROOT}/logs"
LOG_FILE="${LOG_DIR}/create_models.log"

shopt -s nullglob
files=("${MODELFILE_DIR}"/*.Modelfile)
shopt -u nullglob

if [ ${#files[@]} -eq 0 ]; then
    echo "エラー: ${MODELFILE_DIR} に .Modelfile が見つかりません。" >&2
    exit 1
fi

target_filter="${1:-}"
created_count=0

mkdir -p "${LOG_DIR}"
cd "${REPO_ROOT}"

for filepath in "${files[@]}"; do
    filename="$(basename "${filepath}")"
    model_name="${filename%.Modelfile}"

    if [ -n "${target_filter}" ] && [ "${model_name}" != "${target_filter}" ]; then
        continue
    fi

    echo "=== Creating model: ${model_name} (from modelfile/${filename}) ==="
    docker compose exec -T ollama ollama create "${model_name}" -f "/workspace/modelfile/${filename}"

    {
        echo "============================================================"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Model: ${model_name} (modelfile/${filename})"
        echo "============================================================"
        docker compose exec -T ollama ollama show "${model_name}" | tr -d '\r'
        echo ""
    } >> "${LOG_FILE}"

    created_count=$((created_count + 1))
done

if [ -n "${target_filter}" ] && [ "${created_count}" -eq 0 ]; then
    echo "エラー: '${target_filter}' に対応する Modelfile (${MODELFILE_DIR}/${target_filter}.Modelfile) が見つかりません。" >&2
    exit 1
fi

echo "完了: ${created_count} 件のモデルを作成し、パラメータを ${LOG_FILE} に記録しました。"
