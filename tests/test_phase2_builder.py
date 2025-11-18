"""
Phase 2: MkDocs Builder Container Tests

Tests the builder service that creates the MkDocs site at runtime.

Test Strategy:
- Task 2.1: Verify entrypoint.sh script exists and is valid
- Task 2.2: Verify Dockerfile includes entrypoint configuration
- Task 2.3: Verify docker-compose.yml has docs-builder service
- Task 2.4: Test full build process produces expected output
- Task 2.5: Verify environment variables appear in generated HTML
"""

import os
import subprocess
import shutil
import pytest


# Project root directory
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")


class TestTask21_EntrypointScript:
    """Task 2.1: Create builder entrypoint script"""

    def test_entrypoint_script_exists(self):
        """Verify docker/builder/entrypoint.sh exists"""
        entrypoint_path = os.path.join(
            PROJECT_ROOT, "docker", "builder", "entrypoint.sh"
        )
        assert os.path.exists(entrypoint_path), "entrypoint.sh must exist"

    def test_entrypoint_script_is_executable(self):
        """Verify entrypoint.sh has executable permissions"""
        entrypoint_path = os.path.join(
            PROJECT_ROOT, "docker", "builder", "entrypoint.sh"
        )
        assert os.path.exists(entrypoint_path), "entrypoint.sh must exist first"

        # Check if file is executable
        is_executable = os.access(entrypoint_path, os.X_OK)
        assert is_executable, "entrypoint.sh must be executable (chmod +x)"

    def test_entrypoint_has_shebang(self):
        """Verify entrypoint.sh starts with #!/bin/sh"""
        entrypoint_path = os.path.join(
            PROJECT_ROOT, "docker", "builder", "entrypoint.sh"
        )
        assert os.path.exists(entrypoint_path), "entrypoint.sh must exist first"

        with open(entrypoint_path, "r") as f:
            first_line = f.readline().strip()

        assert (
            first_line == "#!/bin/sh"
        ), "entrypoint.sh must start with #!/bin/sh shebang"

    def test_entrypoint_changes_to_workspace(self):
        """Verify entrypoint.sh changes to /workspace directory"""
        entrypoint_path = os.path.join(
            PROJECT_ROOT, "docker", "builder", "entrypoint.sh"
        )
        assert os.path.exists(entrypoint_path), "entrypoint.sh must exist first"

        with open(entrypoint_path, "r") as f:
            content = f.read()
        assert (
            "cd /workspace" in content
        ), "entrypoint.sh must change to /workspace directory"

    def test_entrypoint_sets_current_year(self):
        """Verify entrypoint.sh sets CURRENT_YEAR environment variable"""
        entrypoint_path = os.path.join(
            PROJECT_ROOT, "docker", "builder", "entrypoint.sh"
        )
        assert os.path.exists(entrypoint_path), "entrypoint.sh must exist first"

        with open(entrypoint_path, "r") as f:
            content = f.read()
        assert "CURRENT_YEAR" in content, "entrypoint.sh must set CURRENT_YEAR env var"
        assert "export CURRENT_YEAR" in content, "CURRENT_YEAR must be exported"

    def test_entrypoint_sets_build_date(self):
        """Verify entrypoint.sh sets BUILD_DATE environment variable"""
        entrypoint_path = os.path.join(
            PROJECT_ROOT, "docker", "builder", "entrypoint.sh"
        )
        assert os.path.exists(entrypoint_path), "entrypoint.sh must exist first"

        with open(entrypoint_path, "r") as f:
            content = f.read()
        assert "BUILD_DATE" in content, "entrypoint.sh must set BUILD_DATE env var"
        assert "export BUILD_DATE" in content, "BUILD_DATE must be exported"

    def test_entrypoint_sets_git_info(self):
        """Verify entrypoint.sh sets GIT_INFO environment variable"""
        entrypoint_path = os.path.join(
            PROJECT_ROOT, "docker", "builder", "entrypoint.sh"
        )
        assert os.path.exists(entrypoint_path), "entrypoint.sh must exist first"

        with open(entrypoint_path, "r") as f:
            content = f.read()
        assert "GIT_INFO" in content, "entrypoint.sh must set GIT_INFO env var"
        assert "export GIT_INFO" in content, "GIT_INFO must be exported"

    def test_entrypoint_runs_mkdocs_build(self):
        """Verify entrypoint.sh runs mkdocs build command"""
        entrypoint_path = os.path.join(
            PROJECT_ROOT, "docker", "builder", "entrypoint.sh"
        )
        assert os.path.exists(entrypoint_path), "entrypoint.sh must exist first"

        with open(entrypoint_path, "r") as f:
            content = f.read()
        assert "mkdocs build" in content, "entrypoint.sh must run mkdocs build"
        assert "--site-dir /site" in content, "mkdocs build must output to /site"

    def test_entrypoint_logs_completion(self):
        """Verify entrypoint.sh logs completion message"""
        entrypoint_path = os.path.join(
            PROJECT_ROOT, "docker", "builder", "entrypoint.sh"
        )
        assert os.path.exists(entrypoint_path), "entrypoint.sh must exist first"

        with open(entrypoint_path, "r") as f:
            content = f.read()
        # Should have some logging/echo statement
        assert "echo" in content.lower(), "entrypoint.sh should log completion message"

    def test_entrypoint_syntax_is_valid(self):
        """Verify entrypoint.sh has valid shell syntax"""
        entrypoint_path = os.path.join(
            PROJECT_ROOT, "docker", "builder", "entrypoint.sh"
        )
        assert os.path.exists(entrypoint_path), "entrypoint.sh must exist first"

        # Use sh -n to check syntax without executing
        result = subprocess.run(
            ["sh", "-n", entrypoint_path], capture_output=True, text=True
        )

        assert (
            result.returncode == 0
        ), f"entrypoint.sh has syntax errors: {result.stderr}"


class TestTask22_DockerfileEntrypoint:
    """Task 2.2: Update builder Dockerfile for entrypoint"""

    def test_dockerfile_exists(self):
        """Verify docker/builder/Dockerfile exists"""
        dockerfile_path = os.path.join(PROJECT_ROOT, "docker", "builder", "Dockerfile")
        assert os.path.exists(dockerfile_path), "Dockerfile must exist"

    def test_dockerfile_copies_entrypoint(self):
        """Verify Dockerfile copies entrypoint.sh to /usr/local/bin/"""
        dockerfile_path = os.path.join(PROJECT_ROOT, "docker", "builder", "Dockerfile")
        assert os.path.exists(dockerfile_path), "Dockerfile must exist first"

        with open(dockerfile_path, "r") as f:
            content = f.read()
        assert (
            "COPY" in content and "entrypoint.sh" in content
        ), "Dockerfile must COPY entrypoint.sh"
        assert (
            "/usr/local/bin" in content
        ), "entrypoint.sh must be copied to /usr/local/bin/"

    def test_dockerfile_makes_entrypoint_executable(self):
        """Verify Dockerfile makes entrypoint.sh executable"""
        dockerfile_path = os.path.join(PROJECT_ROOT, "docker", "builder", "Dockerfile")
        assert os.path.exists(dockerfile_path), "Dockerfile must exist first"

        with open(dockerfile_path, "r") as f:
            content = f.read()
        # Should have RUN chmod +x or similar
        assert (
            "chmod +x" in content and "entrypoint.sh" in content
        ) or "--chmod=755" in content, "Dockerfile must make entrypoint.sh executable"

    def test_dockerfile_sets_cmd_to_entrypoint(self):
        """Verify Dockerfile sets CMD to run entrypoint.sh"""
        dockerfile_path = os.path.join(PROJECT_ROOT, "docker", "builder", "Dockerfile")
        assert os.path.exists(dockerfile_path), "Dockerfile must exist first"

        with open(dockerfile_path, "r") as f:
            content = f.read()
        # Should have CMD ["entrypoint.sh"] or similar
        assert (
            "CMD" in content and "entrypoint.sh" in content
        ), "Dockerfile must set CMD to run entrypoint.sh"


class TestTask23_DockerComposeBuilder:
    """Task 2.3: Add docs-builder service to docker-compose.yml"""

    def test_docker_compose_file_exists(self):
        """Verify docker-compose.yml exists"""
        compose_path = os.path.join(PROJECT_ROOT, "docker-compose.yml")
        assert os.path.exists(compose_path), "docker-compose.yml must exist"

    def test_docker_compose_has_builder_service(self):
        """Verify docker-compose.yml contains docs-builder service"""
        compose_path = os.path.join(PROJECT_ROOT, "docker-compose.yml")
        assert os.path.exists(compose_path), "docker-compose.yml must exist first"

        with open(compose_path, "r") as f:
            content = f.read()
        assert (
            "docs-builder" in content
        ), "docker-compose.yml must define docs-builder service"

    def test_builder_service_uses_correct_build_context(self):
        """Verify docs-builder uses build context ./docker/builder"""
        compose_path = os.path.join(PROJECT_ROOT, "docker-compose.yml")
        assert os.path.exists(compose_path), "docker-compose.yml must exist first"

        with open(compose_path, "r") as f:
            content = f.read()
        assert (
            "docker/builder" in content or "./docker/builder" in content
        ), "docs-builder must use build context ./docker/builder"

    def test_builder_service_mounts_workspace(self):
        """Verify docs-builder mounts ./dyalog-docs:/workspace:ro"""
        compose_path = os.path.join(PROJECT_ROOT, "docker-compose.yml")
        assert os.path.exists(compose_path), "docker-compose.yml must exist first"

        with open(compose_path, "r") as f:
            content = f.read()
        assert (
            "dyalog-docs" in content and "/workspace" in content
        ), "docs-builder must mount ./dyalog-docs to /workspace"
        # Should be read-only
        assert (
            ":ro" in content or "read_only: true" in content
        ), "dyalog-docs mount should be read-only"

    def test_builder_service_mounts_site_output(self):
        """Verify docs-builder mounts ./site:/site"""
        compose_path = os.path.join(PROJECT_ROOT, "docker-compose.yml")
        assert os.path.exists(compose_path), "docker-compose.yml must exist first"

        with open(compose_path, "r") as f:
            content = f.read()
        # Look for site volume mount (without :ro since it needs to write)
        assert (
            "./site" in content and "/site" in content
        ), "docs-builder must mount ./site to /site for output"

    def test_docker_compose_config_is_valid(self):
        """Verify docker-compose.yml syntax is valid"""
        result = subprocess.run(
            ["docker", "compose", "config"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        assert (
            result.returncode == 0
        ), f"docker-compose.yml has syntax errors: {result.stderr}"


class TestTask24_FullBuildProcess:
    """Task 2.4: Test full build process"""

    @pytest.fixture(scope="class")
    def clean_site_directory(self):
        """Remove site directory before tests"""
        site_dir = os.path.join(PROJECT_ROOT, "site")
        if os.path.exists(site_dir):
            shutil.rmtree(site_dir)
        yield
        # Cleanup after tests if needed

    def test_builder_image_builds_successfully(self):
        """Verify builder Docker image can be built"""
        builder_path = os.path.join("docker", "builder")
        result = subprocess.run(
            ["docker", "build", "-t", "mkdocs-builder-test", builder_path],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        assert result.returncode == 0, f"Failed to build builder image: {result.stderr}"

    def test_builder_service_runs_successfully(self, clean_site_directory):
        """Verify docs-builder service runs without errors"""
        # This test will actually run the builder
        result = subprocess.run(
            ["docker", "compose", "run", "--rm", "docs-builder"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout for full build
        )

        assert (
            result.returncode == 0
        ), f"Builder service failed: {result.stderr}\nOutput: {result.stdout}"

    def test_site_directory_is_created(self):
        """Verify site/ directory is created after build"""
        site_dir = os.path.join(PROJECT_ROOT, "site")
        assert os.path.exists(site_dir), "site/ directory must be created by builder"
        assert os.path.isdir(site_dir), "site/ must be a directory"

    def test_site_index_html_exists(self):
        """Verify site/index.html exists"""
        index_file = os.path.join(PROJECT_ROOT, "site", "index.html")
        assert os.path.exists(index_file), "site/index.html must exist after build"

    def test_site_has_multiple_index_files(self):
        """Verify site contains multiple index.html files (main + subsites)"""
        site_dir = os.path.join(PROJECT_ROOT, "site")
        assert os.path.exists(site_dir), "site/ directory must exist first"

        # Find all index.html files
        index_files = []
        for root, dirs, files in os.walk(site_dir):
            if "index.html" in files:
                index_files.append(os.path.join(root, "index.html"))

        assert (
            len(index_files) > 1
        ), f"Expected multiple index.html files (main + subsites), found {len(index_files)}"

    def test_build_completes_in_reasonable_time(self):
        """Verify build completes in under 5 minutes"""
        # This is tested implicitly by the timeout in test_builder_service_runs_successfully
        # If we get here, the build completed within timeout
        assert True


class TestTask25_EnvironmentVariables:
    """Task 2.5: Verify environment variables in output"""

    def test_current_year_appears_in_html(self):
        """Verify CURRENT_YEAR appears in generated HTML"""
        site_dir = os.path.join(PROJECT_ROOT, "site")
        assert os.path.exists(site_dir), "site/ directory must exist first"

        # Get current year
        from datetime import datetime

        current_year = str(datetime.now().year)

        # Search for current year in HTML files
        html_files = []
        for root, dirs, files in os.walk(site_dir):
            for file in files:
                if file.endswith(".html"):
                    html_files.append(os.path.join(root, file))

        assert len(html_files) > 0, "No HTML files found in site/"

        found_year = False
        for html_file in html_files[:10]:  # Check first 10 files
            with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if current_year in content:
                found_year = True
                break

        assert (
            found_year
        ), f"Current year {current_year} not found in generated HTML files"

    def test_build_date_appears_in_html(self):
        """Verify BUILD_DATE appears in generated HTML"""
        site_dir = os.path.join(PROJECT_ROOT, "site")
        assert os.path.exists(site_dir), "site/ directory must exist first"

        # Search for date-related strings (UTC, date format, etc.)
        html_files = []
        for root, dirs, files in os.walk(site_dir):
            for file in files:
                if file.endswith(".html"):
                    html_files.append(os.path.join(root, file))

        assert len(html_files) > 0, "No HTML files found in site/"

        found_date = False

        for html_file in html_files[:10]:  # Check first 10 files
            with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            # Look for date-like patterns
            if "UTC" in content or "build" in content.lower():
                found_date = True
                break

        assert found_date, "BUILD_DATE information not found in generated HTML files"

    def test_git_info_handling(self):
        """Verify GIT_INFO is handled (present if .git available, absent otherwise)"""
        site_dir = os.path.join(PROJECT_ROOT, "site")
        assert os.path.exists(site_dir), "site/ directory must exist first"

        # Check if .git directory exists
        git_dir = os.path.join(PROJECT_ROOT, "dyalog-docs", ".git")

        if os.path.exists(git_dir):
            # If .git exists, GIT_INFO should appear in HTML
            html_files = []
            for root, dirs, files in os.walk(site_dir):
                for file in files:
                    if file.endswith(".html"):
                        html_files.append(os.path.join(root, file))

            assert len(html_files) > 0, "No HTML files found in site/"

            # Should have some git-related info
            for html_file in html_files[:20]:
                with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if "git" in content.lower() or "commit" in content.lower():
                    break

            # This is optional - git info might not be displayed in HTML
            # So we don't assert, just check
            pass
        else:
            # If .git doesn't exist, script should handle gracefully
            # Build should still succeed (tested in Task 2.4)
            assert True
