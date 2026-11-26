# Isolated Shepherdr + herdr-core for CLI evidence capture (plan T1) and the switch matrix (T9).
# Nothing from the real user's HOME, XDG dirs or sockets is mounted; every container starts empty.
# Build: eval/shepherdr-env/run.sh build TAG   (TAG = v3.1.26 | v3.2.19)
FROM ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 git ca-certificates curl unzip procps tmux jq \
    && rm -rf /var/lib/apt/lists/*
ARG TAG
# hc is the host's herdr-core binary (static), copied in by run.sh as build context.
COPY hc /usr/local/bin/herdr-core
RUN ln -s herdr-core /usr/local/bin/hc
# shortcut: tailscale/systemctl --user are stubs; the web app is out of scope, only the herdr-task/hc contract is captured.
COPY stubs/ /usr/local/bin/
RUN useradd -m -s /bin/bash tester
USER tester
WORKDIR /home/tester
RUN git clone -q https://github.com/eliasstravik/shepherdr.git /home/tester/shepherdr \
    && git -C /home/tester/shepherdr checkout -q "$TAG" \
    && git config --global user.email tester@example.invalid && git config --global user.name tester \
    && git config --global init.defaultBranch main
ENV PATH=/home/tester/.local/bin:$PATH
# 3.1 is a Herdr-app layout: it needs the app's home dir and --force without the app; 3.2 installs plainly.
# The service (bun) and the web app are left out on purpose.
RUN cd /home/tester/shepherdr && case "$TAG" in \
      v3.1.*) mkdir -p ~/.config/herdr-app && ./install.sh --no-hooks --no-build --yes --force ;; \
      *) ./install.sh --no-hooks --no-build --yes ;; \
    esac > /home/tester/install.log 2>&1 && command -v herdr-task
