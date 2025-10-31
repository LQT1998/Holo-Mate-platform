# backend/ai_service/src/realtime/metrics.py
"""
Prometheus metrics for the realtime (T114) layer with safe no-op fallback.

- If prometheus_client is installed → real metrics.
- If not → all hooks are no-op (the app still runs).

Quick start:
    from prometheus_client import make_asgi_app  # only if installed
    app.mount("/metrics", make_asgi_app())

Hooks to call from your code:
    - on_connect()/on_disconnect()
    - count_in(evt_type), count_out(evt_type, recipients), observe_room(n)
    - count_rl()  # rate-limited close
    - count_drop()  # dropped due to backpressure
    - frame_too_large(), bad_json(), error(reason)
    - auth_ok(), auth_error(reason)
    - heartbeat_ping_sent(), heartbeat_disconnect()
    - presence_joined(n), presence_left(n)
    - typing_emitted(), typing_suppressed()
    - read_receipt_recorded(), message_acked()
    - bus_published(), bus_consumed()
    - with time_event("message.new"): ...  # process-time histogram
"""

import time
from contextlib import contextmanager

# --------- Single guarded import ----------
try:
    from prometheus_client import Counter, Gauge, Histogram  # type: ignore
    _PROM_AVAILABLE = True
except Exception:  # pragma: no cover
    Counter = Gauge = Histogram = None  # type: ignore
    _PROM_AVAILABLE = False


# --------- No-op metric types ----------
class _NullMetric:
    def inc(self, *args, **kwargs):  # noqa: D401
        return
    def dec(self, *args, **kwargs):
        return
    def observe(self, *args, **kwargs):
        return
    def labels(self, *args, **kwargs):
        return self

# Factory helpers
def _gauge(*args, **kwargs):
    return Gauge(*args, **kwargs) if _PROM_AVAILABLE else _NullMetric()

def _counter(*args, **kwargs):
    return Counter(*args, **kwargs) if _PROM_AVAILABLE else _NullMetric()

def _hist(*args, **kwargs):
    return Histogram(*args, **kwargs) if _PROM_AVAILABLE else _NullMetric()


# --------- Metric definitions ----------
ws_connections_open = _gauge(
    "ws_connections_open",
    "Current number of open WebSocket connections",
)

ws_events_in_total = _counter(
    "ws_events_in_total",
    "Incoming WS events by type",
    ["type"],
)

ws_events_out_total = _counter(
    "ws_events_out_total",
    "Outgoing WS events by type (counted per-recipient)",
    ["type"],
)

ws_presence_joins_total = _counter(
    "ws_presence_joins_total",
    "Number of presence.join processed (incremented per-room joined)",
)

ws_presence_leaves_total = _counter(
    "ws_presence_leaves_total",
    "Number of presence.leave processed (incremented per-room left)",
)

ws_typing_emitted_total = _counter(
    "ws_typing_emitted_total",
    "Number of typing events actually broadcast (after debounce)",
)

ws_typing_suppressed_total = _counter(
    "ws_typing_suppressed_total",
    "Number of typing events suppressed by debounce",
)

ws_read_receipts_total = _counter(
    "ws_read_receipts_total",
    "Number of message.read processed (and broadcast)",
)

ws_messages_acked_total = _counter(
    "ws_messages_acked_total",
    "Number of message.ack sent to clients",
)

ws_rate_limited_total = _counter(
    "ws_rate_limited_total",
    "Connections closed due to WS rate limiting",
)

ws_frame_too_large_total = _counter(
    "ws_frame_too_large_total",
    "Frames rejected because they exceed WS_MAX_FRAME_BYTES",
)

ws_bad_json_total = _counter(
    "ws_bad_json_total",
    "Incoming frames that were not valid JSON",
)

ws_errors_total = _counter(
    "ws_errors_total",
    "Generic WS error events by reason",
    ["reason"],
)

ws_auth_ok_total = _counter(
    "ws_auth_ok_total",
    "Successful WS authentications",
)

ws_auth_error_total = _counter(
    "ws_auth_error_total",
    "WS auth errors by reason",
    ["reason"],
)

ws_heartbeat_pings_sent_total = _counter(
    "ws_heartbeat_pings_sent_total",
    "Number of heartbeat ping frames sent",
)

ws_heartbeat_disconnects_total = _counter(
    "ws_heartbeat_disconnects_total",
    "Connections closed due to missed heartbeats",
)

ws_bus_published_total = _counter(
    "ws_bus_published_total",
    "Events published to Redis bus",
)

ws_bus_consumed_total = _counter(
    "ws_bus_consumed_total",
    "Events consumed from Redis bus",
)

ws_dropped_messages_total = _counter(
    "ws_dropped_messages_total",
    "Messages dropped due to per-connection backpressure",
)

ws_room_broadcast_recipients = _hist(
    "ws_room_broadcast_recipients",
    "Distribution of recipient counts per broadcast",
    buckets=(0, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000),
)

ws_event_process_seconds = _hist(
    "ws_event_process_seconds",
    "Server-side processing time per incoming event (excluding IO to clients)",
    ["type"],
    buckets=(0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5),
)


# --------- Hook helpers (safe, never raise) ----------
def on_connect() -> None:
    try: ws_connections_open.inc()
    except Exception: pass

def on_disconnect() -> None:
    try: ws_connections_open.dec()
    except Exception: pass

def auth_ok() -> None:
    try: ws_auth_ok_total.inc()
    except Exception: pass

def auth_error(reason: str) -> None:
    try: ws_auth_error_total.labels(reason=reason).inc()
    except Exception: pass

def rate_limited() -> None:
    try: ws_rate_limited_total.inc()
    except Exception: pass

def count_rl() -> None:  # keep compatibility with existing calls
    rate_limited()

def frame_too_large() -> None:
    try: ws_frame_too_large_total.inc()
    except Exception: pass

def bad_json() -> None:
    try: ws_bad_json_total.inc()
    except Exception: pass

def error(reason: str) -> None:
    try: ws_errors_total.labels(reason=reason).inc()
    except Exception: pass

def heartbeat_ping_sent() -> None:
    try: ws_heartbeat_pings_sent_total.inc()
    except Exception: pass

def heartbeat_disconnect() -> None:
    try: ws_heartbeat_disconnects_total.inc()
    except Exception: pass

def presence_joined(count_rooms: int = 1) -> None:
    if count_rooms <= 0: return
    try: ws_presence_joins_total.inc(count_rooms)
    except Exception: pass

def presence_left(count_rooms: int = 1) -> None:
    if count_rooms <= 0: return
    try: ws_presence_leaves_total.inc(count_rooms)
    except Exception: pass

def typing_emitted() -> None:
    try: ws_typing_emitted_total.inc()
    except Exception: pass

def typing_suppressed() -> None:
    try: ws_typing_suppressed_total.inc()
    except Exception: pass

def read_receipt_recorded() -> None:
    try: ws_read_receipts_total.inc()
    except Exception: pass

def message_acked() -> None:
    try: ws_messages_acked_total.inc()
    except Exception: pass

def bus_published() -> None:
    try: ws_bus_published_total.inc()
    except Exception: pass

def bus_consumed() -> None:
    try: ws_bus_consumed_total.inc()
    except Exception: pass

def count_in(event_type: str) -> None:
    try: ws_events_in_total.labels(type=event_type or "unknown").inc()
    except Exception: pass

def count_out(event_type: str, recipients: int = 1) -> None:
    if recipients < 0: recipients = 0
    try:
        ws_events_out_total.labels(type=event_type or "unknown").inc(recipients)
        ws_room_broadcast_recipients.observe(recipients)
    except Exception: pass

def count_drop() -> None:
    try: ws_dropped_messages_total.inc()
    except Exception: pass

def observe_room(n: int) -> None:
    try: ws_room_broadcast_recipients.observe(max(0, n))
    except Exception: pass


# --------- Timing helper ----------
@contextmanager
def time_event(event_type: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        try:
            ws_event_process_seconds.labels(type=event_type or "unknown") \
                .observe(time.perf_counter() - start)
        except Exception:
            pass
