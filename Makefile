run:
	uvicorn main:app --reload

test:
	docker-compose exec backend pytest

build:
	docker-compose build

down:
	docker-compose down

up:
	docker-compose up

exec_backend:
	docker-compose exec backend bash
