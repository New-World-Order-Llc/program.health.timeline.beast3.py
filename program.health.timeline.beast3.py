# program.health.timeline.beast3.py
# Beast System 3.0 — Deterministic Health Timeline

from dataclasses import dataclass, field
import time
import hashlib

@dataclass
class TimelineEvent:
    family_id: str
    event_type: str
    payload: dict
    ts: float = field(default_factory=time.time)
    hash: str = ""

    def finalize(self):
        serialized = f"{self.family_id}{self.event_type}{self.payload}{self.ts}".encode("utf-8")
        self.hash = hashlib.sha256(serialized).hexdigest()

@dataclass
class HealthTimelineProfile:
    family_id: str
    events: list = field(default_factory=list)
    last_update: float = field(default_factory=time.time)

    def add_event(self, event: TimelineEvent):
        event.finalize()
        self.events.append(event)
        self.last_update = event.ts

class HealthTimelineEngine:
    def __init__(self, kernel):
        self.kernel = kernel
        self.timelines = {}

    def create_timeline(self, family_id: str):
        profile = HealthTimelineProfile(family_id)
        self.timelines[family_id] = profile

        return self.kernel.dispatch(
            module="health.timeline",
            action="create_timeline",
            payload={"family_id": family_id}
        )

    def log(self, family_id: str, event_type: str, payload: dict):
        if family_id not in self.timelines:
            raise ValueError("Timeline not found")

        event = TimelineEvent(
            family_id=family_id,
            event_type=event_type,
            payload=payload
        )

        profile = self.timelines[family_id]
        profile.add_event(event)

        return self.kernel.dispatch(
            module="health.timeline",
            action="log_event",
            payload={
                "family_id": family_id,
                "event_type": event_type,
                "payload": payload
            }
        )

    def get_events(self, family_id: str):
        return self.timelines.get(family_id, None)

    def get_range(self, family_id: str, start_ts: float, end_ts: float):
        profile = self.timelines.get(family_id, None)
        if not profile:
            return None

        return [
            e for e in profile.events
            if start_ts <= e.ts <= end_ts
        ]
