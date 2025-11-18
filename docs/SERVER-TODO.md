# Server Implementation TODO

This file tracks implementation of the nginx documentation preview server as detailed in SERVER-PLAN.md.

## Phase 1: Nginx Container Setup

### Task 1.1: Create nginx Dockerfile
- [ ] Create `docker/nginx/` directory
- [ ] Create `docker/nginx/Dockerfile` with nginx:alpine base
- [ ] Configure to expose port 8080

**Test**: Build the image successfully
```bash
docker build -t docs-nginx docker/nginx/
```

### Task 1.2: Create nginx configuration
- [ ] Create `docker/nginx/nginx.conf`
- [ ] Configure server to listen on port 8080
- [ ] Set root to `/usr/share/nginx/html`
- [ ] Add `try_files $uri $uri/ $uri/index.html =404;` for directory handling
- [ ] Enable access and error logging
- [ ] Set appropriate cache headers

**Test**: Verify configuration syntax
```bash
docker run --rm -v $(pwd)/docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro nginx:alpine nginx -t
```

### Task 1.3: Add docs-nginx service to docker-compose.yml
- [ ] Add `docs-nginx` service definition
- [ ] Mount `./site:/usr/share/nginx/html:ro`
- [ ] Map port 8080:8080

**Test**: Start service with dummy content
```bash
mkdir -p site
echo "<h1>Test</h1>" > site/index.html
docker compose up docs-nginx
curl http://localhost:8080
```

**Success Criteria**:
- Returns "Test" heading
- No errors in nginx logs
- Service stops cleanly with Ctrl+C

## Phase 1.5: Dependency Verification

### Task 1.5.1: Create requirements.txt
- [ ] Create `docker/builder/` directory
- [ ] Create `docker/builder/requirements.txt`
- [ ] Add mkdocs==1.6.0
- [ ] Add mkdocs-material[privacy]==9.5.0
- [ ] Add mkdocs-macros-plugin==1.0.5
- [ ] Add mkdocs-monorepo-plugin==1.1.0
- [ ] Add mkdocs-minify-plugin==0.8.0
- [ ] Add mkdocs-caption==1.1.0
- [ ] Add pymdown-extensions==10.10.0
- [ ] Add markdown-tables-extended==1.0.0

**Test**: File exists and contains all entries
```bash
test -f docker/builder/requirements.txt
grep -c "^mkdocs" docker/builder/requirements.txt  # Should be >= 6
```

### Task 1.5.2: Create builder Dockerfile
- [ ] Create `docker/builder/Dockerfile`
- [ ] Use `python:3.12-slim` as base
- [ ] Install git system package
- [ ] Copy requirements.txt to /tmp/
- [ ] Install Python packages with `pip install --no-cache-dir -r /tmp/requirements.txt`
- [ ] Add verification command to test imports
- [ ] Set working directory to `/workspace`

**Test**: Build image successfully
```bash
docker build -t mkdocs-builder-test docker/builder/
```

### Task 1.5.3: Verify all imports work
- [ ] Test mkdocs import
- [ ] Test material import
- [ ] Test mkdocs_macros import
- [ ] Test mkdocs_monorepo_plugin import
- [ ] Test mkdocs_minify_plugin import
- [ ] Test mkdocs_caption import
- [ ] Test pymdownx import
- [ ] Test markdown_tables_extended import

**Test**: Run import verification
```bash
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
```

**Success Criteria**:
- All imports succeed without ModuleNotFoundError
- Prints "All imports successful"

### Task 1.5.4: Verify mkdocs CLI works
- [ ] Test mkdocs command is available
- [ ] Verify version output

**Test**: Check mkdocs version
```bash
docker run --rm mkdocs-builder-test mkdocs --version
```

**Success Criteria**:
- Command executes without error
- Outputs version information

## Phase 2: MkDocs Builder Container

### Task 2.1: Create builder entrypoint script
- [ ] Create `docker/builder/entrypoint.sh`
- [ ] Make script executable (chmod +x)
- [ ] Add shebang `#!/bin/sh`
- [ ] Change to `/workspace` directory
- [ ] Set CURRENT_YEAR environment variable
- [ ] Set BUILD_DATE environment variable
- [ ] Set GIT_INFO environment variable (handle case where .git not mounted)
- [ ] Run `mkdocs build --site-dir /site`
- [ ] Log completion message
- [ ] Exit with mkdocs exit code

**Test**: Check script syntax
```bash
sh -n docker/builder/entrypoint.sh
```

### Task 2.2: Update builder Dockerfile for entrypoint
- [ ] Copy entrypoint.sh to `/usr/local/bin/`
- [ ] Make entrypoint.sh executable in Dockerfile
- [ ] Set CMD to run entrypoint.sh

**Test**: Build updated image
```bash
docker build -t mkdocs-builder docker/builder/
```

### Task 2.3: Add docs-builder service to docker-compose.yml
- [ ] Add `docs-builder` service definition
- [ ] Use build context `./docker/builder`
- [ ] Mount `./dyalog-docs:/workspace:ro`
- [ ] Mount `./site:/site`
- [ ] Set appropriate command

**Test**: Verify service definition
```bash
docker compose config | grep -A 10 docs-builder
```

### Task 2.4: Test full build process
- [ ] Remove any existing site directory
- [ ] Run builder service
- [ ] Verify no errors in build output
- [ ] Check site directory created
- [ ] Verify index.html exists
- [ ] Check for expected subdirectories

**Test**: Run build and verify output
```bash
rm -rf site/
docker compose run --rm docs-builder
test -f site/index.html
find site/ -name "index.html" | wc -l  # Should be > 1
```

**Success Criteria**:
- Build completes without errors
- site/ directory contains HTML files
- Multiple index.html files present (main + subsites)
- Build time under 5 minutes

### Task 2.5: Verify environment variables in output
- [ ] Check CURRENT_YEAR appears in generated HTML
- [ ] Check BUILD_DATE appears in generated HTML
- [ ] Check GIT_INFO appears in generated HTML (if .git available)

**Test**: Search for environment variables
```bash
grep -r "$(date +%Y)" site/ | head -3
grep -r "UTC" site/ | head -3
```

**Success Criteria**:
- Current year found in generated files
- Build date found in generated files

## Phase 3: Integration and Orchestration

### Task 3.1: Add service dependencies
- [ ] Configure docs-nginx to depend on docs-builder
- [ ] Use `depends_on` with `service_completed_successfully` condition

**Test**: Verify dependency configuration
```bash
docker compose config | grep -A 5 "depends_on"
```

### Task 3.2: Add health check to docs-builder
- [ ] Define health check that tests for /site/index.html
- [ ] Set appropriate interval and timeout

**Test**: Run builder and check health status
```bash
docker compose up -d docs-builder
docker compose ps docs-builder  # Check health status
docker compose down
```

### Task 3.3: Add health check to docs-nginx
- [ ] Install curl in nginx container (or use wget)
- [ ] Define health check for http://localhost:8080
- [ ] Set interval: 5s, timeout: 3s, retries: 3

**Test**: Verify nginx health check
```bash
docker compose up -d docs-nginx
sleep 10
docker compose ps docs-nginx  # Should show healthy
docker compose down
```

### Task 3.4: Test complete workflow from clean state
- [ ] Remove site directory
- [ ] Stop all containers
- [ ] Run `docker compose up docs-nginx`
- [ ] Wait for services to be ready
- [ ] Verify nginx serves content

**Test**: Full integration test
```bash
docker compose down -v
rm -rf site/
docker compose up -d docs-nginx
sleep 30  # Wait for build
curl http://localhost:8080
curl http://localhost:8080/language-reference-guide/
docker compose down
```

**Success Criteria**:
- Single command starts both services
- Builder completes before nginx starts serving
- Root page accessible
- Sub-site pages accessible
- No errors in logs

### Task 3.5: Verify monorepo cross-site links
- [ ] Identify pages with cross-site links in dyalog-docs
- [ ] Test those specific URLs
- [ ] Verify links resolve correctly

**Test**: Check cross-site navigation
```bash
# Find a page with cross-site links and test it
curl -I http://localhost:8080/language-reference-guide/some/cross/link/page/
```

**Success Criteria**:
- Cross-site links return 200 OK
- No 404 errors for inter-site navigation

### Task 3.6: Create convenience script
- [ ] Create `docker/scripts/` directory
- [ ] Create `docker/scripts/serve.sh`
- [ ] Make script executable
- [ ] Add logic to build if site/ missing
- [ ] Start nginx service
- [ ] Follow logs

**Test**: Run script from clean state
```bash
rm -rf site/
bash docker/scripts/serve.sh
# Verify in another terminal:
curl http://localhost:8080
```

**Success Criteria**:
- Script builds site automatically
- Nginx starts and serves content
- User sees logs indicating readiness

## Final Validation

### Task 4.1: Run complete test suite
- [ ] Clean all containers and volumes
- [ ] Remove site directory
- [ ] Run pytest unit tests
- [ ] Verify no regressions

**Test**: Full regression test
```bash
docker compose down -v
rm -rf site/
uv run pytest
```

**Success Criteria**:
- All existing tests pass
- No regressions introduced

### Task 4.2: Integration test script
- [ ] Create `tests/integration/test_docker_compose.py`
- [ ] Test builder service runs successfully
- [ ] Test site directory is populated
- [ ] Test nginx serves root page
- [ ] Test nginx serves sub-pages
- [ ] Test environment variables in output

**Test**: Run integration tests
```bash
uv run pytest tests/integration/test_docker_compose.py -v
```

**Success Criteria**:
- All integration tests pass
- Build time under 5 minutes
- No container errors

### Task 4.3: Documentation and cleanup
- [ ] Update main README if needed
- [ ] Remove any temporary test files
- [ ] Verify no debugging code left in source
- [ ] Ensure all scripts have proper permissions

**Test**: Review checklist
```bash
git status  # Check for untracked files
find docker/ -type f -name "*.sh" -exec test -x {} \; -print  # Verify scripts executable
```

## Notes

- Each task should be completed and tested before moving to the next
- Commit working code after each phase
- If any test fails, fix before proceeding
- Update this TODO as implementation progresses
