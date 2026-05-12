from pathlib import Path
import py_compile


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_expected_paths_exist():
    expected_paths = [
        PROJECT_ROOT / "frosty" / "__init__.py",
        PROJECT_ROOT / "frosty" / "agent.py",
        PROJECT_ROOT / "src" / "__init__.py",
        PROJECT_ROOT / "src" / "session.py",
        PROJECT_ROOT / "src" / "frosty_ai" / "objagents" / "agent.py",
        PROJECT_ROOT / "skills",
    ]

    for path in expected_paths:
        assert path.exists(), f"Missing expected Frosty sample path: {path}"


def test_key_python_files_compile():
    files_to_compile = [
        PROJECT_ROOT / "frosty" / "agent.py",
        PROJECT_ROOT / "src" / "session.py",
        PROJECT_ROOT / "src" / "frosty_ai" / "objagents" / "agent.py",
        PROJECT_ROOT / "src" / "frosty_ai" / "objagents" / "tools.py",
        PROJECT_ROOT / "src" / "frosty_ai" / "objagents" / "main.py",
    ]

    for file_path in files_to_compile:
        py_compile.compile(str(file_path), doraise=True)
