# Use Python 3.11 slim bookworm as base image
FROM python:3.11-slim-bookworm

# Update package lists and install required system packages
RUN apt-get update && apt-get install -y \
    git \
    curl \
    openssh-client \
    sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user 'circuidev'
RUN useradd -m -s /bin/bash circuidev \
    && usermod -aG sudo circuidev \
    && echo 'circuidev ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Set the working directory
WORKDIR /workspace

# Change ownership of workspace to circuidev user
RUN chown -R circuidev:circuidev /workspace

# Switch to the circuidev user
USER circuidev

# Set environment variables
ENV PATH="/workspace/venv/bin:$PATH"
ENV PYTHONPATH="/workspace"
