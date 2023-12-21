build:
	docker build --tag youtube-tldw:latest --label youtube-tldw .

run:
	docker run -d -p 5555:5555 --name youtube-tldw youtube-tldw:latest
