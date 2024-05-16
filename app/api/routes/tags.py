from fastapi import APIRouter

tags_router = APIRouter(prefix="/tags", tags=["Tags"])


@tags_router.get("/{example_url_arg}")
def list_all_tags(example_url_arg: str = "Default value for this arg"):
    return {"message": "All tags", "supplied_arg": example_url_arg}
