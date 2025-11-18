# Nginx Documentation Preview Server Implementation Plan

## Overview

Build a Docker Compose-based documentation preview tool using nginx to serve pre-built MkDocs sites. This replaces the existing `mkdocs serve` approach with a production-grade web server suitable for fast link checking.

## Key Requirements

1. Use nginx (not mkdocs serve) for serving static HTML
2. Build MkDocs site at container runtime, not during image build
3. Mount source files rather than copying into container
4. Enable fast link checking via Docker internal networking
5. Support the monorepo plugin structure
6. Output compatible with existing docs team YAML tooling

## Dependency Management

### Identifying Required Packages

From analysing `dyalog-docs/mkdocs.yml`, the following dependencies are required:

**Core MkDocs**:
- `mkdocs` - Core documentation builder
- `mkdocs-material` - Material theme (referenced in `theme.name`)

**Plugins** (from `plugins:` section):
- `mkdocs-material[privacy]` - Privacy plugin (part of material extras)
- `mkdocs-macros-plugin` - Macros plugin for variables
- `mkdocs-monorepo-plugin` - Monorepo support (critical for cross-site links)
- `mkdocs-minify-plugin` - HTML minification
- `mkdocs-caption` - Table/figure captions

**Markdown Extensions** (from `markdown_extensions:` section):
- `pymdown-extensions` - Provides: details, keys, superfences, arithmatex, highlight
- `markdown-tables-extended` - Extended table support

### Ensuring Correctness

**Strategy 1: Pin Versions in requirements.txt**

Create `docker/builder/requirements.txt` with pinned versions:
```txt
mkdocs==1.6.0
mkdocs-material[privacy]==9.5.0
mkdocs-macros-plugin==1.0.5
mkdocs-monorepo-plugin==1.1.0
mkdocs-minify-plugin==0.8.0
mkdocs-caption==1.1.0
pymdown-extensions==10.10.0
markdown-tables-extended==1.0.0
```

**Strategy 2: Test Build During Phase 2**

The Phase 2 test explicitly validates that the build succeeds:
```bash
docker compose run --rm docs-builder
```

If plugins are missing or incompatible, mkdocs will fail with clear error messages like:
- `ModuleNotFoundError: No module named 'mkdocs_macros'`
- `Plugin 'monorepo' not found`
- `Invalid configuration: markdown_extensions: 'markdown_tables_extended' is not a valid extension`

**Strategy 3: Dockerfile Verification**

Add verification step in `docker/builder/Dockerfile`:
```dockerfile
RUN python -c "import mkdocs; import material; import mkdocs_macros; import mkdocs_monorepo_plugin; import mkdocs_minify_plugin; import mkdocs_caption; import pymdownx; import markdown_tables_extended" && \
    mkdocs --version
```

This ensures all imports succeed during image build.

**Strategy 4: Separate Test Phase**

Phase 1.5 (Dependency Verification) explicitly tests all dependencies before attempting the full build.

### Version Pinning Strategy

**Initial approach**: Use latest compatible versions initially, then pin after successful build.

**Lock file**: After first successful build, run:
```bash
docker compose run --rm docs-builder pip freeze > docker/builder/requirements.lock
```

Then update Dockerfile to install from lock file for reproducible builds.

### Docker Build Caching

To optimise rebuild times for the builder container:

1. **Layer ordering**: Copy requirements.txt before copying other files
2. **Pip cache**: Use `pip install --no-cache-dir` to reduce image size but rely on Docker layer caching
3. **Multi-stage build** (optional): Separate dependency installation from runtime

Example Dockerfile structure for optimal caching:
```dockerfile
FROM python:3.12-slim

# Install system dependencies (cached unless Dockerfile changes)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies (cached unless requirements.txt changes)
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application files (changes frequently, comes last)
COPY entrypoint.sh /usr/local/bin/
...
```

This ensures Python packages aren't reinstalled on every Dockerfile change.

### Handling Missing or Incompatible Plugins

If build fails in Phase 2:
1. Check error message for missing module name
2. Search PyPI for correct package name (e.g., `mkdocs-monorepo-plugin` vs `mkdocs-monorepo`)
3. Add to requirements.txt
4. Rebuild and retest
5. Document any package name differences in this plan

## Architecture

```
docker-compose.yml
├── docs-builder (service)
│   └── Builds MkDocs site into shared volume
├── docs-nginx (service)
│   └── Serves built site via nginx
└── link-checker (service)
    └── Checks links against docs-nginx
```

### Shared Volumes

- `./dyalog-docs:/workspace` (source files, read-only mount)
- `./site:/site` (built HTML, bind-mounted to local directory for inspection)

## Implementation Phases

### Phase 1: Nginx Container Setup

**Goal**: Create nginx service that serves static HTML from a volume.

**Tasks**:
1. Create `docker/nginx/Dockerfile`
   - Base: `nginx:alpine`
   - Copy custom nginx configuration
   - Expose port 8080
2. Create `docker/nginx/nginx.conf`
   - Configure to serve from `/usr/share/nginx/html`
   - Add logging for debugging
   - Set appropriate cache headers
   - MkDocs generates directories with index.html files (e.g., `/path/to/page/index.html`)
   - Use try_files to serve `/path/to/page` or `/path/to/page/` correctly
   - Example: `try_files $uri $uri/ $uri/index.html =404;`
3. Add `docs-nginx` service to `docker-compose.yml`
   - Mount `./site:/usr/share/nginx/html:ro` (bind-mount, read-only)
   - Expose port 8080 to host

**Test**:
```bash
# Create dummy HTML in site directory
mkdir -p site
echo "<h1>Test</h1>" > site/index.html

# Start nginx
docker compose up docs-nginx

# Verify in browser or curl
curl http://localhost:8080
```

**Success Criteria**:
- Nginx serves static HTML files
- Accessible on localhost:8080
- No errors in nginx logs

### Phase 1.5: Dependency Verification

**Goal**: Verify all MkDocs dependencies install correctly.

**Tasks**:
1. Create `docker/builder/requirements.txt` with all identified dependencies
2. Create `docker/builder/Dockerfile` for testing
   - Base: `python:3.12-slim`
   - Install `git` (required for GIT_INFO environment variable)
   - Copy requirements.txt
   - Install Python dependencies with pip cache for faster rebuilds
   - Add verification command
3. Build test image and verify imports
4. Run `mkdocs --version` to confirm installation

**Test**:
```bash
# Build builder image
docker build -t mkdocs-builder-test docker/builder/

# Test imports
docker run --rm mkdocs-builder-test python -c "
import mkdocs
import material
import mkdocs_macros
import mkdocs_monorepo_plugin
import mkdocs_minify_plugin
import mkdocs_caption
import pymdownx
import markdown_tables_extended
print('All imports successful')
"

# Verify mkdocs works
docker run --rm mkdocs-builder-test mkdocs --version
```

**Success Criteria**:
- All Python imports succeed
- mkdocs command executes
- No import errors or missing modules
- Build completes in reasonable time

### Phase 2: MkDocs Builder Container

**Goal**: Create service that builds MkDocs site into shared volume.

**Tasks**:
1. Update `docker/builder/Dockerfile` (from Phase 1.5)
   - Add working directory `/workspace`
   - Copy entrypoint script
2. Create `docker/builder/entrypoint.sh`
   - Change to `/workspace` directory
   - Set environment variables:
     - `CURRENT_YEAR=$(date +%Y)`
     - `BUILD_DATE=$(date -u +"%Y-%m-%d %H:%M:%S UTC")`
     - `GIT_INFO=$(git rev-parse --short HEAD) $(git log -1 --format='%s')`
   - Run `mkdocs build --site-dir /site`
   - Log completion message
3. Add `docs-builder` service to `docker-compose.yml`
   - Mount `./dyalog-docs:/workspace:ro` (read-only)
   - Mount `./site:/site` (bind-mount for inspection)
   - Run entrypoint script
4. Install `git` in builder Dockerfile (needed for GIT_INFO variable)

**Test**:
```bash
# Build the site
docker compose run --rm docs-builder

# Verify site directory populated locally
ls -la site/

# Check for index.html and directory structure
find site/ -name "index.html" | head -10

# Verify environment variables were set
grep -r "$(date +%Y)" site/ | head -5
```

**Success Criteria**:
- MkDocs builds without errors
- HTML files present in `./site` directory (inspectable locally)
- Environment variables (CURRENT_YEAR, BUILD_DATE, GIT_INFO) appear in generated HTML
- Build completes in reasonable time (<5 minutes)

### Phase 3: Integration and Orchestration

**Goal**: Coordinate builder and nginx services.

**Tasks**:
1. Add dependency in `docker-compose.yml`
   - Make `docs-nginx` depend on `docs-builder`
   - Use `depends_on` with health checks
2. Add health check to `docs-builder`
   - Check for `/site/index.html` existence
3. Add health check to `docs-nginx`
   - Curl against http://localhost:8080
4. Create convenience script `docker/scripts/serve.sh`
   - Build if needed
   - Start nginx
   - Show logs

**Test**:
```bash
# Full workflow
docker compose down -v  # Clean slate
docker compose up docs-nginx

# Wait for build completion, then verify
curl http://localhost:8080
curl http://localhost:8080/language-reference-guide/
curl http://localhost:8080/interface-guide/
```

**Success Criteria**:
- Single command starts both services
- Nginx waits for build completion
- All mkdocs sites accessible
- Cross-site links work correctly
- Monorepo structure preserved

### Phase 4: Link Checker Container Stub

**Goal**: Create minimal link checker that validates the server is working.

**Tasks**:
1. Create `link_check/cli.py`
   - Argument parsing for `--base-url`, `--output`
   - Simple HTTP GET to base URL
   - Report success/failure
2. Create `docker/link-checker/Dockerfile`
   - Base: `python:3.12-slim`
   - Copy link_check package
   - Install requests library
   - Set entrypoint to cli.py
3. Add `link-checker` service to `docker-compose.yml`
   - Network: same as docs-nginx
   - No port exposure needed (uses internal network)
   - Mount for output: `./reports:/reports`

**Test**:
```bash
# Start nginx
docker compose up -d docs-nginx

# Run link checker stub
docker compose run --rm link-checker \
    --base-url http://docs-nginx:8080 \
    --output /reports/test.yaml

# Check output
cat reports/test.yaml
```

**Success Criteria**:
- Link checker connects to nginx via internal network
- Base URL returns HTTP 200
- YAML output file created
- Sub-second execution time

## Docker Compose Structure

```yaml
services:
  docs-builder:
    build: ./docker/builder
    volumes:
      - ./dyalog-docs:/workspace:ro
      - ./site:/site
    command: ["./entrypoint.sh"]

  docs-nginx:
    build: ./docker/nginx
    ports:
      - "8080:8080"
    volumes:
      - ./site:/usr/share/nginx/html:ro
    depends_on:
      docs-builder:
        condition: service_completed_successfully
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080"]
      interval: 5s
      timeout: 3s
      retries: 3
```

## Testing Strategy

### Per Phase Testing

Each phase includes specific tests to validate functionality before proceeding. Tests should be:
- Automated where possible
- Documented in phase description
- Reproducible from clean state
- Quick to run

### Integration Testing

After Phase 3, create `tests/integration/test_docker_compose.py`:
```python
def test_server_workflow():
    """Test complete server workflow (builder + nginx)."""
    # Clean environment (remove site directory)
    # Run builder service
    # Verify site directory populated with HTML
    # Start nginx service
    # Verify nginx serves content correctly
    # Test multiple page paths (root, sub-pages, cross-site links)
    # Verify environment variables in generated HTML
```

### Regression Testing

Before each phase, run full test suite:
```bash
# Clean environment
docker compose down
rm -rf site/

# Run unit tests
uv run pytest

# Test server workflow
docker compose up -d docs-nginx
curl http://localhost:8080
docker compose down
```

## Iteration Process

1. Complete one phase fully before moving to next
2. Commit working code after each phase
3. Update this plan if requirements change
4. Document any deviations in commit messages
5. Run regression tests before each commit

## Success Metrics

- Build time: <5 minutes
