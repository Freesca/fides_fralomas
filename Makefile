
MATCHMAKING_SERVICE_PORT=9001
GAME_SERVICE_PORT=9002
USER_SERVICE_PORT=9003

all:docker-up

docker-up-build:
	docker-compose up --build -d
	docker-compose logs
docker-up:
	docker-compose up
	docker-compose logs
docker-up-detached:
	docker-compose up -d

docker-down:
	docker-compose down
docker-rm:
	docker-compose down -v --rmi all

docker-logs:
	docker-compose logs
docker-ps:
	docker-compose ps


script-init:
	chmod +x init-python.sh
	./init-python.sh
	make script-init-services
	make script-init-frontend
script-init-services:
	cd matchmaking_microservice && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd pong_game_microservice && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd user_menagement_microservice && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
script-init-frontend:
	cd pong_frontend && npm install

script-run-all:
	make script-run-matchmaking_service &
	make script-run-game_service &
	make script-run_user_service &
	make script-run-frontend &

script-run-matchmaking_service:
	cd matchmaking_microservice && source venv/bin/activate && python manage.py runserver 0.0.0.0:${MATCHMAKING_SERVICE_PORT}
script-run-game_service:
	cd pong_game_microservice && source venv/bin/activate && python manage.py runserver 0.0.0.0:${GAME_SERVICE_PORT}
script-run-user_service:
	cd user_menagement_microservice && source venv/bin/activate && python manage.py runserver 0.0.0.0:${USER_SERVICE_PORT}

script-run-frontend:
	cd pong_frontend && npm run dev

get-last-sent-email:
	@cat "user_menagement_microservice/sent_emails/$(shell ls user_menagement_microservice/sent_emails/ | tail -n 1)"