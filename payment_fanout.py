from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Literal, TypedDict

import infrai

Channel = Literal["email", "sms", "push"]
Action = Literal["review", "notify"]


class Subscriber(TypedDict):
    subscriber_id: str
    channel: Channel
    risk_tier: str


@dataclass(frozen=True)
class PaymentEvent:
    payment_id: str
    merchant_id: str
    amount_cents: int
    currency: str
    status: Literal["captured", "failed", "refunded"]


@dataclass(frozen=True)
class NotificationPlan:
    event: PaymentEvent
    action: Action
    queue_name: str
    messages: List[Dict[str, Any]]


class NotificationFanout:
    def plan(self, event: PaymentEvent, subscribers: Iterable[Subscriber]) -> NotificationPlan:
        action: Action = "review" if event.amount_cents >= 100000 or event.status == "failed" else "notify"
        queue_name = "risk-actions" if action == "review" else "payment-notifications"
        messages: List[Dict[str, Any]] = []
        for sub in subscribers:
            messages.append(
                {
                    "id": f"{event.payment_id}:{sub['subscriber_id']}",
                    "subscriber_id": sub["subscriber_id"],
                    "channel": sub["channel"],
                    "risk_tier": sub["risk_tier"],
                    "payment_id": event.payment_id,
                    "merchant_id": event.merchant_id,
                    "amount_cents": event.amount_cents,
                    "currency": event.currency,
                    "status": event.status,
                    "action": action,
                }
            )
        return NotificationPlan(event=event, action=action, queue_name=queue_name, messages=messages)

    def create_queue(self, queue_name: str) -> Dict[str, Any]:
        return infrai.queue.create(name=queue_name)

    def publish_plan(self, plan: NotificationPlan) -> List[Dict[str, Any]]:
        published = []
        for message in plan.messages:
            published.append(infrai.queue.publish(queue=plan.queue_name, payload=message))
        return published


def build_payment_event(payload: Dict[str, Any]) -> PaymentEvent:
    return PaymentEvent(
        payment_id=payload["payment_id"],
        merchant_id=payload["merchant_id"],
        amount_cents=int(payload["amount_cents"]),
        currency=payload["currency"],
        status=payload["status"],
    )
