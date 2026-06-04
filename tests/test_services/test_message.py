"""Message service model tests — guard the nullable fields Moodle actually sends."""

from __future__ import annotations

from moodle_cli.services.message import Conversation


def test_conversation_accepts_null_unreadcount() -> None:
    # Moodle returns unreadcount=null for a conversation with nothing unread.
    # The model must tolerate it (regression: it used to require int and 500'd).
    conv = Conversation(id=1413749, name="", type=3, membercount=1, unreadcount=None)
    assert conv.unreadcount is None


def test_conversation_keeps_int_unreadcount() -> None:
    conv = Conversation(id=1, unreadcount=4)
    assert conv.unreadcount == 4
