SHELL := /bin/bash

.PHONY: help build run smoke clean

help:
	@echo "OpenShiho targets:"
	@echo "  make build   Build the container image (auto-detects docker/podman)"
	@echo "  make run     Run the container (builds first if the image is missing)"
	@echo "  make smoke   Validate shell/python syntax and workflow YAML"
	@echo "  make clean   Remove the local openshiho:latest image"

build:
	cd container && ./build.sh

run:
	cd container && ./run.sh

smoke:
	bash -n container/build.sh container/run.sh container/scripts/htb-connect
	python3 -m py_compile container/scripts/query-scripts-v1.0.py container/scripts/query-learnings-v1.0.py
	@python3 -c "import yaml" 2>/dev/null && \
	  python3 -c "import yaml, glob; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml')]" && \
	  echo "workflow YAML OK" || \
	  echo "skipping workflow YAML check (PyYAML not installed)"

clean:
	@RUNTIME=$${RUNTIME:-$$(command -v podman >/dev/null 2>&1 && echo podman || echo docker)}; \
	echo "==> Removing openshiho:latest via $$RUNTIME"; \
	$$RUNTIME rmi openshiho:latest 2>/dev/null || true
