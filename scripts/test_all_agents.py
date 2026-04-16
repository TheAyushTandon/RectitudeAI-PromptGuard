"""All-agents import and registration test."""
import asyncio
from backend.agents.registry import agent_registry
from backend.agents.hr_database_agent import HRDatabaseAgent
from backend.agents.email_agent import EmailAgent
from backend.agents.code_exec_agent import CodeExecAgent
from backend.agents.financial_advisor_agent import FinancialAdvisorAgent
from backend.agents.tools.calculator_tool import CalculatorTool
from backend.agents.tools.stock_tool import StockTool
from backend.agents.tools.code_executor import CodeExecutor
from backend.agents.tools.email_tool import EmailTool
from backend.agents.tools.database_tool import DatabaseTool
from backend.agents.router import AgentRouter


def test_all_agents():
    # Register all agents
    agents = [HRDatabaseAgent(), EmailAgent(), CodeExecAgent(), FinancialAdvisorAgent()]
    for a in agents:
        agent_registry.register(a)

    print(f"[OK] {len(agent_registry)} agents registered: {agent_registry.agent_names}")
    assert len(agent_registry) == 4

    # Verify each agent
    for a in agents:
        assert a.name in agent_registry
        assert len(a.allowed_tools) > 0
        print(f"  {a.name}: {a.description[:60]}... tools={a.allowed_tools}")

    # Test agent listing
    listing = agent_registry.list_agents()
    assert len(listing) == 4
    print("[OK] Agent listing works")


def test_calculator():
    calc = CalculatorTool()
    r = calc.evaluate("2 + 3 * 4")
    assert r["result"] == 14
    print(f"[OK] Calculator: 2 + 3 * 4 = {r['result']}")

    r = calc.evaluate("sqrt(144)")
    assert r["result"] == 12.0
    print(f"[OK] Calculator: sqrt(144) = {r['result']}")


def test_stock_tool():
    tool = StockTool()
    q = tool.get_quote("AAPL")
    assert "error" not in q
    assert q["symbol"] == "AAPL"
    print(f"[OK] Stock: AAPL = ${q['price']}")

    q2 = tool.get_quote("INVALID")
    assert "error" in q2
    print("[OK] Stock: invalid ticker handled")


def test_code_executor():
    executor = CodeExecutor()

    # Safe code
    ok, _ = executor.validate_code("print(2 + 3)")
    assert ok
    print("[OK] CodeExecutor: safe code accepted")

    # Dangerous code
    ok, reason = executor.validate_code("import os; os.system('rm -rf /')")
    assert not ok
    print(f"[OK] CodeExecutor blocked: {reason}")

    ok, reason = executor.validate_code("eval('__import__(\"os\")')")
    assert not ok
    print(f"[OK] CodeExecutor blocked: {reason}")

    ok, reason = executor.validate_code("open('/etc/passwd').read()")
    assert not ok
    print(f"[OK] CodeExecutor blocked: {reason}")


async def test_code_execution():
    executor = CodeExecutor()

    # Run safe code
    result = await executor.execute("print(sum(range(10)))")
    assert result.success
    assert "45" in result.stdout
    print(f"[OK] Code execution: sum(range(10)) = 45 ({result.execution_time_ms:.1f}ms)")

    # Block dangerous code
    result2 = await executor.execute("import subprocess")
    assert not result2.success
    assert result2.blocked
    print(f"[OK] Execution blocked: {result2.block_reason}")


def test_email_tool():
    tool = EmailTool()

    # Valid domain
    ok, _ = tool.validate_recipient("test@acmecorp.com")
    assert ok
    print("[OK] Email: acmecorp.com domain accepted")

    # Invalid domain
    ok, reason = tool.validate_recipient("attacker@evil.com")
    assert not ok
    print(f"[OK] Email blocked: {reason[:60]}")


def test_keyword_router():
    router = AgentRouter()

    # HR keywords
    result = router._classify_with_keywords("Who works in the engineering department?")
    assert result == "hr_database"
    print(f"[OK] Router (keyword): HR query -> {result}")

    # Email keywords
    result = router._classify_with_keywords("Send an email to the customer about their order")
    assert result == "email_agent"
    print(f"[OK] Router (keyword): Email query -> {result}")

    # Code keywords
    result = router._classify_with_keywords("Run this python script to analyze the logs")
    assert result == "code_exec"
    print(f"[OK] Router (keyword): Code query -> {result}")

    # Finance keywords
    result = router._classify_with_keywords("What should I invest in for my retirement portfolio?")
    assert result == "financial_advisor"
    print(f"[OK] Router (keyword): Finance query -> {result}")


if __name__ == "__main__":
    test_all_agents()
    test_calculator()
    test_stock_tool()
    test_code_executor()
    asyncio.run(test_code_execution())
    test_email_tool()
    test_keyword_router()
    print("\n=== ALL AGENT SYSTEM TESTS PASSED ===")
