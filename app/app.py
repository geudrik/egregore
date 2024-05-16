from fastapi import FastAPI

from app.api.middlewares.request_logging import attach_request_logging
from app.api.routes.tags import tags_router
from app.env import CYCLE_INDEX_TEMPLATES
from app.logger import logger

tags_metadata = [
    {
        "name": "Tags",
        "description": "Manage Tags, their visibilities, searches, etc",
    },
    {"name": "Tag History", "description": "All changes to a tag are preserved in a historical log"},
    # Future idea: the idea of "publishing" a tag to a backend. This idealistic backend would handle the automagic
    #   application of associating a given tag ID to an item in the data backend to add context to it, by relying on
    #   the searches the Tag outlines to determine whether the ~thing is a match or not
    # {
    #     "name": "Published Tags",
    #     "description": "When tags are published, a copy of them is PUT into the published index. The idea is that the "
    #                    "backend system responsible for actually executing the queries is separate from this system, so "
    #                    "to track what a user has published, we just PUT the specific tag version into the published "
    #                    "index."
    # },
    {"name": "Comments", "description": "Comment management"},
    {"name": "Audit", "description": "Methods to view the audit log for the system"},
    {
        "name": "Paginated",
        "description": "These endpoints are paginated. See the pagination model for details on response type",
    },
]

description = """
*Ever wish you had a central place for storing sets of hunting queries along side a bunch of contextual information?*

Well, wish no more! This little app is an [OpenSearch](https://opensearch.org/) backed RESTful API written for threat 
researchers. Besides storing sets of searches and contextual information about those searches, it also audits every 
action and records all changes to individual tags. So you get the info you care about lumped logically together, full 
auditability, and the ability to diff changes between version 3 and 11!

### Important Terms

- `Tag` : A collection of metadata that adds context to the searchers (known as 'searches') bucketed underneath. A 
Tag must contain at least one Search
- `Search` : A set of one or more Queries that comprise a complete ~thing to search for. A `Search` must contain at 
least one Query, and also contains additional metadata providing it an optional bounds, and either an AND or OR logic
that applies to all Queries that are a part of the Search.
- `Query` : A single item lookup - the most basic of "searches", but lacks bounding

Check out the models below to get a better understanding of what the shapes of these objects take.

### Sequences

You'll notice that a handful of routes have a URL parameter called `sequence`. This is akin to a "version ID", and is 
the simplest way to solve the transactional safety problem in a system that's eventually consistent (OpenSearch). 

This is a short string returned on every read call (for things you're able to edit). You'll need to `GET` the latest 
version, and use the contained sequence returned in your `PUT`/`PATCH`/`DELETE` calls. This ensures that someone else 
doesn't change the thing you think you're changing while you're trying to make your change (it avoids race conditions)

#### How To Use

TODO: Once we've written some routes, do a walk-through of how we can get the latest sequence (and object), and use it
to preform an update to that object
"""

logger.info("Creating FastAPI App")
app_args = {
    "openapi_tags": tags_metadata,
    "title": "Egregore: A Hunting Catalog for Everyone",
    "description": description,
}

if CYCLE_INDEX_TEMPLATES:
    from app.development import lifecycle_manager

    logger.info("Index cycling is ENABLED")
    app_args["lifespan"] = lifecycle_manager


app = FastAPI(**app_args)
attach_request_logging(app)

routers = [
    tags_router,
]
for router in routers:
    logger.info(f"Loading router for {router.prefix}")
    app.include_router(router)
