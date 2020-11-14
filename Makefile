.PHONY: backend
backend:
	find . | grep -E "(__pycache__|\.pyc|\.pyo|\.pytest_cache)" | xargs rm -rf
	rm -Rf backend/api/migrations
	black backend/*/*.py
	# cd .. && tox && cd ..
	coverage erase
	coverage run -m pytest ./backend -v
	coverage report -m
	coverage html

.PHONY: setup
setup:
	python3 backend/manage.py makemigrations api
	python3 backend/manage.py migrate

.PHONY: start
start:
	python3 backend/manage.py runserver 8000