#!/bin/bash

# Function to install Docker on Linux
install_docker_linux() {
    sudo apt-get update
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    sudo usermod -aG docker $USER
}

# Function to install Docker on macOS
install_docker_macos() {
    brew install --cask docker
    open /Applications/Docker.app
    echo "Please follow the instructions to set up Docker on macOS."
}

# Function to install Docker on Windows
install_docker_windows() {
    echo "Please install Docker Desktop for Windows from the official website: https://www.docker.com/products/docker-desktop"
    start https://www.docker.com/products/docker-desktop
}

# Function to install Docker Compose on Linux
install_docker_compose_linux() {
    sudo curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep -oP '(?<="tag_name": ")[^"]*')" /docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
}

# Function to install Docker Compose on macOS (Docker Desktop includes Docker Compose)
install_docker_compose_macos() {
    echo "Docker Desktop for macOS includes Docker Compose."
}

# Function to install Docker Compose on Windows (Docker Desktop includes Docker Compose)
install_docker_compose_windows() {
    echo "Docker Desktop for Windows includes Docker Compose."
}

# Check the OS and install Docker and Docker Compose accordingly
case "$(uname -s)" in
    Linux*)
        echo "Detected Linux OS"
        if ! [ -x "$(command -v docker)" ]; then
            install_docker_linux
        else
            echo "Docker already installed."
        fi
        if ! [ -x "$(command -v docker-compose)" ]; then
            install_docker_compose_linux
        else
            echo "Docker Compose already installed."
        fi
        ;;
    Darwin*)
        echo "Detected macOS"
        if ! [ -x "$(command -v docker)" ]; then
            install_docker_macos
        else
            echo "Docker already installed."
        fi
        if ! [ -x "$(command -v docker-compose)" ]; then
            install_docker_compose_macos
        else
            echo "Docker Compose already installed."
        fi
        ;;
    MINGW*|MSYS*|CYGWIN*)
        echo "Detected Windows OS"
        if ! [ -x "$(command -v docker)" ]; then
            install_docker_windows
        else
            echo "Docker already installed."
        fi
        if ! [ -x "$(command -v docker-compose)" ]; then
            install_docker_compose_windows
        else
            echo "Docker Compose already installed."
        fi
        ;;
    *)
        echo "Unknown OS"
        exit 1
        ;;
esac

# Ensure Docker is running (for Linux)
if [[ "$(uname -s)" == "Linux" ]]; then
    sudo systemctl start docker
    sudo systemctl enable docker
fi

# Build and run Docker containers
echo "Building and running Docker containers..."
docker-compose up --build -d

# Wait for containers to be ready
echo "Waiting for containers to be ready..."
sleep 10

# Apply database migrations
echo "Applying database migrations..."
docker-compose exec web flask db upgrade

# Open the application in the default web browser
if command -v xdg-open &> /dev/null
then
    xdg-open http://localhost:8000
elif command -v open &> /dev/null
then
    open http://localhost:8000
elif command -v start &> /dev/null
then
    start http://localhost:8000
fi

echo "Setup complete. Your Flask app should now be running on http://localhost:8000"
