from unittest.mock import MagicMock

import pytest
from nodestream.project import (
    PipelineConfiguration,
    PipelineDefinition,
    PipelineScope,
    Project,
)

from nodestream_plugin_k8s.commands import ListCommand


@pytest.fixture
def project():
    return Project(
        scopes_by_name={
            "crons": PipelineScope(
                name="crons",
                pipelines_by_name={
                    "test_cron_pipeline_a": PipelineDefinition(
                        name="test_cron_pipeline_a",
                        file_path="crons/test_cron_pipeline_a",
                        configuration=PipelineConfiguration(
                            annotations={
                                "nodestream_plugin_k8s_schedule": "*/5 * * * *",
                                "nodestream_plugin_k8s_debug": True,
                            },
                        ),
                    ),
                    "test_cron_pipeline_b": PipelineDefinition(
                        name="test_cron_pipeline_b",
                        file_path="crons/test_cron_pipeline_b",
                        configuration=PipelineConfiguration(
                            annotations={
                                "nodestream_plugin_k8s_schedule": "*/5 * * * *",
                            }
                        ),
                    ),
                },
            ),
            "perpetual": PipelineScope(
                name="perpetual",
                pipelines_by_name={
                    "test_perpetual_pipeline_a": PipelineDefinition(
                        name="test_perpetual_pipeline_a",
                        file_path="perpetual/test_perpetual_pipeline_a",
                        configuration=PipelineConfiguration(
                            annotations={
                                "nodestream_plugin_k8s_conccurency": 4,
                                "nodestream_plugin_k8s_debug": True,
                            },
                        ),
                    ),
                    "test_perpetual_pipeline_b": PipelineDefinition(
                        name="test_perpetual_pipeline_b",
                        file_path="perpetual/test_perpetual_pipeline_b",
                        configuration=PipelineConfiguration(
                            annotations={
                                "nodestream_plugin_k8s_conccurency": 4,
                            }
                        ),
                    ),
                },
            ),
        }
    )


@pytest.fixture
def subject():
    return ListCommand()


TEST_JSON_NO_DEBUG = [
    {
        "pipeline_name": "test_cron_pipeline_a",
        "cron_schedule": "*/5 * * * *",
        "perpetual_concurrency": None,
        "suspend": False,
        "debug_enabled": True,
    },
    {
        "pipeline_name": "test_cron_pipeline_b",
        "cron_schedule": "*/5 * * * *",
        "perpetual_concurrency": None,
        "suspend": False,
        "debug_enabled": False,
    },
]


TEST_JSON_DEBUG = [
    {
        "pipeline_name": "test_perpetual_pipeline_a",
        "cron_schedule": None,
        "perpetual_concurrency": 4,
        "suspend": False,
        "debug_enabled": True,
    },
    {
        "pipeline_name": "test_perpetual_pipeline_b",
        "cron_schedule": None,
        "perpetual_concurrency": 0,
        "suspend": True,
        "debug_enabled": False,
    },
]


"""
nodestream k8s list --scope crons --json
"""


@pytest.mark.asyncio
async def test_no_debug(project: Project, subject: ListCommand):
    def options_mock(option):
        options = {"scope": "crons", "json": True, "development": False}
        return options[option]

    subject.get_project = MagicMock(return_value=project)
    subject.display_as_json = MagicMock()
    subject.option = MagicMock(side_effect=options_mock)
    await subject.handle_async()
    results = subject.display_as_json.call_args[0][0]
    results = [result.as_dict() for result in results]
    assert results == TEST_JSON_NO_DEBUG


"""
nodestream k8s list --scope perpetual --json --development
"""


@pytest.mark.asyncio
async def test_debug(project: Project, subject: ListCommand):
    def options_mock(option):
        options = {"scope": "perpetual", "json": True, "development": True}
        return options[option]

    subject.get_project = MagicMock(return_value=project)
    subject.display_as_json = MagicMock()
    subject.option = MagicMock(side_effect=options_mock)
    await subject.handle_async()
    results = subject.display_as_json.call_args[0][0]
    results = [result.as_dict() for result in results]
    assert results == TEST_JSON_DEBUG
