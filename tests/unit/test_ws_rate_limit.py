from backend.ai_service.src.realtime.rate_limit import TokenBucket


def test_token_bucket_per_10s():
    tb = TokenBucket.per_10s(5)
    for _ in range(5):
        assert tb.consume()
    assert not tb.consume()
    tb.last_refill -= 10.1
    assert tb.consume()


