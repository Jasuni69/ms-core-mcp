import pytest

from tools.table import table_preview, optimize_delta
from tools.pipeline import pipeline_run
from tools.powerbi import semantic_model_refresh
from tools.graph import graph_user, graph_teams_message, _normalise_channel_message_content


@pytest.mark.asyncio
async def test_table_preview_requires_context():
    result = await table_preview(ctx=None)
    assert isinstance(result, dict)
    assert "error" in result


@pytest.mark.asyncio
async def test_optimize_delta_requires_context():
    result = await optimize_delta(ctx=None)
    assert isinstance(result, dict)
    assert "error" in result


@pytest.mark.asyncio
async def test_pipeline_run_requires_context():
    result = await pipeline_run(ctx=None)
    assert isinstance(result, dict)
    assert "error" in result


@pytest.mark.asyncio
async def test_semantic_model_refresh_requires_context():
    result = await semantic_model_refresh(ctx=None)
    assert isinstance(result, dict)
    assert "error" in result


@pytest.mark.asyncio
async def test_graph_user_requires_context():
    result = await graph_user("someone@example.com", ctx=None)  # type: ignore[arg-type]
    assert isinstance(result, dict)
    assert "error" in result


def test_normalise_channel_message_plain_text_to_html():
    content_type, content = _normalise_channel_message_content("Hello & welcome")
    assert content_type == "html"
    assert content == "<div>Hello &amp; welcome</div>"


def test_normalise_channel_message_newlines_replaced():
    _, content = _normalise_channel_message_content("Line1\nLine2")
    assert "<br>" in content


def test_normalise_channel_message_invalid_type():
    with pytest.raises(ValueError):
        _normalise_channel_message_content("hi", content_type="invalid")


@pytest.mark.asyncio
async def test_graph_teams_message_requires_context():
    result = await graph_teams_message("team", "channel", "text", ctx=None)
    assert isinstance(result, dict)
    assert "error" in result



