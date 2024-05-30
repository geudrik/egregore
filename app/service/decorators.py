from functools import wraps

from app.logger import logger
from app.models.service import ReturnModel


def add_to_history(wrapped):
    """Decorator we use to decorate our Tag methods. So long as a tag method returns the complete JSON response from
    ES for any one given tag (the successfully updated object), this decorator will then use it and add it to the
    history Index"""

    @wraps(wrapped)
    async def inner(self, *args, **kwargs) -> ReturnModel:
        ret = await wrapped(self, *args, **kwargs)
        await self.history_service.add(ret)
        return ret

    return inner


def audit(action, component, subcomponent=None, subcomponent_action=None):
    """Decorator to audit all service calls. This will add an audit log entry for every call made to any given
    decorated service method.

    :arg action: The action being performed (eg: create, read, update, delete)
    :arg component: The component the action is being performed on (eg: tag, tag history, audit, comment, etc)
    :arg subcomponent: Optional, a secondary component that's having action taken against (eg: references, patterns)
    :arg subcomponent_action: Optional, the action being taken against the subcomponent (eg: create, update, delete)
    """

    def wrapper(wrapped):
        @wraps(wrapped)
        async def inner(self, *args, **kwargs) -> ReturnModel:
            ret: ReturnModel = await wrapped(self, *args, **kwargs)
            logger.debug(f"Adding new audit log : {action} {component} {self.user.username} : {ret.audit_message}")
            await self.audit_service.add(
                action=action,
                component=component,
                message=ret.audit_message,
                user=self.user.username,
                subcomponent=subcomponent,
                subcomponent_action=subcomponent_action,
                tag_id=ret.data.get("_id", None),
                version=ret.data.get("_version", None),
            )
            return ret

        return inner

    return wrapper
