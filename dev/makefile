CWD := $(shell pwd)
DEV_DIR := $(realpath $(dir $(firstword $(MAKEFILE_LIST))))
VENV := $(DEV_DIR)/venv
IMAGE := charon:local

$(VENV):
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip

.PHONY: install
venv-install: $(VENV)
	$(VENV)/bin/pip install -e ..

.PHONY: docker-build
docker-build:
	docker build -t $(IMAGE) ..

.PHONY: run-tests
run-tests: #docker-build
	docker run --rm -v $(DEV_DIR)/tests/charon.test.yml:/test/charon.test.yml -v $(DEV_DIR)/tests/test.sh:/test/test.sh -w /test $(IMAGE) ./test.sh
	docker run --rm -v $(DEV_DIR)/tests/charon.test.yml:/test/charon.test.yml -v $(DEV_DIR)/tests/test2.sh:/test/test.sh -w /test $(IMAGE) ./test.sh
	docker run --rm -v $(DEV_DIR)/tests/charon.test.yml:/test/charon.test.yml -v $(DEV_DIR)/tests/test3.sh:/test/test.sh -w /test $(IMAGE) ./test.sh
	docker run --rm -v $(DEV_DIR)/tests/charon.test.yml:/test/charon.test.yml -v $(DEV_DIR)/tests/test4.sh:/test/test.sh -w /test $(IMAGE) ./test.sh
	docker run --rm -v $(DEV_DIR)/tests/charon.test.yml:/test/charon.test.yml -v $(DEV_DIR)/tests/test5.sh:/test/test.sh -w /test $(IMAGE) ./test.sh
