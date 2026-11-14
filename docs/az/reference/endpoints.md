# Endpoint-lər və xam sorğular

Hər API yolu ayrıca ayar kimi saxlanılır, ona görə Epoint tərəfindəki dəyişikliyə SDK-nın yeni versiyasını gözləmədən uyğunlaşa bilərsiniz.

## Standart yollar

| Ad | Standart yol | İstifadə edən |
| --- | --- | --- |
| `payment` | `/api/1/request` | `payments.create` |
| `checkout` | `/api/1/checkout` | `payments.form` (formanın `action` ünvanı) |
| `status` | `/api/1/get-status` | `payments.status` |
| `reverse` | `/api/1/reverse` | `payments.reverse` |
| `hold` | `/api/1/pre-auth-request` | `payments.hold` |
| `capture` | `/api/1/pre-auth-complete` | `payments.capture` |
| `card_register` | `/api/1/card-registration` | `cards.register` |
| `card_register_pay` | `/api/1/card-registration-with-pay` | `cards.register_and_pay` |
| `card_charge` | `/api/1/execute-pay` | `cards.charge` |
| `card_status` | `/api/1/get-status-card` | `cards.status` |
| `payout` | `/api/1/refund-request` | `cards.payout` |
| `split_payment` | `/api/1/split-request` | `split.create` |
| `split_charge` | `/api/1/split-execute-pay` | `split.charge` |
| `split_register_pay` | `/api/1/split-card-registration-with-pay` | `split.register_and_pay` |
| `installment_plans` | `/api/1/get-installment-request` | `installments.plans` |
| `installment_payment` | `/api/1/installment-request` | `installments.create` |
| `wallets` | `/api/1/wallet/status` | `wallets.list` |
| `wallet_payment` | `/api/1/wallet/payment` | `wallets.pay` |
| `widget` | `/api/1/token/widget` | `widgets.create` |
| `widget_split` | `/api/1/token/split-payment` | `widgets.split` |
| `invoice_create` | `/api/1/invoices/create` | `invoices.create` |
| `invoice_update` | `/api/1/invoices/update` | `invoices.update` |
| `invoice_view` | `/api/1/invoices/view` | `invoices.get` |
| `invoice_list` | `/api/1/invoices/list` | `invoices.list` |
| `invoice_sms` | `/api/1/invoices/send-sms` | `invoices.send_sms` |
| `invoice_email` | `/api/1/invoices/send-email` | `invoices.send_email` |
| `b2b_transfer` | `/api/1/b2b/payment` | `transfers.create` |
| `b2b_status` | `/api/1/b2b/payment/{order_id}` | `transfers.status` |
| `heartbeat` | `/api/heartbeat` | `heartbeat` |

Yollar `base_url` ünvanına nisbətəndir. Fiqurlu mötərizədəki dəyərlər hər çağırışda doldurulur və URL üçün kodlanır.

## Yolu dəyişmək

Kodda:

```python
ep = Epoint(endpoints={"payment": "/api/2/request"})
```

Yalnız göstərdiyiniz yollar dəyişir. Qalanları standart dəyərində qalır.

Konfiqurasiya faylında:

```toml
[endpoints]
payment = "/api/2/request"
```

Mühit dəyişənində, hissələr arasında iki alt xətlə:

```console
$ export EPOINT_ENDPOINTS__PAYMENT=/api/2/request
```

## SDK-da olmayan endpoint-i çağırmaq

`request()` istənilən məlumatı imzalayır və istənilən endpoint-ə göndərir. Ona cədvəldəki endpoint adını və ya `/` ilə başlayan yolu verin:

```python
answer = ep.request("/api/1/some-new-call", {"order_id": "A-1", "amount": 10})
```

Cavab heç bir emal olmadan açılmış JSON-dur. Xətalar digər çağırışlardakı kimi idarə olunur: `status: error` `GatewayError`, HTTP xətaları isə `HTTPStatusError` qaldırır.

Standart olaraq `request()` pul hərəkət etdirən çağırış sayılır və nəticəsi bəlli olmayan xətadan sonra heç vaxt təkrarlanmır. Yalnız oxuyan çağırış üçün təkrar cəhdlərə icazə vermək məqsədilə `safe=True` verin:

```python
ep.request("/api/1/some-report", {"date": "2026-03-01"}, safe=True)
```

Sizin `public_key` dəyəriniz məlumata əlavə olunur, boş dəyərlər (`None` və ya `""`) isə imzalamadan əvvəl çıxarılır.
