# Start from Ubuntu
FROM ubuntu:latest

# Update and install vim and curl
RUN apt-get update && apt-get install -y \
    vim \
    curl

# Keep the container running
CMD ["tail", "-f", "/dev/null"]
