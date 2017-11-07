requirements:
	@echo "Requirements are installed through edx-platform"

test:
	@echo "Tests are contained in edx-platform. See openedx/tests/xblock_integration/test_review_xblock.py for tests"

quality:
	pip install -r requirements/quality.txt
	pylint --rcfile=pylintrc review
	pep8 --config=pep8 review
