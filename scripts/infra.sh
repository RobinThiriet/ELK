#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

BRANCH_CONSIGNE1="consigne-1-log-analysed"
BRANCH_CONSIGNE2="consigne-2-python-apps-filebeat"
BRANCH_CONSIGNE3="consigne-3-filebeat-par-service"
BRANCH_CONSIGNE4="consigne-4-jaeger-ui"

ROOT_CONTAINERS=(
  "elk-elasticsearch"
  "elk-logstash"
  "elk-kibana"
  "elk-jaeger"
  "elk-kibana-setup"
  "elk-filebeat"
)

PY_CONTAINERS=(
  "chaos-api-server"
  "chaos-api-client"
  "chaos-filebeat-server"
  "chaos-filebeat-client"
)

VOLUMES=(
  "elk_esdata"
  "elk_filebeatdata"
  "python_apps_filebeat_server_data"
  "python_apps_filebeat_client_data"
)

NETWORKS=(
  "elk-observability"
)

current_branch() {
  git -C "$ROOT_DIR" branch --show-current
}

switch_branch() {
  local target="$1"
  if [[ "$(current_branch)" != "$target" ]]; then
    echo "-> Passage sur la branche $target"
    git -C "$ROOT_DIR" checkout "$target"
  else
    echo "-> Branche deja active : $target"
  fi
}

compose_root() {
  docker compose -f "$ROOT_DIR/docker-compose.yml" "$@"
}

compose_python() {
  if [[ -f "$ROOT_DIR/python_apps/docker-compose.yml" ]]; then
    docker compose -f "$ROOT_DIR/python_apps/docker-compose.yml" --project-directory "$ROOT_DIR/python_apps" "$@"
  fi
}

ensure_python_dirs() {
  mkdir -p \
    "$ROOT_DIR/python_apps/runtime_logs/server" \
    "$ROOT_DIR/python_apps/runtime_logs/client"
}

deploy_consigne1() {
  switch_branch "$BRANCH_CONSIGNE1"
  echo "-> Demarrage de la stack ELK pour la consigne 1"
  compose_root up -d
  echo "-> Consigne 1 prete"
}

deploy_consigne2() {
  switch_branch "$BRANCH_CONSIGNE2"
  echo "-> Demarrage de la stack ELK pour la consigne 2"
  compose_root up -d
  echo "-> Demarrage de python_apps pour la consigne 2"
  compose_python up --build -d
  echo "-> Consigne 2 prete"
}

deploy_consigne3() {
  switch_branch "$BRANCH_CONSIGNE3"
  ensure_python_dirs
  echo "-> Demarrage de la stack ELK pour la consigne 3"
  compose_root up -d
  echo "-> Demarrage de python_apps pour la consigne 3"
  compose_python up --build -d
  echo "-> Consigne 3 prete"
}

deploy_consigne4() {
  switch_branch "$BRANCH_CONSIGNE4"
  ensure_python_dirs
  echo "-> Demarrage de la stack ELK + Jaeger pour la consigne 4"
  compose_root up -d
  echo "-> Demarrage de python_apps pour la consigne 4"
  compose_python up --build -d
  echo "-> Consigne 4 prete"
}

clean_stack() {
  echo "-> Arret de python_apps si present"
  compose_python down --remove-orphans || true

  echo "-> Arret de la stack ELK"
  compose_root down --remove-orphans || true

  echo "-> Suppression des conteneurs eventuellement restants"
  docker rm -f "${PY_CONTAINERS[@]}" "${ROOT_CONTAINERS[@]}" >/dev/null 2>&1 || true

  echo "-> Suppression des reseaux dedies"
  for network in "${NETWORKS[@]}"; do
    docker network rm "$network" >/dev/null 2>&1 || true
  done
}

prune_stack() {
  clean_stack

  echo "-> Suppression des volumes dedies"
  for volume in "${VOLUMES[@]}"; do
    docker volume rm -f "$volume" >/dev/null 2>&1 || true
  done

  echo "-> Suppression des logs generes"
  rm -rf "$ROOT_DIR/python_apps/runtime_logs" || true
  rm -f "$ROOT_DIR/log_analysed/python_apps/"*.log >/dev/null 2>&1 || true

  echo "-> Nettoyage termine"
}

status_stack() {
  echo "Branche git : $(current_branch)"
  echo
  echo "[ELK]"
  compose_root ps || true
  if [[ -f "$ROOT_DIR/python_apps/docker-compose.yml" ]]; then
    echo
    echo "[python_apps]"
    compose_python ps || true
  fi
}

usage() {
  cat <<'EOF'
Usage:
  ./scripts/infra.sh deploy consigne1|consigne2|consigne3|consigne4
  ./scripts/infra.sh clean
  ./scripts/infra.sh prune
  ./scripts/infra.sh status
  ./scripts/infra.sh branch
EOF
}

main() {
  local cmd="${1:-}"
  case "$cmd" in
    deploy)
      case "${2:-}" in
        consigne1) deploy_consigne1 ;;
        consigne2) deploy_consigne2 ;;
        consigne3) deploy_consigne3 ;;
        consigne4) deploy_consigne4 ;;
        *) usage; exit 1 ;;
      esac
      ;;
    clean)
      clean_stack
      ;;
    prune)
      prune_stack
      ;;
    status)
      status_stack
      ;;
    branch)
      current_branch
      ;;
    *)
      usage
      exit 1
      ;;
  esac
}

main "$@"
