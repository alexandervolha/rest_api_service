IMAGE_NAME:=alexvolha/rest_api

build:
	docker build -f docker/Dockerfile -t $(IMAGE_NAME):base .

build_prod:
	docker build -f docker/Dockerfile.prod -t $(IMAGE_NAME):latest .

test:
	docker run --rm -it -v $(shell pwd)/rest_api_service:/app/rest_api_service:ro -v $(shell pwd)/tests:/app/tests:ro $(IMAGE_NAME):base bash -c "pytest -vv --disable-warnings tests/ $(ARGS)"

push:
	docker push alexvolha/rest_api:latest
