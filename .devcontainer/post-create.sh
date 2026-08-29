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
# Pin the installer script itself to a specific commit SHA of the
# upstream python-poetry/install.python-poetry.org repo (with a
# checksum check) rather than the mutable install.python-poetry.org
# endpoint, consistent with how GitHub Actions are pinned by commit SHA
# elsewhere in this repo.
POETRY_INSTALLER_SHA="de1ef28b5fe8d5b6dd1353827d06c14f796fd230"
POETRY_INSTALLER_SHA256="75745ca71373a7b22fa150953543f03d826a52f8e4bc4350328a33bddd668026"
POETRY_INSTALLER_PATH="$(mktemp)"
trap 'rm -f "${POETRY_INSTALLER_PATH}"' EXIT
curl -fsSL --tlsv1.2 --proto "=https" --retry 3 \
  "https://raw.githubusercontent.com/python-poetry/install.python-poetry.org/${POETRY_INSTALLER_SHA}/install-poetry.py" \
  -o "${POETRY_INSTALLER_PATH}"
echo "${POETRY_INSTALLER_SHA256}  ${POETRY_INSTALLER_PATH}" | sha256sum -c -
python3 "${POETRY_INSTALLER_PATH}" --version 2.4.1

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
