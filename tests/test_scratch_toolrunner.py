"""Throwaway scratch file for exploring ToolRunner output shape. Delete when done."""
from hialt.tools.runner import ToolRunner


def test_scratch_pytest_on_self():
    result = ToolRunner().run_pytest("tests/test_tool_runner.py")
    assert result.success


def test_scratch_ruff_on_self():
    result = ToolRunner().run_ruff("src/")
    print("\n--- ruff ToolResult ---")
    print(f"success={result.success} exit_code={result.exit_code}")
    print("stdout:", result.stdout[:500])


def test_scratch_mypy_on_self():
    result = ToolRunner().run_mypy("src/")
    print("\n--- mypy ToolResult ---")
    print(f"success={result.success} exit_code={result.exit_code}")
    print("stdout:", result.stdout[:500])


def test_scratch_pytest_bad_path():
    result = ToolRunner().run_pytest("tests/this_does_not_exist.py")
    print("\n--- pytest bad path ToolResult ---")
    print(f"success={result.success} exit_code={result.exit_code}")
    print("stderr:", result.stderr[:500])
    assert not result.success  # confirms it fails gracefully, doesn't raise