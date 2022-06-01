.PHONY: tests build publish docs

build: tests
	python3 -m build

tests:
	pytest

publish: build tests
	twine upload dist/*

docs:
	sphinx-build docs_src docs
