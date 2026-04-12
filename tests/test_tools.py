import pytest
from unittest.mock import MagicMock, patch

# Import your tools
from tools.base_tool import BaseTool
from tools.web_search import WebSearchTool
from tools.file_tool import FileTool
from tools.system_tool import SystemTool
from tools.code_executor import CodeExecutor


# -----------------------------------
# Fixtures
# -----------------------------------

@pytest.fixture
def base_tool():
    return BaseTool(name="test_tool")


@pytest.fixture
def web_tool():
    tool = WebSearchTool(api_key="fake_key")
    tool.client = MagicMock()
    return tool


@pytest.fixture
def file_tool(tmp_path):
    return FileTool(base_path=tmp_path)


@pytest.fixture
def system_tool():
    return SystemTool()


@pytest.fixture
def code_executor():
    return CodeExecutor()


# -----------------------------------
# BaseTool Tests
# -----------------------------------

def test_base_tool_execute_not_implemented(base_tool):
    with pytest.raises(NotImplementedError):
        base_tool.execute("input")


def test_base_tool_name(base_tool):
    assert base_tool.name == "test_tool"


# -----------------------------------
# WebSearchTool Tests
# -----------------------------------

def test_web_search_success(web_tool):
    web_tool.client.search.return_value = {"results": ["data"]}

    result = web_tool.execute("AI news")

    web_tool.client.search.assert_called_once()
    assert "results" in result


def test_web_search_empty_query(web_tool):
    with pytest.raises(ValueError):
        web_tool.execute("")


def test_web_search_api_failure(web_tool):
    web_tool.client.search.side_effect = Exception("API down")

    result = web_tool.execute("test")

    assert "error" in str(result).lower()


# -----------------------------------
# FileTool Tests
# -----------------------------------

def test_file_write_and_read(file_tool):
    file_tool.write("test.txt", "hello")

    content = file_tool.read("test.txt")

    assert content == "hello"


def test_file_delete(file_tool):
    file_tool.write("temp.txt", "data")

    file_tool.delete("temp.txt")

    assert not file_tool.exists("temp.txt")


def test_file_not_found(file_tool):
    with pytest.raises(FileNotFoundError):
        file_tool.read("missing.txt")


def test_file_security_path_traversal(file_tool):
    with pytest.raises(Exception):
        file_tool.read("../hack.txt")


# -----------------------------------
# SystemTool Tests
# -----------------------------------

def test_system_command_execution(system_tool):
    with patch("os.system") as mock_system:
        mock_system.return_value = 0

        result = system_tool.execute("echo hello")

        mock_system.assert_called_once()
        assert result == 0


def test_system_invalid_command(system_tool):
    with patch("os.system", side_effect=Exception("fail")):
        result = system_tool.execute("bad_command")

        assert "error" in str(result).lower()


# -----------------------------------
# CodeExecutor Tests
# -----------------------------------

def test_code_executor_python(code_executor):
    code = "print('Hello')"

    result = code_executor.execute(code)

    assert "Hello" in result


def test_code_executor_error(code_executor):
    code = "raise Exception('fail')"

    result = code_executor.execute(code)

    assert "fail" in result.lower()


def test_code_executor_security(code_executor):
    """
    Ensure dangerous operations are blocked
    """
    dangerous_code = "import os; os.remove('file.txt')"

    result = code_executor.execute(dangerous_code)

    assert "not allowed" in result.lower() or "error" in result.lower()


# -----------------------------------
# Integration Tests (IMPORTANT)
# -----------------------------------

def test_tool_chain_execution(web_tool, file_tool):
    """
    Simulate chaining: search -> save result
    """
    web_tool.client.search.return_value = {"results": ["AI data"]}

    result = web_tool.execute("AI")
    file_tool.write("output.txt", str(result))

    saved = file_tool.read("output.txt")

    assert "AI data" in saved


def test_tool_resilience(system_tool, web_tool):
    """
    System should not crash if one tool fails
    """
    web_tool.client.search.side_effect = Exception("fail")

    result1 = web_tool.execute("test")
    result2 = system_tool.execute("echo ok")

    assert result2 == 0
    assert result1 is not None


# -----------------------------------
# Stress / Edge Cases
# -----------------------------------

def test_large_file_handling(file_tool):
    large_content = "A" * 100000

    file_tool.write("big.txt", large_content)
    content = file_tool.read("big.txt")

    assert len(content) == 100000


def test_multiple_tool_calls(web_tool):
    web_tool.client.search.return_value = {"results": ["data"]}

    for _ in range(10):
        result = web_tool.execute("loop")

        assert "results" in result