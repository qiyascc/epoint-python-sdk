# Subscriptions with saved cards

A monthly subscription in three parts: the first payment saves the card, a daily job charges due subscriptions, and failed charges are retried a few times before the subscription is paused.

## Part 1. The first payment saves the card

```python
from epoint_sdk import Epoint

epoint = Epoint()

def start_subscription(user, plan):
    sub = Subscription.objects.create(user=user, plan=plan, state="pending")
    order_id = f"SUB-{sub.pk}-1"
    sub.last_order_id = order_id
    sub.save()

    reg = epoint.cards.register_and_pay(plan.price, order_id, description=f"{plan.name}, first month")
    sub.card_id = reg.card_id or ""
    sub.save()
    return reg.redirect_url
```

When the callback arrives with `tx.paid`, the subscription becomes active and the card is ready:

```python
def on_callback(tx):
    sub = Subscription.objects.select_for_update().get(last_order_id=tx.order_id)
    if not tx.matches(order_id=sub.last_order_id, amount=sub.plan.price):
        return
    if tx.paid:
        sub.card_id = tx.card_id or sub.card_id
        sub.card_mask = tx.card_mask or ""
        sub.state = "active"
        sub.paid_until = add_month(today())
        sub.save()
```

## Part 2. The daily billing job

```python
from epoint_sdk import GatewayError, NotSentError, OutcomeUnknownError

def bill_due_subscriptions():
    for sub in Subscription.objects.filter(state="active", paid_until__lte=today()):
        bill(sub)

def bill(sub):
    period = sub.paid_until.strftime("%Y%m")
    order_id = f"SUB-{sub.pk}-{period}-{sub.failures + 1}"
    sub.last_order_id = order_id
    sub.save()

    try:
        tx = epoint.cards.charge(sub.card_id, sub.plan.price, order_id,
                                 description=f"{sub.plan.name}, {period}")
    except NotSentError:
        return
    except OutcomeUnknownError:
        sub.state = "needs_check"
        sub.save()
        return
    except GatewayError as exc:
        record_failure(sub, str(exc))
        return

    if tx.paid:
        sub.paid_until = add_month(sub.paid_until)
        sub.failures = 0
        sub.save()
    elif tx.failed:
        record_failure(sub, tx.message or tx.code or "declined")
```

Why the order id looks like this:

- It contains the period and the attempt number, for example `SUB-12-202603-1`. If the job runs twice before anything changes, the second run sends the **same** id. Epoint refuses it, so the customer is never charged twice for one attempt.
- `NotSentError` means nothing reached Epoint, so the next run simply tries again with the same id.
- `OutcomeUnknownError` stops automatic billing for this subscription until someone, or the reconciliation job, checks what happened.

## Part 3. Failures and retries

```python
MAX_FAILURES = 3

def record_failure(sub, reason):
    sub.failures += 1
    sub.last_failure = reason
    if sub.failures >= MAX_FAILURES:
        sub.state = "paused"
        notify_user_card_problem(sub.user)
    sub.save()
```

After a declined charge `failures` goes up, so the next run builds a new id, `SUB-12-202603-2`. Each real new attempt gets its own id, while a repeated run of the same attempt does not.

## Letting users change the card

Start a fresh `cards.register()` flow, and when its callback arrives with `operation_code == OperationCode.CARD_REGISTRATION`, replace `sub.card_id` and reset `failures`.

## Cancelling

Stop charging at once and keep the card id only as long as you need it for refunds.
