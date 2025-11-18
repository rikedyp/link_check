FROM python:3.12-slim

# Install git (required by mkdocs-monorepo-plugin)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Set working directory
WORKDIR /workspace

# Verify all imports work
RUN python -c "import mkdocs; import material; import mkdocs_macros; import mkdocs_monorepo_plugin; import mkdocs_minify_plugin; import mkdocs_caption; import pymdownx; import markdown_tables_extended; print('All imports successful')"

# Verify mkdocs CLI works
RUN mkdocs --version
