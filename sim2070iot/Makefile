.PHONY: run
run: 
	@echo "+ $@"
	@pipenv run python sim2070iot.py

lint:
	@pipenv run autoflake -ri .
	@pipenv run isort .
	@pipenv run black .
