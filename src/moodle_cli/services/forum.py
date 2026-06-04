"""Forum service."""

from __future__ import annotations

from pydantic import BaseModel

from moodle_cli.services.base import BaseService


class Forum(BaseModel):
    id: int
    course: int = 0
    name: str = ""
    type: str = ""
    intro: str = ""
    numdiscussions: int = 0


class Discussion(BaseModel):
    id: int
    discussion: int = 0
    name: str = ""
    subject: str = ""
    message: str = ""
    userid: int = 0
    userfullname: str = ""
    timemodified: int = 0
    # Activity signals returned by mod_forum_get_forum_discussions — previously
    # dropped, which is what blinded "who replied last / how many replies" and
    # broke the standing forum-debt ("ball with you") detection downstream.
    created: int = 0
    numreplies: int = 0
    numunread: int = 0
    usermodified: int = 0
    usermodifiedfullname: str = ""
    pinned: bool = False
    locked: bool = False


class Post(BaseModel):
    id: int
    discussionid: int = 0
    # parentid is null on the root post; other id fields can be absent too.
    parentid: int | None = None
    subject: str = ""
    message: str = ""
    timecreated: int = 0
    author: dict[str, object] = {}

    @property
    def author_name(self) -> str:
        a = self.author or {}
        return str(a.get("fullname") or a.get("name") or a.get("id") or "?")


class ForumService(BaseService):
    def list_forums(self, course_id: int) -> list[Forum]:
        data = self.call("mod_forum_get_forums_by_courses", courseids=[course_id])
        return [Forum(**f) for f in data]

    def get_discussions(self, forum_id: int) -> list[Discussion]:
        data = self.call("mod_forum_get_forum_discussions", forumid=forum_id)
        return [Discussion(**d) for d in data.get("discussions", [])]

    def get_posts(self, discussion_id: int) -> list[Post]:
        """Every post in a discussion (mod_forum_get_discussion_posts).

        Read-only: lists posts, does not log a view event (that would be
        mod_forum_view_forum_discussion, which is deliberately NOT allowlisted).
        """
        data = self.call("mod_forum_get_discussion_posts", discussionid=discussion_id)
        return [Post(**p) for p in data.get("posts", [])]

    def add_discussion(self, forum_id: int, subject: str, message: str) -> int:
        """Start a new discussion (write — only reachable via the full `moodle` CLI)."""
        data = self.call(
            "mod_forum_add_discussion",
            forumid=forum_id,
            subject=subject,
            message=message,
        )
        return int(data["discussionid"])
