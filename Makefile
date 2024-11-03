.PHONY : install test coverage release

install:
	python3 -m venv .venv && \
	source .venv/bin/activate && \
	pip install -r requirements.txt

test:
	ruff check . && \
	python3 -m unittest

coverage:
	coverage run --branch -m unittest
	coverage html
	open htmlcov/index.html

release:
	.github/release.sh ${bump}
