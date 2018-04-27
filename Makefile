compose:
	cp docker-compose.yml.template docker-compose.yml

exec:
	docker-compose exec art-backend /bin/bash -it

open:
	open http://0.0.0.0:8080/admin
