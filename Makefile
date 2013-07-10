publish:
  @if [ -e "$$HOME/.pypirc" ]; then \
		echo "Uploading to Pypi"; \
		python setup.py register ; \
		python setup.py sdist upload ; \
