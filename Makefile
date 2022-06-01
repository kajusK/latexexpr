.PHONY: tests build publish docs

build: tests
	python3 -m build

tests:
	pytest

publish:
	twine upload --skip-existing dist/*

docs:
	sphinx-build docs_src docs
