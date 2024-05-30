from datetime import datetime
from uuid import UUID

from app.logger import logger
from app.service.base import BaseService


class AuditService(BaseService):

    _index_name = "tags-audit"

    def __init__(self, user, client):
        super().__init__(client)
        self.user = user

        # This is a work-around, since audit log creation is a decorator
        self.audit_service = self

    async def add(
        self,
        action: str,
        component: str,
        message: str,
        user: str,
        subcomponent: str = None,
        subcomponent_action: str = None,
        tag_id: UUID = None,
        version: int = None,
    ) -> None:
        """Create a new Audit entry
        :arg action: Action to perform
        :arg component: The component the action is being performed on (tag, tag history, audit, comment, etc)
        :arg user: The user that's performing this action
        :arg message: A message describing what's going on and/or why
        :arg subcomponent: Optional, a secondary component that's having action taken against (eg: references, patterns)
        :arg subcomponent_action: Optional, the action being taken against the subcomponent (eg: create, update, delete)
        :arg tag_id: Optional, the ID of a Tag if available
        :arg version: Optional, the version of the Tag if available
        """
        body = {
            "created": datetime.utcnow(),
            "action": action,
            "component": component,
            "user": user,
            "message": message,
            "subcomponent": subcomponent,
            "subcomponent_action": subcomponent_action,
            "tag_id": tag_id,
            "version": version,
        }
        logger.debug("Adding new Audit entry", **body)
        await self._index(body=body)

    async def metrics(self, bucket_size=100) -> dict:
        """Agg our audit logs"""
        body = {
            "size": 0,
            "aggs": {
                "unique_components": {
                    "terms": {"field": "component", "size": bucket_size},
                    "aggs": {
                        "unique_actions": {
                            "terms": {"field": "action", "size": bucket_size},
                            "aggs": {
                                "unique_sub_components": {
                                    "terms": {"field": "subcomponent", "size": bucket_size},
                                    "aggs": {
                                        "unique_sub_component_actions": {
                                            "terms": {"field": "subcomponent_action", "size": bucket_size},
                                            "aggs": {"unique_docs": {"cardinality": {"field": "_id"}}},
                                        }
                                    },
                                }
                            },
                        }
                    },
                }
            },
        }

        aggs = await self.client.search(index=self.index_name_read, body=body)

        summary = {"components": []}

        for component_bucket in aggs["aggregations"]["unique_components"]["buckets"]:
            component = component_bucket["key"]
            summary["components"].append(
                {"count": component_bucket["doc_count"], "component": component, "actions": []}
            )

            for action_bucket in component_bucket["unique_actions"]["buckets"]:
                action = action_bucket["key"]
                summary["components"][-1]["actions"].append(
                    {"count": action_bucket["doc_count"], "action": action, "subcomponents": []}
                )

                for sub_component_bucket in action_bucket["unique_sub_components"]["buckets"]:
                    sub_component = sub_component_bucket["key"]
                    summary["components"][-1]["actions"][-1]["subcomponents"].append(
                        {
                            "count": sub_component_bucket["doc_count"],
                            "name": sub_component,
                            "actions": [],
                        }
                    )

                    for sub_component_action_bucket in sub_component_bucket["unique_sub_component_actions"]["buckets"]:
                        sub_component_action = sub_component_action_bucket["key"]
                        unique_count = sub_component_action_bucket["unique_docs"]["value"]

                        summary["components"][-1]["actions"][-1]["subcomponents"][-1]["actions"].append(
                            {
                                "action": sub_component_action,
                                "count": unique_count,
                            }
                        )

        return summary
