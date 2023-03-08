.ONESHELL:

SHELL = /bin/bash

override CONDA = $(CONDA_BASE)/bin/conda
override PKG = esr_task
override CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate

help:
	@echo "current CONDA_BASE: $(CONDA_BASE)"
	@echo "current CONDA: $(CONDA)"

clear_env:
	rm -rf $(CONDA_BASE)/envs/$(PKG)
	$(CONDA) index $(CONDA_BASE)/conda-bld

clear_all:
	rm -rf $(CONDA_BASE)/envs/$(PKG)
	rm -rf $(CONDA_BASE)/pkgs/$(PKG)*
	rm -rf $(CONDA_BASE)/conda-bld/linux-64/$(PKG)*
	rm -rf $(CONDA_BASE)/conda-bld/osx-arm64/$(PKG)*
	rm -rf $(CONDA_BASE)/conda-bld/$(PKG)*
	rm -rf $(CONDA_BASE)/conda-bld/linux-64/.cache/paths/$(PKG)*
	rm -rf $(CONDA_BASE)/conda-bld/linux-64/.cache/recipe/$(PKG)*
	rm -rf $(CONDA_BASE)/conda-bld/osx-arm64/.cache/paths/$(PKG)*
	rm -rf $(CONDA_BASE)/conda-bld/osx-arm64/.cache/recipe/$(PKG)*
	$(CONDA) index $(CONDA_BASE)/conda-bld

env: clear_all
	$(CONDA) env create -f env.yml

build:
	$(CONDA) build . --no-test

install:
	$(CONDA_ACTIVATE) $(PKG); $(CONDA) install $(PKG) -c local --yes --prefix $(CONDA_BASE)/envs/$(PKG)

all: env build install
