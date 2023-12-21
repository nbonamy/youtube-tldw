build:
	docker build --tag youtube-tldw:latest --label youtube-tldw .

run:
	@-docker rm -f youtube-tldw > /dev/null 2>&1
	docker run -d -p 5555:5555 --name youtube-tldw youtube-tldw:latest

all: build run
