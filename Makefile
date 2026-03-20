SHELL := /bin/bash

.PHONY: help all up consigne1 consigne2 consigne3 consigne4 consigne5 clean clean1 clean2 clean3 clean4 clean5 clean-all prune status branch

help:
	@echo "Targets disponibles :"
	@echo "  make all        - alias de make up"
	@echo "  make up         - lance la stack associee a la branche active"
	@echo "  make consigne1  - deploye la branche consigne 1 (logs statiques)"
	@echo "  make consigne2  - deploye la branche consigne 2 (server/client + Filebeat partage)"
	@echo "  make consigne3  - deploye la branche consigne 3 (un Filebeat par service)"
	@echo "  make consigne4  - deploye la branche consigne 4 (Jaeger UI + traces client/server)"
	@echo "  make consigne5  - deploye la branche consigne 5 (python_apps_with_db + PostgreSQL)"
	@echo "  make clean1     - arrete proprement ce que lance make consigne1"
	@echo "  make clean2     - arrete proprement ce que lance make consigne2"
	@echo "  make clean3     - arrete proprement ce que lance make consigne3"
	@echo "  make clean4     - arrete proprement ce que lance make consigne4"
	@echo "  make clean5     - arrete proprement ce que lance make consigne5"
	@echo "  make clean      - alias de make clean-all"
	@echo "  make clean-all  - arrete proprement toutes les stacks du projet"
	@echo "  make prune      - clean + suppression des volumes et logs generes"
	@echo "  make status     - affiche l'etat des conteneurs et la branche git courante"
	@echo "  make branch     - affiche la branche git courante"

all: up

up:
	@./scripts/infra.sh up

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
	@./scripts/infra.sh clean all

clean1:
	@./scripts/infra.sh clean consigne1

clean2:
	@./scripts/infra.sh clean consigne2

clean3:
	@./scripts/infra.sh clean consigne3

clean4:
	@./scripts/infra.sh clean consigne4

clean5:
	@./scripts/infra.sh clean consigne5

clean-all:
	@./scripts/infra.sh clean all

prune:
	@./scripts/infra.sh prune

status:
	@./scripts/infra.sh status

branch:
	@./scripts/infra.sh branch
