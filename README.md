# link_check

![Tests](https://github.com/[username]/link_check/workflows/Tests/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-placeholder-brightgreen)

## Description

Placeholder for project description.

## Prerequisites

- Python 3.12 or later
- [uv](https://github.com/astral-sh/uv) (Python package manager)
- Docker and Docker Compose (for documentation preview server)

### Installing uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Installing Docker

Follow the official Docker installation instructions for your platform:
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (recommended for Windows/macOS)
- [Docker Engine](https://docs.docker.com/engine/install/) (Linux)

## Installation

```bash
git clone https://github.com/[username]/link_check.git
cd link_check
uv sync
```

## Usage

Placeholder for usage instructions.

## Testing

### Python Tests

Run the Python test suite:
```bash
uv run pytest
```

Run with verbose output:
```bash
uv run pytest -v
```

### Docker Container Tests

Test the nginx documentation server:
```bash
# Create test content
mkdir -p site
echo "<h1>Test</h1>" > site/index.html

# Start the nginx service
docker compose up docs-nginx

# In another terminal, test the server
curl http://localhost:8080

# Stop the service
docker compose down
```

Test the MkDocs builder container:
```bash
bash docker/builder/test_builder.sh
```

### Code Quality

Check code formatting:
```bash
uv run black --check link_check/ tests/
```

Run linting:
```bash
uv run ruff check link_check/ tests/
```

Format code:
```bash
uv run black link_check/ tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
