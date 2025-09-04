from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator


# --- Action Models for Steps ---


class RunSqlQueryAction(BaseModel):
    action: Literal["run_sql_query"]
    query: str = Field(
        ..., description="The SQL query string or a 'file:/path/to/query.sql' URI."
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Parameters to pass to the query."
    )


class TestConnectionAction(BaseModel):
    action: Literal["test_connection"]


class BrowsePathAction(BaseModel):
    action: Literal["browse_path"]
    path: str = Field(default="/", description="The virtual path to browse.")


class ReadContentAction(BaseModel):
    action: Literal["read_content"]
    path: str = Field(..., description="The virtual path of the file to read.")


class RunDeclarativeAction(BaseModel):
    """
    A generic action that uses a blueprint from the ApiCatalog to execute
    a pre-defined, templated API call (e.g., Send Email, Create Ticket).
    """

    action: Literal["run_declarative_action"]
    template_key: str = Field(
        ..., description="The key of the action template to use from the ApiCatalog."
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Data to be passed into the action's Jinja2 template.",
    )


class AggregateContentAction(BaseModel):
    """
    Discovers files from sources and aggregates their content into a single output file.
    """

    action: Literal["aggregate_content"]

    source_paths: Optional[List[str]] = Field(
        None, description="A static list of local file or directory paths to aggregate."
    )
    source_results: Optional[List[str]] = Field(
        None,
        description="A list of result objects from previous 'browse' steps, referenced via Jinja.",
    )

    target_path: str = Field(
        ..., description="The VFS path for the aggregated output file."
    )
    header_template: Optional[str] = Field(
        None, description="A Jinja2 template for the file header."
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Metadata for rendering the header."
    )

    # A model validator ensures that at least one of the source fields is provided.
    @model_validator(mode="after")
    def check_at_least_one_source(self) -> "AggregateContentAction":
        if not self.source_paths and not self.source_results:
            raise ValueError(
                "At least one of 'source_paths' or 'source_results' must be provided."
            )
        return self


class RunPythonScriptAction(BaseModel):
    """Executes a Python script in a sandboxed environment."""

    action: Literal["run_python_script"]
    script_path: str = Field(
        ..., description="The path to the Python script to execute."
    )
    input_data_json: str = Field(
        "{}", description="A JSON string to be passed to the script's stdin."
    )


class FileToWrite(BaseModel):
    """Represents a single file to be written to the filesystem."""

    path: str = Field(
        ..., description="The destination path for the file, can be a Jinja template."
    )
    content: str = Field(
        ..., description="The content of the file, can be a Jinja template."
    )


class WriteFilesAction(BaseModel):
    """Writes a collection of in-memory content to the filesystem."""

    action: Literal["write_files"]
    # Change the type from a Dict to a List of our new model.
    files: List[FileToWrite] = Field(
        ..., description="A list of file objects, each with a path and content."
    )


class RunTransformAction(BaseModel):
    """
    Executes a .transformer.yaml script as a native step in a flow.
    """

    action: Literal["run_transform"]
    script_path: str = Field(
        ..., description="The path to the .transformer.yaml script to execute."
    )
    # This input is flexible and will be rendered by Jinja before execution.
    input_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="A dictionary containing data to be passed to the transformer's context.",
    )


# A discriminated union of all possible actions.
# This list MUST be updated whenever a new action is created.
AnyConnectorAction = Union[
    TestConnectionAction,
    BrowsePathAction,
    ReadContentAction,
    RunSqlQueryAction,
    RunDeclarativeAction,
    AggregateContentAction,
    RunPythonScriptAction,
    WriteFilesAction,
    RunTransformAction,
]


class ConnectorStep(BaseModel):
    """
    Defines a single, executable step within a declarative workflow script.
    """

    id: str  # The ID is now REQUIRED for unambiguous dependency resolution.

    # A human-readable name for the step.
    name: str

    description: str | None = None
    connection_source: str = Field(
        ..., description="Source identifier, e.g., 'user:my_db' or 'file:...'"
    )

    # The specific action to be executed in this step.
    run: AnyConnectorAction = Field(..., discriminator="action")

    # A mapping to extract and name specific pieces of the step's result.
    outputs: Optional[Dict[str, str]] = Field(
        None,
        description="A mapping of output names to JMESPath queries to extract values from the result.",
    )
    depends_on: Optional[List[str]] = Field(
        None,
        description="A list of step IDs that must complete before this step can run.",
    )
    # A Jinja2 expression that determines if this step should be executed.
    if_condition: Optional[str] = Field(
        None,
        alias="if",
        description="A Jinja2 expression that must evaluate to true for the step to run.",
    )

    cache_config: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def set_default_id(self) -> "ConnectorStep":
        """If an 'id' is not provided, create a default one from the step's name."""
        if self.id is None:
            # Create a machine-friendly key from the human-readable name.
            self.id = self.name.replace(" ", "_").replace("-", "_").lower()
        return self


class ConnectorScript(BaseModel):
    name: str
    description: str | None = None
    steps: List[ConnectorStep]
    cache_config: Optional[Dict[str, Any]] = None
    script_input: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Placeholder for data piped from stdin."
    )
