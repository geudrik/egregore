import json
import pathlib
from typing import Callable

import loguru
import opensearchpy
from opensearchpy import AsyncOpenSearch

from app.env import OPENSEARCH_INDEX_PREFIX
from app.logger import logger


def handle_client_interaction(func):
    async def inner(self, *args, **kwargs):
        try:
            await func(self, *args, **kwargs)

        except opensearchpy.exceptions.NotFoundError:
            # TODO: Ideally have the template name from _meta logged as well?
            logger.exception("Failed to delete index template")

    return inner


class Manager:
    templates_dir = f"{pathlib.Path(__file__).resolve().parent.resolve()}/index_templates"

    templates = [
        "tag.template.json",
        "tag_audit.template.json",
        "tag_comments.template.json",
        "tag_history.template.json",
    ]

    component_templates = [
        "tag.component.json",
    ]

    def __init__(self, client: AsyncOpenSearch, logger: loguru.logger):
        self.client = client
        self.logger = logger

    def _load_template_data(self, template) -> dict:
        with open(f"{self.templates_dir}/{template}", "r") as handle:
            return json.loads(handle.read())

    @handle_client_interaction
    async def _call_client(self, func: Callable, args: dict) -> dict:
        """Thin wrapper to streamline calls to OpenSearch here"""
        self.logger.debug(f"{func.__dict__['__wrapped__'].__name__}({args['name']})")
        return await func(**args)

    async def nuke(self):
        """Bigg hammer - deletes everything. Data, Indexes, Templates, etc"""
        await self.delete_indexes()
        await self.delete_templates()
        await self.delete_component_templates()

    async def delete_indexes(self):
        """Deletes all indexes"""
        pattern = f"{OPENSEARCH_INDEX_PREFIX}tags-*"
        self.logger.warning(f"Deleting all indexes that match {pattern}")
        await self.client.indices.delete(index=pattern)

    @handle_client_interaction
    async def delete_templates(self):
        """Deletes all index templates from OpenSearch"""
        self.logger.warning("Deleting all index templates")
        for template in reversed(self.templates):
            data = self._load_template_data(template)
            name = f"{OPENSEARCH_INDEX_PREFIX}{data['_meta']['name']}"
            args = {"name": name}
            await self._call_client(self.client.indices.delete_index_template, args)

    @handle_client_interaction
    async def delete_component_templates(self):
        """Deletes all index component templates from OpenSearch"""
        self.logger.warning("Deleting all component templates")
        for template in reversed(self.component_templates):
            data = self._load_template_data(template)
            name = f"{OPENSEARCH_INDEX_PREFIX}{data['_meta']['name']}"
            args = {"name": name}
            await self._call_client(self.client.cluster.delete_component_template, args)

    @handle_client_interaction
    async def create_component_templates(self):
        """Creates all of our component templates"""
        self.logger.warning("Creating all component templates")
        for template in reversed(self.component_templates):
            data = self._load_template_data(template)
            name = f"{OPENSEARCH_INDEX_PREFIX}{data['_meta']['name']}"
            args = {"name": name, "body": data}
            await self._call_client(self.client.cluster.put_component_template, args)

    @handle_client_interaction
    async def create_templates(self):
        """Creates all of our templates"""
        self.logger.warning("Creating all templates")
        for template in reversed(self.templates):
            data = self._load_template_data(template)
            name = f"{OPENSEARCH_INDEX_PREFIX}{data['_meta']['name']}"

            # Audit and Comment indexes aren't composed of the component template, so skip those
            if "audit" not in name and "comment" not in name:
                data["composed_of"] = [f"{OPENSEARCH_INDEX_PREFIX}{data['composed_of'][0]}"]

            data["index_patterns"] = [f"{OPENSEARCH_INDEX_PREFIX}{data['index_patterns'][0]}"]
            args = {"name": name, "body": data}
            await self._call_client(self.client.indices.put_index_template, args)
