PYTHON ?= $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)

.PHONY: test demo privacy-scan schema-check link-check dependency-check validate ci

test:
	$(PYTHON) -m pytest

demo:
	$(PYTHON) -m src.demo

privacy-scan:
	$(PYTHON) scripts/privacy_scan.py

schema-check:
	$(PYTHON) scripts/validate_schema.py

link-check:
	$(PYTHON) scripts/check_markdown_links.py

dependency-check:
	$(PYTHON) -m pip check

validate: privacy-scan schema-check link-check dependency-check test demo

ci: validate
