import json
from src.core.tools import ToolRegistry


def test_register_tool() -> None:
    registry = ToolRegistry()

    registry.register(
        name="echo",
        description="Echo a message",
        parameters={
            "type": "object",
            "properties": {"msg": {"type": "string"}},
            "required": ["msg"],
        },
        handler=lambda msg: msg,
    )

    schemas = registry.get_schemas()
    assert len(schemas) == 1
    assert schemas[0]["function"]["name"] == "echo"


def test_duplicate_registration_raises() -> None:
    registry = ToolRegistry()

    def handler(x: str) -> str:
        return x

    registry.register(
        name="test",
        description="test",
        parameters={"type": "object", "properties": {}, "required": []},
        handler=handler,
    )

    try:
        registry.register(
            name="test",
            description="duplicate",
            parameters={"type": "object", "properties": {}, "required": []},
            handler=handler,
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "already registered" in str(e)


def test_execute_tool() -> None:
    registry = ToolRegistry()

    registry.register(
        name="add",
        description="Add two numbers",
        parameters={
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"},
            },
            "required": ["a", "b"],
        },
        handler=lambda a, b: str(a + b),
    )

    result = registry.execute("add", {"a": 3, "b": 5})
    assert result == "8"


def test_execute_unknown_tool() -> None:
    registry = ToolRegistry()
    result = registry.execute("nonexistent", {})
    data = json.loads(result)
    assert "error" in data
    assert "Unknown tool" in data["error"]


def test_execute_handler_error() -> None:
    registry = ToolRegistry()

    registry.register(
        name="fail",
        description="Always fails",
        parameters={"type": "object", "properties": {}, "required": []},
        handler=lambda: 1 / 0,
    )

    result = registry.execute("fail", {})
    data = json.loads(result)
    assert "error" in data
    assert "tool" in data
