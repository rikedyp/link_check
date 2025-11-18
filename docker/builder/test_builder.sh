#!/usr/bin/env bash
set -e

echo "Building mkdocs-builder-test image..."
docker build -t mkdocs-builder-test docker/builder/

echo ""
echo "Testing Python imports..."
docker run --rm mkdocs-builder-test python -c "import mkdocs; import material; import mkdocs_macros; import mkdocs_monorepo_plugin; import mkdocs_minify_plugin; import mkdocs_caption; import pymdownx; import markdown_tables_extended; print('All imports successful')"

echo ""
echo "Testing mkdocs CLI..."
docker run --rm mkdocs-builder-test mkdocs --version

echo ""
echo "All builder verification tests passed!"
