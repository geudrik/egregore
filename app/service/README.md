## General Notes

## Services

The primary business logic for the app lives here in these services. Services are broken up into logical domains of
ownership (loosely 1:1 to the indexes in OpenSearch)

### Base Service

All services inherit from [this base](base.py). This base outlines a couple primary methods that are shared across the
board with all services

#### Count

Returns the number count of the number of docs that exist that are not deleted (default, all deletes are soft deletes).
Optionally, count all docs (including those that are deleted)

#### Get

This is a shared method to retrieve a doc by its ID (by the doc ID within OpenSearch), optionally performing an eager
sequence
validation.

> [!NOTE]
> Due to the expected minimal volume (size _and_ write calls), all OpenSearch indexes for the purpose of this POC are
_not_ chronologically rotated. In a production system, they would (and should) be where it makes sense (eg: the audit
> trail, tag history, etc). While that functionality isn't coded, the services are written in such a way that enabling
> that functionality would be relatively trivial (see the `@property` methods of this base service)

#### List

Used for endpoints that list all `things`. By design, supports pagination, filtering, and sorting. Called by endpoints
that drive listing tables in the UI

### Tag Service

Performs actions for the manipulation and retrieval of tags. The most complex service. See methods for additional
context about what they do and how they work

### Tag History Service

Simple service to automatically add historical changes to the running history set for any given tag. Fairly simple
service as writes happen automatically, and a user can only get and list entries based on criteria

### Audit Service

Interact with the Audit trail. Very simple service as writes happen automatically, and the only things a user can do is
list based on criteria

### Comment Service

TODO: