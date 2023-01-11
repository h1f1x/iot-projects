.PHONY: init
init:
	@pipenv install

.PHONY: clean
clean:
	@pipenv --rm
	@pipenv clean

.PHONY: run
run: 
	@echo "+ $@"
	@pipenv run python sim2070iot.py

.PHONY: lint
lint:
	@pipenv run autoflake -ri .
	@pipenv run isort .
	@pipenv run black .

.PHONY: test
test:
	@pipenv run pytest -v .

.PHONY: sync
sync:
	fswatch -o . | xargs -n1 -I{} rsync -av . pi@192.168.178.124:iot-projects/sim2070iot
