.PHONY: backend
backend:
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	black backend/*/*.py
	# cd .. && tox && cd ..
	coverage erase
	coverage run --source=backend -m pytest -v
	coverage report -m
	coverage html