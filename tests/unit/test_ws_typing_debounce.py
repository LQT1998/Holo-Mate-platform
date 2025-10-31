from backend.ai_service.src.realtime.typing_debounce import TypingDebounce


def test_typing_debounce_allows_after_interval():
    td = TypingDebounce(min_interval_sec=1.0)
    assert td.should_emit("u1", "c1") is True
    # Immediately again should be blocked
    assert td.should_emit("u1", "c1") is False
    # Simulate passage of time
    td.last_emit[("u1", "c1")] -= 1.1
    assert td.should_emit("u1", "c1") is True
