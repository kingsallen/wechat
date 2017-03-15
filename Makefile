all:
	python ./app.py --port=9311 --env=platform --logpath=/tmp/

test:
	python -m unittest discover -v

cleanup:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
