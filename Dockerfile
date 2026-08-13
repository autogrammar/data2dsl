FROM alpine:3.22.1

WORKDIR /workspace
COPY README.md VERSION ./

CMD ["sh", "-c", "test -s README.md && test -s VERSION"]
