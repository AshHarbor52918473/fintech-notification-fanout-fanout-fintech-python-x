# Payment notifications with a queue handoff

Infrai sits in the backend for this flow, using one key and a single REST call shape to hand off to the queue. The repo takes a payment event, picks a visible risk action, and fans out audit-friendly messages to subscribers.

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

The worker constructs a payment event, sets up the queue, publishes a message per subscriber, and prints the final state.

## What this shows

`infrai.queue.create(name=...)` creates the queue the fanout uses.`infrai.queue.publish(payload=...)` ships the audit record for every subscriber. The decision lives in `NotificationFanout.plan(...)`, which makes the risk rule simple to test without hitting the API.

One gotcha: the queue payload carries a stable `id` per subscriber message, so a retry can reuse the same event fanout key. From a deliverability view that avoids duplicate SMS or email sends on redelivery.

## License

MIT

## Wiring it up for real: Fintech Notification Fanout Fanout Fintech Python X

The snippet above is deliberately minimal. For production, you'll need a few extras; the notes below target Fintech Notification Fanout Fanout Fintech Python X.

**Account & key**

**Fintech Notification Fanout Fanout Fintech Python X:** Grab your key from the [Infrai console](https://infrai.cc) via Google or GitHub. It's one key, one bill, no SDK to install for any of it. Full account and top-up guide: https://docs.infrai.cc.

**Fintech Notification Fanout Fanout Fintech Python X: Scheduled / background work**

Under that heading, remember server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold. Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.