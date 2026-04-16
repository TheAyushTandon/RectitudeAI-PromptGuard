"""Quick verification test for the HR Database Agent."""
import asyncio
from backend.agents.hr_database_agent import HRDatabaseAgent
from backend.agents.tools.database_tool import DatabaseTool
from backend.agents.registry import agent_registry


def test_agent_basics():
    agent = HRDatabaseAgent()
    assert agent.name == "hr_database"
    assert "query_database" in agent.allowed_tools
    print(f"[OK] Agent: {agent.name}, tools: {agent.allowed_tools}")

    agent_registry.register(agent)
    assert "hr_database" in agent_registry
    print(f"[OK] Registry has {len(agent_registry)} agents: {agent_registry.agent_names}")


def test_database_tool_validation():
    tool = DatabaseTool()
    assert tool.is_available(), "Database not found. Run: python scripts/seed_demo_db.py"
    print("[OK] Database available")

    ok, _ = tool.validate_query("SELECT name FROM employees")
    assert ok, "Valid SELECT rejected"

    ok, reason = tool.validate_query("DROP TABLE employees")
    assert not ok, "DROP should be blocked"
    print(f"[OK] DROP blocked: {reason}")

    ok, reason = tool.validate_query("SELECT 1; DELETE FROM employees")
    assert not ok, "Multi-statement should be blocked"
    print(f"[OK] Multi-statement blocked: {reason}")

    ok, reason = tool.validate_query("INSERT INTO employees VALUES (1)")
    assert not ok, "INSERT should be blocked"
    print(f"[OK] INSERT blocked: {reason}")


async def test_database_queries():
    tool = DatabaseTool()

    # Basic query
    result = await tool.execute("SELECT name, department, role FROM employees LIMIT 3")
    assert result["row_count"] == 3
    print(f"[OK] Basic query returned {result['row_count']} rows")
    for row in result["rows"]:
        print(f"     {row}")

    # Sensitive column masking
    result2 = await tool.execute("SELECT name, email, ssn FROM employees LIMIT 2")
    for row in result2["rows"]:
        assert "***" in str(row.get("ssn", "")), "SSN should be masked"
        assert "***" in str(row.get("email", "")), "Email should be masked"
    print("[OK] Sensitive columns masked correctly")

    # Full table cap
    result3 = await tool.execute("SELECT * FROM employees")
    assert len(result3["rows"]) <= 10, "Results should be capped at 10"
    assert result3["truncated"] == True
    print(f"[OK] Results capped: showing {len(result3['rows'])} of {result3['row_count']}")


if __name__ == "__main__":
    test_agent_basics()
    test_database_tool_validation()
    asyncio.run(test_database_queries())
    print("\n=== All HR Agent tests PASSED ===")
