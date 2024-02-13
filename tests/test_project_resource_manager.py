import pytest
from nodestream.project import (
    PipelineConfiguration,
    PipelineDefinition,
    PipelineScope,
    Project,
)

from nodestream_plugin_k8s.project_resource_manager import (
    PipelineDesiredState,
    PipelineResourceManager,
    ProjectResourceManager,
)


@pytest.fixture
def project():
    return Project(
        scopes_by_name={
            "crons": PipelineScope(
                name="crons",
                pipelines_by_name={
                    "test_pipeline_1": PipelineDefinition(
                        name="test_pipeline_1",
                        file_path="crons/test_pipeline_1",
                        configuration=PipelineConfiguration(
                            annotations={
                                "nodestream_plugin_k8s_schedule": "*/5 * * * *",
                            },
                        ),
                    ),
                    "test_pipeline_2": PipelineDefinition(
                        name="test_pipeline_2",
                        file_path="crons/test_pipeline_2",
                        configuration=PipelineConfiguration(
                            annotations={
                                "nodestream_plugin_k8s_schedule": "*/5 * * * *",
                            }
                        ),
                    ),
                },
            ),
            "deployments": PipelineScope(
                name="deployments",
                pipelines_by_name={
                    "test_pipeline_3": PipelineDefinition(
                        name="test_pipeline_3",
                        file_path="deployments/test_pipeline_3",
                        configuration=PipelineConfiguration(
                            annotations={
                                "nodestream_plugin_k8s_conccurency": 4,
                            }
                        ),
                    ),
                },
            ),
            "development": PipelineScope(
                name="development",
                pipelines_by_name={
                    "development_pipeline_3": PipelineDefinition(
                        name="development_pipeline_3",
                        file_path="deployments/development_pipeline_3",
                        configuration=PipelineConfiguration(
                            annotations={
                                "nodestream_plugin_k8s_schedule": "*/5 * * * *",
                                "nodestream_plugin_k8s_debug": True,
                            }
                        ),
                    ),
                    "development_pipeline_4": PipelineDefinition(
                        name="development_pipeline_4",
                        file_path="deployments/development_pipeline_4",
                        configuration=PipelineConfiguration(
                            annotations={
                                "nodestream_plugin_k8s_conccurency": 4,
                                "nodestream_plugin_k8s_debug": True,
                            }
                        ),
                    ),
                },
            ),
            "other": PipelineScope(
                name="other",
                pipelines_by_name={
                    "test_pipeline_4": PipelineDefinition(
                        name="test_pipeline_4",
                        file_path="other/test_pipeline_4",
                    ),
                },
            ),
        },
    )


@pytest.fixture
def project_resource_manager(project):
    return ProjectResourceManager(project)


@pytest.fixture
def perpetual_resource_manager(project):
    return PipelineResourceManager(
        project.scopes_by_name["deployments"].pipelines_by_name["test_pipeline_3"]
    )


@pytest.fixture
def cron_resource_manager(project):
    return PipelineResourceManager(
        project.scopes_by_name["crons"].pipelines_by_name["test_pipeline_1"]
    )


@pytest.fixture
def development_cron_resource_manager(project):
    return PipelineResourceManager(
        project.scopes_by_name["development"].pipelines_by_name[
            "development_pipeline_3"
        ]
    )


@pytest.fixture
def development_perpetual_resource_manager(project):
    return PipelineResourceManager(
        project.scopes_by_name["development"].pipelines_by_name[
            "development_pipeline_4"
        ]
    )


def test_get_managed_pipelines(project_resource_manager):
    managed_pipelines = list(project_resource_manager.get_managed_pipelines())
    assert len(managed_pipelines) == 5


def test_pipeline_resource_manager_cron_desired_state(cron_resource_manager):
    assert cron_resource_manager.desired_state == PipelineDesiredState(
        pipeline_name="test_pipeline_1",
        cron_schedule="*/5 * * * *",
        perpetual_concurrency=None,
    )


def test_pipeline_resource_manager_perpetual_desired_state(perpetual_resource_manager):
    assert perpetual_resource_manager.desired_state == PipelineDesiredState(
        pipeline_name="test_pipeline_3",
        cron_schedule=None,
        perpetual_concurrency=4,
        debug_enabled=False,
    )


def test_developement_desired_state(
    development_cron_resource_manager, development_perpetual_resource_manager
):
    assert development_cron_resource_manager.desired_state == PipelineDesiredState(
        pipeline_name="development_pipeline_3",
        cron_schedule="*/5 * * * *",
        perpetual_concurrency=None,
        debug_enabled=True,
    )
    assert development_perpetual_resource_manager.desired_state == PipelineDesiredState(
        pipeline_name="development_pipeline_4",
        cron_schedule=None,
        perpetual_concurrency=4,
        debug_enabled=True,
    )
