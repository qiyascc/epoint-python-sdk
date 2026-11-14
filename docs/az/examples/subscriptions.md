# Yadda saxlanmış kartlarla abunəlik

Aylıq abunəlik üç hissədən ibarətdir: ilk ödəniş kartı yadda saxlayır, gündəlik tapşırıq ödəniş vaxtı çatmış abunəliklər üzrə ödəniş alır, uğursuz ödənişlər isə abunəlik dayandırılmazdan əvvəl bir neçə dəfə təkrarlanır.

## 1-ci hissə. İlk ödəniş kartı yadda saxlayır

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

Callback `tx.paid` ilə gələndə abunəlik aktiv olur və kart istifadəyə hazırdır:

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

## 2-ci hissə. Gündəlik ödəniş tapşırığı

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

Sifariş identifikatoru niyə belədir:

- İdentifikatorda dövr və cəhdin nömrəsi var, məsələn `SUB-12-202603-1`. Heç nə dəyişmədən tapşırıq iki dəfə işləsə, ikinci dəfə **eyni** identifikator göndərilir. Epoint onu rədd edir, ona görə müştəridən bir cəhd üçün heç vaxt iki dəfə pul çıxılmır.
- `NotSentError` Epoint-ə heç nəyin çatmadığını bildirir, ona görə tapşırıq növbəti dəfə işə düşəndə eyni identifikatorla sadəcə yenidən cəhd edir.
- `OutcomeUnknownError` bu abunəlik üçün avtomatik ödənişi kimsə və ya üzləşmə tapşırığı nə baş verdiyini yoxlayana qədər dayandırır.

## 3-cü hissə. Uğursuzluqlar və təkrar cəhdlər

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

Kart rədd ediləndən sonra `failures` artır, ona görə tapşırıq növbəti dəfə işə düşəndə yeni identifikator yaranır: `SUB-12-202603-2`. Hər həqiqi yeni cəhdin öz identifikatoru olur, eyni cəhd təkrar işə düşəndə isə identifikator dəyişmir.

## İstifadəçiyə kartı dəyişməyə imkan vermək

Yeni `cards.register()` axınına başlayın. Onun callback-i `operation_code == OperationCode.CARD_REGISTRATION` ilə gələndə `sub.card_id` dəyərini əvəz edin və `failures` sayğacını sıfırlayın.

## Abunəliyi ləğv etmək

Kartdan pul çıxmağı dərhal dayandırın və kart identifikatorunu yalnız geri qaytarmalar üçün lazım olduğu müddətdə saxlayın.
