# Kayıtlı kartlarla abonelik

Üç parçadan oluşan aylık bir abonelik: ilk ödeme kartı kaydeder, günlük bir görev vadesi gelen abonelikleri tahsil eder ve başarısız çekimler abonelik durdurulmadan önce birkaç kez yeniden denenir.

## 1. bölüm. İlk ödeme kartı kaydeder

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

Callback `tx.paid` ile geldiğinde abonelik etkinleşir ve kart kullanıma hazırdır:

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

## 2. bölüm. Günlük tahsilat görevi

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

Sipariş kimliği neden böyle:

- Kimlik dönemi ve deneme numarasını içerir, örneğin `SUB-12-202603-1`. Hiçbir şey değişmeden görev iki kez çalışırsa ikinci çalıştırma **aynı** kimliği gönderir. Epoint bunu reddeder, bu yüzden müşteriden bir deneme için asla iki kez çekim yapılmaz.
- `NotSentError`, Epoint'e hiçbir şeyin ulaşmadığı anlamına gelir, bu yüzden görev bir sonraki çalışmasında aynı kimlikle yeniden dener.
- `OutcomeUnknownError`, biri veya mutabakat görevi ne olduğunu kontrol edene kadar bu abonelik için otomatik tahsilatı durdurur.

## 3. bölüm. Başarısız çekimler ve yeniden denemeler

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

Reddedilen bir çekimden sonra `failures` artar, bu yüzden görev bir sonraki çalışmasında yeni bir kimlik üretir: `SUB-12-202603-2`. Her gerçek yeni denemenin kendi kimliği olur, aynı denemenin tekrar çalışmasında ise kimlik değişmez.

## Kullanıcının kartı değiştirmesine izin vermek

Yeni bir `cards.register()` akışı başlatın. Bu akışın callback'i `operation_code == OperationCode.CARD_REGISTRATION` ile geldiğinde `sub.card_id` değerini değiştirin ve `failures` sayacını sıfırlayın.

## Aboneliği iptal etmek

Çekim yapmayı hemen durdurun ve kart kimliğini yalnızca iadeler için gerektiği sürece saklayın.
