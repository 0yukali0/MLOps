FROM alpine AS builder
WORKDIR /tools
RUN wget https://github.com/dolthub/doltgresql/releases/download/v0.52.3/doltgresql-linux-amd64.tar.gz
RUN tar -zxvf doltgresql-linux-amd64.tar.gz

FROM ubuntu:24.04
RUN apt update && \
    apt install postgresql postgresql-contrib -y && \
    rm -rf /var/lib/apt/lists/*
COPY --from=builder /tools/doltgresql-linux-amd64/bin/doltgres /usr/local/bin
USER postgres
WORKDIR /postgres
ENTRYPOINT doltgres --data-dir=.