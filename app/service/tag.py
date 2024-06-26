from datetime import datetime
from uuid import UUID, uuid4

from app.lib.exceptions import NotFound
from app.logger import logger
from app.models.pagination import SortingArgs, FilteringArgs, PaginationArgs
from app.models.sequence import DocumentSequence
from app.models.service import ReturnModel
from app.service.audit import AuditService
from app.service.base import BaseService
from app.service.decorators import audit, add_to_history
from app.service.tag_history import TagHistoryService


class TagService(BaseService):

    _index_name = "tags-latest"

    def __init__(self, user, client, history_service: TagHistoryService, audit_service: AuditService):
        super().__init__(client)
        self.user = user
        self.history_service = history_service
        self.audit_service = audit_service

    def _update_meta(self, payload):
        """Update the meta information for a tag"""
        now = datetime.utcnow()
        payload["updated"] = now
        payload["editor"] = self.user.username
        payload["state"] = None
        return payload

    async def _get_tag_for_editing(self, tag_id: UUID, sequence: DocumentSequence) -> ReturnModel:
        """Get a tag for editing, updating all of the metadata fields along the way"""
        tag = await self.get(tag_id, sequence=sequence)
        tag.data["_source"] = self._update_meta(tag.data["_source"])
        return tag

    async def count(self, include_deleted: bool = False) -> int:
        """Counts all tags, by default excluding those that are deleted
        :arg include_deleted if True, include deleted tags in the count"""
        query = None
        if not include_deleted:
            query = {"query": {"bool": {"must_not": {"exists": {"field": "deleted"}}}}}
        return await super(TagService, self).count(query)

    async def count_patterns(self) -> dict:
        """Perform a count of all patterns in the Tags index (just sum the total number of patterns across all tags)
        TODO: This is inefficient. Ensure this is cached
        """
        agg = await self.client.search(
            index=self.index_name_read,
            body={
                "_source": False,
                "size": 0,
                "query": {"nested": {"path": "patterns", "query": {"match_all": {}}}},
                "aggregations": {
                    "nested_patterns_count": {
                        "nested": {"path": "patterns"},
                        "aggregations": {"unique_patterns": {"cardinality": {"field": "patterns.id"}}},
                    }
                },
            },
        )

        return {
            "patterns": {
                "count": agg.get("aggregations", {}).get("nested_patterns_count", {}).get("doc_count", 0),
                "unique": agg.get("aggregations", {})
                .get("nested_patterns_count", {})
                .get("unique_patterns", {})
                .get("value", 0),
            }
        }

    async def count_clauses(self) -> dict:
        """
        TODO: This is inefficient. Ensure this is cached
        :return:
        """
        agg = await self.client.search(
            index=self.index_name_read,
            body={
                "_source": False,
                "size": 0,
                "query": {"nested": {"path": "patterns.clauses", "query": {"match_all": {}}}},
                "aggregations": {
                    "nested_clauses_count": {
                        "nested": {"path": "patterns.clauses"},
                        "aggregations": {"clauses_count": {"cardinality": {"field": "patterns.clauses.id"}}},
                    }
                },
            },
        )

        return {
            "clauses": {
                "count": agg.get("aggregations", {}).get("nested_clauses_count", {}).get("doc_count", 0),
                "unique": agg.get("aggregations", {})
                .get("nested_clauses_count", {})
                .get("clauses_count", {})
                .get("value", 0),
            }
        }

    async def list(
        self,
        pagination: PaginationArgs = PaginationArgs(),
        filtering: FilteringArgs = FilteringArgs(),
        sorting: SortingArgs = SortingArgs(),
        include_deleted: bool = True,
    ) -> ReturnModel:
        """Perform a tag listing"""

        extra_filter = None
        if not include_deleted:
            extra_filter = {"bool": {"must_not": {"exists": {"field": "deleted"}}}}

        total_count: int = await self.count(include_deleted=include_deleted)
        results = await super(TagService, self).list(pagination, filtering, sorting, extra_filter=extra_filter)

        return ReturnModel(results.data, total=total_count, limit=results.limit, offset=results.offset)

    @audit("read", "tag")
    @add_to_history
    async def create(self, tag_data: dict) -> ReturnModel:
        """Create a new tag"""
        new_id = uuid4()
        tag_data = self._update_meta(tag_data)
        tag_data["author"] = self.user.username
        tag_data["created"] = tag_data["updated"]
        logger.info(f"Creating new Tag [{tag_data['name']}]", tag_id=new_id)
        new_tag = await self._index(tag_data, doc_id=new_id)

        return ReturnModel(new_tag, audit_message="Creating new Tag")

    @audit("update", "tag", subcomponent="references", subcomponent_action="create")
    @add_to_history
    async def create_reference(self, tag_id: UUID, sequence: DocumentSequence, payload: dict) -> ReturnModel:
        """Create a new reference for the supplied tag"""
        existing = await self._get_tag_for_editing(tag_id, sequence)
        existing = existing.data["_source"]

        logger.info("Creating new reference for Tag", tag_id=tag_id)

        # Since tags may not have a references field at all yet, we need to ensure it exists
        existing["references"] = existing.get("references", [])

        # Create a payload we pass off to our update call that contains only the top level field
        existing["references"].append(payload)

        ret = await self._index(doc_id=tag_id, body=existing, sequence=sequence)
        return ReturnModel(
            ret, audit_message=f"Tag [{tag_id}] had {list(payload.keys())} modified by [{self.user.username}]"
        )

    @audit("update", "tag", subcomponent="patterns", subcomponent_action="create")
    @add_to_history
    async def create_pattern(self, tag_id: UUID, sequence: DocumentSequence, payload: dict) -> ReturnModel:
        """Create a new pattern for the supplied tag"""
        existing = await self._get_tag_for_editing(tag_id, sequence)
        existing = existing.data["_source"]

        logger.info("Creating new pattern for Tag", tag_id=tag_id)

        # Since tags may not have a patterns field at all yet, we need to ensure it exists
        existing["patterns"] = existing.get("patterns", [])

        # Create a payload we pass off to our update call that contains only the top level field
        existing["patterns"].append(payload)

        ret = await self._index(doc_id=tag_id, body=existing, sequence=sequence)
        ret["_audit_message"] = "whatever"

        return ReturnModel(
            ret, audit_message=f"Tag [{tag_id}] had {list(payload.keys())} modified by [{self.user.username}]"
        )

    @audit("update", "tag")
    @add_to_history
    async def update(self, tag_id: UUID, sequence: DocumentSequence, payload: dict) -> ReturnModel:
        logger.info(f"Updating Tag base info", tag_id=tag_id)
        tag = await self._get_tag_for_editing(tag_id, sequence=sequence)

        updated_tag = tag.data["_source"] | payload
        ret = await self._index(doc_id=tag_id, body=updated_tag, sequence=sequence)

        return ReturnModel(
            ret, audit_message=f"Tag [{tag_id}] had {list(payload.keys())} modified by [{self.user.username}]"
        )

    @audit("update", "tag", subcomponent="references", subcomponent_action="update")
    @add_to_history
    async def update_reference(
        self, tag_id: UUID, sequence: DocumentSequence, reference_id: str, payload: dict
    ) -> ReturnModel:
        tag = await self._get_tag_for_editing(tag_id, sequence=sequence)
        tag = tag.data["_source"]

        if not tag["references"]:
            raise NotFound("No references found for the supplied Tag")

        # Find the reference by ID
        for ref in tag["references"]:
            if ref["id"] == reference_id:
                ref.update(payload)
                break
        else:
            raise NotFound("No reference found with the supplied ID")

        ret = await self._index(doc_id=tag_id, body=tag, sequence=sequence)

        return ReturnModel(
            ret, audit_message=f"Tag [{tag_id}] had reference {reference_id} modified by [{self.user.username}]"
        )

    @audit("delete", "tag")
    @add_to_history
    async def delete(self, tag_id: UUID, sequence: DocumentSequence) -> ReturnModel:
        logger.info(f"Deleting Tag", tag_id=tag_id)
        tag = await self._get_tag_for_editing(tag_id, sequence=sequence)
        tag = tag.data["_source"]

        # Set our deleted field to be the same as the update timestamp to signify this tag has been deleted
        tag["deleted"] = tag["updated"]

        deleted = await self._index(doc_id=tag_id, body=tag, sequence=sequence)
        return ReturnModel(deleted, audit_message=f"Tag [{tag['name']}] deleted")

    @audit("update", "tag", subcomponent="references", subcomponent_action="delete")
    @add_to_history
    async def delete_reference(self, tag_id: UUID, sequence: DocumentSequence, reference_id: str) -> ReturnModel:
        tag = await self._get_tag_for_editing(tag_id, sequence=sequence)
        tag = tag.data["_source"]

        if not tag["references"]:
            raise NotFound("No references found for the supplied Tag")

        # Remove the reference by ID
        new_references = [ref for ref in tag["references"] if ref["id"] != reference_id]
        if len(new_references) == len(tag["references"]):
            raise NotFound("No reference found with the supplied ID")

        tag["references"] = new_references
        ret = await self._index(doc_id=tag_id, body=tag, sequence=sequence)

        return ReturnModel(ret, audit_message=f"Tag [{tag_id}] had reference {reference_id} deleted")
