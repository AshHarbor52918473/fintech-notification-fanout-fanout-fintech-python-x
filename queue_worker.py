import json
from typing import Any, Dict, List

from payment_fanout import NotificationFanout, PaymentEvent, Subscriber, build_payment_event


DEFAULT_SUBSCRIBERS: List[Subscriber] = [
    {"subscriber_id": "ops-ledger", "channel": "email", "risk_tier": "ops"},
    {"subscriber_id": "fraud-watch", "channel": "push", "risk_tier": "risk"},
    {"subscriber_id": "merchant-recon", "channel": "sms", "risk_tier": "finance"},
]


def handle_payment_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    event = build_payment_event(payload)
    fanout = NotificationFanout()
    plan = fanout.plan(event, DEFAULT_SUBSCRIBERS)
    published = fanout.publish_plan(plan)
    return {
        "payment_id": event.payment_id,
        "queue_name": plan.queue_name,
        "action": plan.action,
        "published_count": len(published),
    }


if __name__ == "__main__":
    sample = {
        "payment_id": "pay_1001",
        "merchant_id": "m_42",
        "amount_cents": 125000,
        "currency": "USD",
        "status": "captured",
    }
    print(json.dumps(handle_payment_event(sample), indent=2, sort_keys=True))
