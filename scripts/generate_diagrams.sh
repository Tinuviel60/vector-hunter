#!/usr/bin/env sh
set -eu

# ---------------------------------------------------------------------------
# Résolution des chemins : on se base sur l'emplacement du script
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PROJECT_ROOT="$(CDPATH= cd -- "${SCRIPT_DIR}/.." && pwd)"

PROJECT_NAME="vector-hunter"
SRC_ROOT="${PROJECT_ROOT}/sources"
ROOT_PKG="vect_hunt"

OUT_DIR="${PROJECT_ROOT}/diagrams"
DOT_DIR="${OUT_DIR}/dot"
RENDER_DIR="${OUT_DIR}/rendered"

mkdir -p "${DOT_DIR}" "${RENDER_DIR}"

# Rend le package importable
export PYTHONPATH="${SRC_ROOT}"

# ---------------------------------------------------------------------------
# Détection des options supportées par ta version de pyreverse
# ---------------------------------------------------------------------------
HELP_TEXT="$(pyreverse --help 2>/dev/null || true)"

# On génère uniquement du DOT avec pyreverse
PYR_DOT_OPTS="-o dot"

# Réduction du bruit si possible
echo "${HELP_TEXT}" | grep -q -- "--no-assoc" && PYR_DOT_OPTS="${PYR_DOT_OPTS} --no-assoc" || PYR_DOT_OPTS="${PYR_DOT_OPTS} -A"
echo "${HELP_TEXT}" | grep -q -- " -S" && PYR_DOT_OPTS="${PYR_DOT_OPTS} -S" || true
echo "${HELP_TEXT}" | grep -q -- "--no-ancestors" && PYR_DOT_OPTS="${PYR_DOT_OPTS} --no-ancestors" || true

# ---------------------------------------------------------------------------
# Render un fichier DOT en plusieurs variantes SVG
# Arguments :
#   $1 : chemin vers le fichier .dot
#   $2 : préfixe de sortie (sans extension)
# ---------------------------------------------------------------------------
render_dot_variants() {
  dot_path="$1"
  out_prefix="$2"

  # Layout hiérarchique gauche → droite
  dot -Grankdir=LR -Gnodesep=0.6 -Granksep=1.0 -Gsplines=true -Goverlap=false \
    -Tsvg "${dot_path}" -o "${out_prefix}_dot_LR.svg"

  # Layout force-directed (souvent plus lisible pour gros graphes)
  sfdp -Goverlap=false -Gsplines=true \
    -Tsvg "${dot_path}" -o "${out_prefix}_sfdp.svg"
}

# ---------------------------------------------------------------------------
# Lance pyreverse pour produire les fichiers DOT
# Arguments :
#   $1 : label du projet
#   $2 : cible (package / module)
#   $3 : dossier de sortie
# ---------------------------------------------------------------------------
run_pyreverse_dot() {
  label="$1"
  target="$2"
  out_dir="$3"

  mkdir -p "${out_dir}"
  pyreverse ${PYR_DOT_OPTS} -p "${label}" "${target}" -d "${out_dir}"
}

# ---------------------------------------------------------------------------
# Rend les fichiers DOT standards générés par pyreverse
# ---------------------------------------------------------------------------
render_pyreverse_outputs() {
  dot_dir="$1"
  render_dir="$2"
  label="$3"

  mkdir -p "${render_dir}"

  classes_dot="${dot_dir}/classes_${label}.dot"
  packages_dot="${dot_dir}/packages_${label}.dot"

  [ -f "${classes_dot}" ] && render_dot_variants "${classes_dot}" "${render_dir}/classes_${label}"
  [ -f "${packages_dot}" ] && render_dot_variants "${packages_dot}" "${render_dir}/packages_${label}"
}

# ---------------------------------------------------------------------------
# 1) Diagramme global
# ---------------------------------------------------------------------------
GLOBAL_LABEL="${PROJECT_NAME}_global"
GLOBAL_DOT_OUT="${DOT_DIR}/global"
GLOBAL_RENDER_OUT="${RENDER_DIR}/global"

run_pyreverse_dot "${GLOBAL_LABEL}" "${ROOT_PKG}" "${GLOBAL_DOT_OUT}"
render_pyreverse_outputs "${GLOBAL_DOT_OUT}" "${GLOBAL_RENDER_OUT}" "${GLOBAL_LABEL}"

# ---------------------------------------------------------------------------
# 2) Diagrammes game et engine
# ---------------------------------------------------------------------------
if [ -d "${SRC_ROOT}/${ROOT_PKG}/game" ]; then
  GAME_LABEL="${PROJECT_NAME}_game"
  GAME_DOT_OUT="${DOT_DIR}/game"
  GAME_RENDER_OUT="${RENDER_DIR}/game"

  run_pyreverse_dot "${GAME_LABEL}" "${ROOT_PKG}.game" "${GAME_DOT_OUT}"
  render_pyreverse_outputs "${GAME_DOT_OUT}" "${GAME_RENDER_OUT}" "${GAME_LABEL}"
fi

if [ -d "${SRC_ROOT}/${ROOT_PKG}/engine" ]; then
  ENGINE_LABEL="${PROJECT_NAME}_engine"
  ENGINE_DOT_OUT="${DOT_DIR}/engine"
  ENGINE_RENDER_OUT="${RENDER_DIR}/engine"

  run_pyreverse_dot "${ENGINE_LABEL}" "${ROOT_PKG}.engine" "${ENGINE_DOT_OUT}"
  render_pyreverse_outputs "${ENGINE_DOT_OUT}" "${ENGINE_RENDER_OUT}" "${ENGINE_LABEL}"
fi

# ---------------------------------------------------------------------------
# 3) Un diagramme par package sous vect_hunt/engine
# ---------------------------------------------------------------------------
ENGINE_PATH="${SRC_ROOT}/${ROOT_PKG}/engine"

if [ -d "${ENGINE_PATH}" ]; then
  for pkg_init in "${ENGINE_PATH}"/*/__init__.py; do
    [ -f "${pkg_init}" ] || continue

    pkg_name="$(basename "$(dirname "${pkg_init}")")"
    PKG_LABEL="${PROJECT_NAME}_engine_${pkg_name}"
    PKG_DOT_OUT="${DOT_DIR}/engine_${pkg_name}"
    PKG_RENDER_OUT="${RENDER_DIR}/engine_${pkg_name}"

    run_pyreverse_dot "${PKG_LABEL}" "${ROOT_PKG}.engine.${pkg_name}" "${PKG_DOT_OUT}"
    render_pyreverse_outputs "${PKG_DOT_OUT}" "${PKG_RENDER_OUT}" "${PKG_LABEL}"
  done
fi

echo "DOT files generated in : ${DOT_DIR}"
echo "SVG variants generated in : ${RENDER_DIR}"
