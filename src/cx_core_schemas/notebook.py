from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from .connector_script import ScriptInputParameter, ConnectorStep


# --- Block Model ---


# class Block(BaseModel):
#     """
#     Represents a single, executable or static unit of content within a Contextual Page.
#     """

#     id: str = Field(
#         ...,
#         description="A unique, user-defined identifier for the block within the page (e.g., 'get_raw_data').",
#     )

#     engine: Literal[
#         "markdown",
#         "sql",
#         "python",
#         "transform",
#         "ui-component",
#         "stream",
#         "agent",
#         "cx-action",
#         "shell",
#         "run",
#         "yaml",
#     ] = Field(
#         ...,
#         description="The execution engine responsible for processing the block's content.",
#     )

#     content: str = Field(
#         ...,
#         description="The source code, Markdown text, or declarative YAML content of the block.",
#     )

#     name: Optional[str] = Field(
#         None, description="An optional, human-readable name for the block."
#     )

#     inputs: List[str] = Field(
#         default_factory=list,
#         description="A list of dependencies this block has on the outputs of other blocks, specified as 'block_id.output_name'.",
#     )

#     outputs: List[str] = Field(
#         default_factory=list,
#         description="A list of named variables that this block produces for other blocks to consume.",
#     )

#     if_condition: Optional[str] = Field(
#         None,
#         alias="if",
#         description="A Jinja2 expression that must evaluate to true for the block to run.",
#     )

#     class Config:
#         populate_by_name = (
#             True  # Allows using 'if' as a field name, which is a Python keyword.
#         )


class ContextualPage(BaseModel):
    """
    The in-memory representation of a complete, executable `.cx.md` document.
    """

    id: Optional[str] = Field(
        None,
        description="The full, namespaced ID of the page (e.g., 'my-project/my-page').",
    )

    name: str = Field(
        ...,
        description="The primary name/title of the Contextual Page, derived from the front matter.",
    )

    description: Optional[str] = Field(
        None, description="A human-readable description of the page's purpose."
    )

    inputs: Dict[str, ScriptInputParameter] = Field(
        default_factory=dict,
        description="Parameters that can be passed to the entire page at runtime, making it a reusable function.",
    )

    blocks: List[ConnectorStep] = Field(
        ..., description="The ordered list of steps/blocks."
    )

    version: str = Field("1.0.0", description="The version of the Contextual Page.")

    author: Optional[str] = Field(
        None, description="The author of the Contextual Page."
    )

    tags: List[str] = Field(
        default_factory=list,
        description="A list of tags for categorization and discovery.",
    )
