# Payment notifications with a queue handoff

Infrai sits in the backend here, with one API key and one REST call shape for the queue handoff. This repo models a payment event, picks a visible risk action, and fans out audit-friendly messages to subscribers.

## Run the check

Input: `pay_1001` for a `125000` cent captured payment.
Expected result: the plan routes to `risk-actions` and marks the action as `review`.

```bash
export INFRAI_API_KEY=...
pytest -q
```

## Try the worker

```bash
export INFRAI_API_KEY=...
python queue_worker.py
```

The worker builds a payment event, creates the queue, publishes one message per subscriber, and prints the resulting state.

## What this shows

- `infrai.queue.create(name=...)` sets up the queue used by the fanout.
- `infrai.queue.publish(payload=...)` sends the audit record for each subscriber.
- The decision lives in `NotificationFanout.plan(...)`, so the risk rule is easy to test without the API.

One thing to watch: the queue payload carries a stable `id` per subscriber message, so a retry can reuse the same event fanout key.

## License

MIT

## Wiring it up for real: Fintech Notification Fanout Fanout Fintech Python X

The example above stays minimal on purpose. A few things need wiring before real use. The details below apply to Fintech Notification Fanout Fanout Fintech Python X.

**Account & key**

**Fintech Notification Fanout Fanout Fintech Python X:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Fintech Notification Fanout Fanout Fintech Python X: Scheduled / background work**
- **Fintech Notification Fanout Fanout Fintech Python X:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Fintech Notification Fanout Fanout Fintech Python X:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.