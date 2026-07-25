FROM ubuntu:22.04

# Avoid interactive prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# Install only the runtime dependencies wisecow.sh needs
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        fortune-mod \
        fortunes-min \
        cowsay \
        netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# cowsay installs to /usr/games — add it to PATH
ENV PATH="/usr/games:${PATH}"

WORKDIR /app

COPY wisecow.sh .
# Strip Windows CRLF line endings (git on Windows checks out \r\n)
RUN sed -i 's/\r$//' wisecow.sh && chmod +x wisecow.sh

EXPOSE 4499

CMD ["./wisecow.sh"]
