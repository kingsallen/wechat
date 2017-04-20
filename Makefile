.PHONY: all test cleanup

all:
	python ./app.py --port=9301 --env=platform --logpath=/tmp/

test:
	python -m unittest discover -v

cleanup:
	rm -r `ls | grep -v '.env'`
