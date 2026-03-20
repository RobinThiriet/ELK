#!/bin/sh
set -eu

KIBANA_URL="${KIBANA_URL:-http://kibana:5601}"
KIBANA_VERSION="${KIBANA_VERSION:-8.19.11}"
DATA_VIEW_ID="${DATA_VIEW_ID:-demo-data-view}"
DATA_VIEW_NAME="${DATA_VIEW_NAME:-demo}"
DATA_VIEW_PATTERN="${DATA_VIEW_PATTERN:-elk-demo-*}"
SEARCH_ID="${SEARCH_ID:-demo-logs-search}"
DASHBOARD_ID="${DASHBOARD_ID:-demo-dashboard}"

curl_json() {
  local method="$1"
  local url="$2"
  local data="${3:-}"

  if [ -n "$data" ]; then
    curl -fsS -X "$method" \
      -H "Content-Type: application/json" \
      -H "kbn-xsrf: true" \
      "$url" \
      -d "$data"
    return
  fi

  curl -fsS -X "$method" \
    -H "kbn-xsrf: true" \
    "$url"
}

wait_for_kibana() {
  echo "-> Attente de Kibana sur $KIBANA_URL"
  until curl -fsS "$KIBANA_URL/api/status" >/dev/null 2>&1; do
    sleep 5
  done
  echo "-> Kibana repond"
}

create_data_view() {
  local payload
  payload=$(cat <<JSON
{"attributes":{"title":"$DATA_VIEW_PATTERN","timeFieldName":"@timestamp","name":"$DATA_VIEW_NAME","allowHidden":false}}
JSON
)

  echo "-> Creation ou mise a jour de la Data View $DATA_VIEW_NAME"
  curl_json "POST" "$KIBANA_URL/api/saved_objects/index-pattern/$DATA_VIEW_ID?overwrite=true" "$payload" >/dev/null
}

set_default_data_view() {
  local config_id

  config_id=$(curl_json "GET" "$KIBANA_URL/api/saved_objects/_find?type=config&per_page=100" | \
    sed -n 's/.*"id":"\([^"]*\)".*/\1/p' | head -n 1)

  if [ -z "$config_id" ]; then
    config_id="$KIBANA_VERSION"
  fi

  echo "-> Definition de la Data View par defaut"
  curl_json "POST" "$KIBANA_URL/api/saved_objects/config/$config_id?overwrite=true" \
    "{\"attributes\":{\"defaultIndex\":\"$DATA_VIEW_ID\"}}" >/dev/null
}

create_saved_search() {
  local payload
  payload=$(cat <<JSON
{
  "attributes": {
    "title": "demo-logs",
    "description": "Vue sauvegardee des logs demo",
    "columns": ["service", "level", "event_type", "message"],
    "sort": [["@timestamp", "desc"]],
    "hideChart": false,
    "kibanaSavedObjectMeta": {
      "searchSourceJSON": "{\"query\":{\"language\":\"kuery\",\"query\":\"\"},\"filter\":[],\"indexRefName\":\"kibanaSavedObjectMeta.searchSourceJSON.index\"}"
    }
  },
  "references": [
    {
      "id": "$DATA_VIEW_ID",
      "name": "kibanaSavedObjectMeta.searchSourceJSON.index",
      "type": "index-pattern"
    }
  ]
}
JSON
)

  echo "-> Creation ou mise a jour de la recherche sauvegardee"
  curl_json "POST" "$KIBANA_URL/api/saved_objects/search/$SEARCH_ID?overwrite=true" "$payload" >/dev/null
}

create_dashboard() {
  local payload
  payload=$(cat <<JSON
{
  "attributes": {
    "title": "demo",
    "description": "Dashboard persistent pour visualiser rapidement les logs ELK du projet",
    "hits": 0,
    "optionsJSON": "{\"useMargins\":true,\"syncColors\":false,\"syncCursor\":true,\"syncTooltips\":false,\"hidePanelTitles\":false}",
    "panelsJSON": "[{\"version\":\"$KIBANA_VERSION\",\"type\":\"search\",\"panelIndex\":\"1\",\"gridData\":{\"x\":0,\"y\":0,\"w\":48,\"h\":15,\"i\":\"1\"},\"panelRefName\":\"panel_0\",\"embeddableConfig\":{\"columns\":[\"service\",\"level\",\"event_type\",\"message\"],\"sort\":[[\"@timestamp\",\"desc\"]],\"hideChart\":false}}]",
    "timeRestore": false,
    "kibanaSavedObjectMeta": {
      "searchSourceJSON": "{\"query\":{\"language\":\"kuery\",\"query\":\"\"},\"filter\":[]}"
    }
  },
  "references": [
    {
      "id": "$SEARCH_ID",
      "name": "panel_0",
      "type": "search"
    }
  ]
}
JSON
)

  echo "-> Creation ou mise a jour du dashboard demo"
  curl_json "POST" "$KIBANA_URL/api/saved_objects/dashboard/$DASHBOARD_ID?overwrite=true" "$payload" >/dev/null
}

main() {
  wait_for_kibana
  create_data_view
  set_default_data_view
  create_saved_search
  create_dashboard
  echo "-> Bootstrap Kibana termine"
}

main "$@"
