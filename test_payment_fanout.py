from payment_fanout import NotificationFanout, PaymentEvent


def test_high_value_payment_goes_to_risk_actions_queue():
    event = PaymentEvent(
        payment_id="pay_1001",
        merchant_id="m_42",
        amount_cents=125000,
        currency="USD",
        status="captured",
    )
    subscribers = [
        {"subscriber_id": "ops-ledger", "channel": "email", "risk_tier": "ops"},
        {"subscriber_id": "fraud-watch", "channel": "push", "risk_tier": "risk"},
    ]
    plan = NotificationFanout().plan(event, subscribers)

    assert plan.action == "review"
    assert plan.queue_name == "risk-actions"
    assert plan.messages[0]["id"] == "pay_1001:ops-ledger"
    assert plan.messages[1]["action"] == "review"
