SHELL := /bin/bash

.PHONY: help consigne1 consigne2 consigne3 consigne4 consigne5 clean prune status branch

help:
	@echo "Targets disponibles :"
	@echo "  make consigne1  - deploye la branche consigne 1 (logs statiques)"
	@echo "  make consigne2  - deploye la branche consigne 2 (server/client + Filebeat partage)"
	@echo "  make consigne3  - deploye la branche consigne 3 (un Filebeat par service)"
	@echo "  make consigne4  - deploye la branche consigne 4 (consigne 3 + Jaeger UI)"
	@echo "  make consigne5  - deploye la branche consigne 5 (python_apps_with_db + PostgreSQL + ELK)"
	@echo "  make clean      - arrete et supprime proprement les conteneurs/reseaux du projet"
	@echo "  make prune      - clean + suppression des volumes et logs generes"
	@echo "  make status     - affiche l'etat des conteneurs et la branche git courante"
	@echo "  make branch     - affiche la branche git courante"

consigne1:
	@./scripts/infra.sh deploy consigne1

consigne2:
	@./scripts/infra.sh deploy consigne2

consigne3:
	@./scripts/infra.sh deploy consigne3

consigne4:
	@./scripts/infra.sh deploy consigne4

consigne5:
	@./scripts/infra.sh deploy consigne5

clean:
	@./scripts/infra.sh clean

prune:
	@./scripts/infra.sh prune

status:
	@./scripts/infra.sh status

branch:
	@./scripts/infra.sh branch
