#!/bin/bash
set -e

echo "Installing system dependencies for Doppler CLI..."
sudo apt-get update
sudo apt-get install -y gpgv

echo "Installing Doppler CLI..."
curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh | sudo sh

echo "Installing Docker CLI..."
sudo apt-get install -y docker.io

echo "Configuring Docker permissions..."
sudo usermod -aG docker vscode || true
sudo chmod 666 /var/run/docker.sock || true

echo "Installing GitHub CLI Agentic Workflows extension..."
gh extension install github/gh-aw

echo "Installing Poetry..."
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
export PATH="/home/vscode/.local/bin:$PATH"
echo 'export PATH="/home/vscode/.local/bin:$PATH"' >> ~/.bashrc

echo "Configuring Poetry..."
poetry config virtualenvs.in-project true

echo "Installing project dependencies with all extras..."
poetry install --all-extras

echo "Installing Playwright browsers with system dependencies using poe..."
poetry run poe install-browsers
poetry run playwright install-deps chromium

echo "Setup complete!"
echo ""
echo "Installed versions:"
poetry --version
doppler --version
docker --version
gh --version
gh extension list
poetry run playwright --version
