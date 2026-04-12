import pytest
from unittest.mock import MagicMock, patch

# Import your agents
from agent.base_agent import BaseAgent
from agent.planner_agent import PlannerAgent
from agent.coding_agent import CodingAgent
from agent.automation_agent import AutomationAgent
from core.orchestrator import Orchestrator


# -----------------------------
# Fixtures
# -----------------------------

@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm.generate.return_value = "Mocked response"
    return llm


@pytest.fixture
def mock_memory():
    memory = MagicMock()
    memory.store = MagicMock()
    memory.retrieve = MagicMock(return_value="Previous context")
    return memory


@pytest.fixture
def base_agent(mock_llm, mock_memory):
    return BaseAgent(llm=mock_llm, memory=mock_memory)


@pytest.fixture
def planner_agent(mock_llm, mock_memory):
    return PlannerAgent(llm=mock_llm, memory=mock_memory)


@pytest.fixture
def coding_agent(mock_llm, mock_memory):
    return CodingAgent(llm=mock_llm, memory=mock_memory)


@pytest.fixture
def automation_agent(mock_llm, mock_memory):
    return AutomationAgent(llm=mock_llm, memory=mock_memory)


# -----------------------------
# BaseAgent Tests
# -----------------------------

def test_base_agent_run(base_agent, mock_llm):
    result = base_agent.run("Hello")

    mock_llm.generate.assert_called_once()
    assert isinstance(result, str)
    assert result == "Mocked response"


def test_base_agent_memory_interaction(base_agent, mock_memory):
    base_agent.run("Test input")

    mock_memory.store.assert_called()


# -----------------------------
# PlannerAgent Tests
# -----------------------------

def test_planner_generates_plan(planner_agent, mock_llm):
    plan = planner_agent.plan("Build JARVIS")

    mock_llm.generate.assert_called()
    assert isinstance(plan, str)


def test_planner_handles_empty_input(planner_agent):
    with pytest.raises(ValueError):
        planner_agent.plan("")


# -----------------------------
# CodingAgent Tests
# -----------------------------

def test_coding_agent_generates_code(coding_agent, mock_llm):
    code = coding_agent.generate_code("Create API")

    mock_llm.generate.assert_called()
    assert "Mocked response" in code


def test_coding_agent_handles_errors(coding_agent):
    with patch.object(coding_agent.llm, "generate", side_effect=Exception("LLM error")):
        result = coding_agent.generate_code("Fail case")

        assert "error" in result.lower()


# -----------------------------
# AutomationAgent Tests
# -----------------------------

def test_automation_executes_task(automation_agent, mock_llm):
    result = automation_agent.execute("Open browser")

    mock_llm.generate.assert_called()
    assert isinstance(result, str)


def test_automation_invalid_task(automation_agent):
    with pytest.raises(ValueError):
        automation_agent.execute(None)


# -----------------------------
# Orchestrator Tests
# -----------------------------

@pytest.fixture
def orchestrator(mock_llm, mock_memory):
    return Orchestrator(llm=mock_llm, memory=mock_memory)


def test_orchestrator_routes_to_planner(orchestrator):
    with patch.object(orchestrator, "planner") as mock_planner:
        mock_planner.plan.return_value = "Plan created"

        result = orchestrator.handle("Plan something")

        assert result == "Plan created"


def test_orchestrator_routes_to_coding(orchestrator):
    with patch.object(orchestrator, "coding") as mock_coding:
        mock_coding.generate_code.return_value = "Code generated"

        result = orchestrator.handle("Write code")

        assert result == "Code generated"


def test_orchestrator_routes_to_automation(orchestrator):
    with patch.object(orchestrator, "automation") as mock_auto:
        mock_auto.execute.return_value = "Executed"

        result = orchestrator.handle("Open app")

        assert result == "Executed"


def test_orchestrator_fallback(orchestrator, mock_llm):
    result = orchestrator.handle("Random input")

    mock_llm.generate.assert_called()
    assert isinstance(result, str)