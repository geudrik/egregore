from abc import ABC, abstractmethod
from typing import List

import opensearchpy
from opensearchpy import AsyncOpenSearch

from app.env import OPENSEARCH_INDEX_PREFIX
from app.lib.exceptions import IntegrityError, ServerError, NotFound
from app.models.pagination import PaginationArgs, FilteringArgs, SortingArgs
from app.models.sequence import DocumentSequence
from app.models.service import ReturnModel


class AbstractBaseService(ABC):

    _index_name: str

    @abstractmethod
    def __init__(self):
        raise NotImplementedError("Please Implement this method")

    @property
    @abstractmethod
    def index_name_write(self):
        raise NotImplementedError("Please Implement this method")

    @property
    @abstractmethod
    def index_name_read(self):
        raise NotImplementedError("Please Implement this method")


class BaseService(AbstractBaseService):

    def __init__(self, client: AsyncOpenSearch):
        self.client = client

    @property
    def index_name_write(self) -> str:
        """In the event that there's enough data here to warrant time stamped index names, can update that here
        Note that if we migrate to chronological index names, we will need to update routes on CRUD calls to get the
        'created' value for a given tag. Alternatively, this could just be blindly added into the sequence
        """
        return f"{OPENSEARCH_INDEX_PREFIX}{self._index_name}"

    @property
    def index_name_read(self) -> str:
        """Even if we have timestamped indexes, this should be the alias name since that's where reads come from
        Note that if we migrate to chronological index names, we will need to update routes on CRUD calls to get the
        'created' value for a given tag. Alternatively, this could just be blindly added into the sequence
        """
        return f"{OPENSEARCH_INDEX_PREFIX}{self._index_name}"

    @staticmethod
    def generate_listing_query(
        pagination: PaginationArgs = PaginationArgs(),
        filtering: FilteringArgs = FilteringArgs(),
        sorting: SortingArgs = SortingArgs(),
        extra_filter: dict | None = None,
    ):
        """Generates the lucene query we can use for listed endpoints"""
        # Begin creating our Query
        body = {
            "version": True,  # Include the doc version
            "from": pagination.offset,
            "size": pagination.limit,
            "sort": [{f"{sorting.sort_by}": sorting.sort_order}],
            "query": {"bool": {"must": []}},
        }

        # Add filtering args
        if filtering.q:
            body["query"]["bool"]["must"].append({"query_string": {"query": filtering.q}})

        # Allow for an optional additional MUST clause
        if extra_filter is not None:
            body["query"]["bool"]["must"].append(extra_filter)

        return body

    async def _index(self, body, doc_id=None, sequence: DocumentSequence = None) -> dict:
        """Preform an index of a document (add or overwrite optionally [upsert])"""
        res = await self.client.index(
            index=self.index_name_write,
            body=body,
            id=doc_id if doc_id else None,
            refresh=True,
            if_primary_term=sequence.primary_term if sequence is not None else None,
            if_seq_no=sequence.seq_no if sequence is not None else None,
        )

        # Merge the two dicts
        faked_source = {"_source": body}
        this_doc = res | faked_source

        return this_doc

    async def count(self, query: dict = None) -> int:
        """Perform a count, optionally taking filter params
        :arg query The query used to perform the count of docs against. If unset, will count everything"""
        result = await self.client.count(
            index=self.index_name_read,
            body=query if query else None,
        )
        return result.get("count", 0)

    async def get(
        self, doc_id, sequence: DocumentSequence = None, fields: List[str] = None, allow_deleted: bool = False
    ) -> ReturnModel:
        """Get a single doc by ID. If a sequence is supplied, it will be tested to ensure matches the fetched doc
        TODO: If we start using timestamped indexes for things, need to also pass the created date for this so we
            can calculate the index we need to query"""

        try:
            res = await self.client.get(
                index=self.index_name_read,
                id=doc_id,
                _source_includes=fields if fields is not None else None,
            )

            if res["_source"].get("deleted"):
                if not allow_deleted:
                    raise NotFound(f"No document found for {doc_id}")

        except opensearchpy.exceptions.NotFoundError:
            raise NotFound(f"No document found for {doc_id}")

        if sequence is not None and f"{res['_seq_no']},{res['_primary_term']}" != sequence.string:
            raise IntegrityError(
                "Supplied sequence does not match existing. Please fetch first, and use the returned sequence and make "
                "the call again"
            )

        return ReturnModel(res)

    async def list(
        self,
        pagination: PaginationArgs = PaginationArgs(),
        filtering: FilteringArgs = FilteringArgs(),
        sorting: SortingArgs = SortingArgs(),
        extra_filter: dict | None = None,
    ) -> ReturnModel:
        """List all docs outlined by the query params passed in"""

        body = self.generate_listing_query(pagination, filtering, sorting, extra_filter)
        try:
            result = await self.client.search(body=body, index=self.index_name_read, seq_no_primary_term=True)

        except opensearchpy.exceptions.RequestError as e:
            raise ServerError(str(e))

        result_list = []
        for res in result.get("hits", {}).get("hits", []):
            result_list.append(res)

        return ReturnModel(
            result_list,
            limit=pagination.limit,
            offset=pagination.offset,
        )
