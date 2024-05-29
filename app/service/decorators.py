def add_to_history(wrapped):
    """Decorator we use to decorate our Tag methods. So long as a tag method returns the complete JSON response from
    ES for any one given tag (the successfully updated object), this decorator will then use it and add it to the
    history Index"""

    async def inner(self, *args, **kwargs) -> tuple:
        audit_args, ret = await wrapped(self, *args, **kwargs)
        await self.history_service.add(ret)
        return audit_args, ret

    return inner


def audit(wrapped):
    """Decorator to audit all service calls. This will add an audit log entry for every call made to the service"""

    async def inner(self, *args, **kwargs) -> dict:
        audit_args, ret = await wrapped(self, *args, **kwargs)
        audit_args["user"] = self.user.username
        await self.audit_service.add(**audit_args)
        return ret

    return inner
