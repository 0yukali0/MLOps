FROM alpine AS builder
WORKDIR /tools
RUN wget https://github.com/dolthub/doltgresql/releases/download/v0.52.3/doltgresql-linux-amd64.tar.gz
RUN tar -zxvf doltgresql-linux-amd64.tar.gz


FROM postgres:15.14-alpine
COPY --from=builder /tools/doltgresql-linux-amd64/bin/doltgres /usr/local/bin