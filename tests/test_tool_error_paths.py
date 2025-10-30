import pytest

from tools.table import table_preview, optimize_delta
from tools.pipeline import pipeline_run
from tools.powerbi import semantic_model_refresh
from tools.graph import graph_user


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



