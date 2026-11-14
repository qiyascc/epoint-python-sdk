# Güvenilirlik

Ağlar birbirinden çok farklı iki şekilde arızalanır ve bir ödeme istemcisinin bunları ayırt etmesi gerekir:

- **Hiçbir şey gönderilmedi.** Bağlantı reddedildi veya hiç açılmadı. Tekrar denemek zararsızdır.
- **Bir şey gönderildi ama net bir yanıt gelmedi.** İstek sunucunuzdan çıktıktan sonra zaman aşımı oldu, bağlantı koptu veya 5xx hatası geldi. Epoint karttan çekimi yapmış olabilir. Aynı isteği tekrar gönderirseniz para iki kez çekilebilir.

SDK her çağrıyı iki gruptan birine koyar ve farklı kurallar uygular.

## İki tür çağrı

Para hareketi yaratan çağrılar
: `payments.create`, `payments.reverse`, `payments.hold`, `payments.capture`, `cards.register`, `cards.register_and_pay`, `cards.charge`, `cards.payout`, tüm `split` çağrıları, `installments.create`, `wallets.pay`, tüm `widgets` çağrıları, `invoices.create`, `invoices.update`, `invoices.send_sms`, `invoices.send_email`, `transfers.create` ve `safe=True` verilmediği sürece `request()`.

Yalnızca okuma yapan çağrılar
: `payments.status`, `cards.status`, `installments.plans`, `wallets.list`, `invoices.get`, `invoices.list`, `transfers.status` ve `heartbeat`.

## Her arızada ne olur

| Arıza | Para hareketi yaratan çağrılar | Yalnızca okuma yapan çağrılar |
| --- | --- | --- |
| Bağlantı reddedildi, bağlantı veya havuz zaman aşımı | Yeniden denenir, sonra `NotSentError` | Yeniden denenir, sonra `NotSentError` |
| Yanıt beklerken zaman aşımı, gönderimden sonra kopan bağlantı | **Yeniden denenmez**, `OutcomeUnknownError` | Yeniden denenir, sonra `TransportError` |
| HTTP 429 | Yeniden denenir, sonra `HTTPStatusError` | Yeniden denenir, sonra `HTTPStatusError` |
| HTTP 500, 502, 503, 504 | **Yeniden denenmez**, `OutcomeUnknownError` | Yeniden denenir, sonra `HTTPStatusError` |
| Diğer 5xx | `OutcomeUnknownError` | `HTTPStatusError` |
| JSON olmayan gövdeli 2xx | `OutcomeUnknownError` | `HTTPStatusError` |
| Diğer 4xx | `HTTPStatusError` | `HTTPStatusError` |
| `status: error` içeren JSON | `GatewayError` | `GatewayError` |

HTTP 429, Epoint'in isteği işlemediği anlamına gelir, bu yüzden ödemelerde de yeniden denenir.

## SDK ne kadar bekler

`max_retries` (varsayılan 2) ek deneme sayısıdır. SDK `n` numaralı denemeden (0'dan sayılır) önce

```text
min(backoff_cap, backoff_base * 2 ** n) + random(0, backoff_base / 2)
```

saniye bekler. Varsayılanlarla bu önce yaklaşık 0.5, sonra 1 saniyedir. Rastgele kısım, çok sayıda worker'ın aynı anda yeniden denemesini önler.

Her deneme bağlantı için en fazla `connect_timeout` (varsayılan 10), her okuma ve yazma için en fazla `timeout` (varsayılan 30) saniye bekler.

```python
ep = Epoint(timeout=15, connect_timeout=5, max_retries=3, backoff_base=0.3, backoff_cap=4)
```

`max_retries=0` yeniden denemeleri tamamen kapatır.

## OutcomeUnknownError ile başa çıkmak

İstisna `order_id` değerini taşır. Yeni bir sipariş kimliği üretmeyin ve isteği yeniden göndermeyin. Önce ne olduğunu öğrenin:

```python
from epoint_sdk import OutcomeUnknownError

try:
    tx = ep.cards.charge(card_id, "9.90", "SUB-1001-3")
except OutcomeUnknownError as exc:
    queue_check(exc.order_id)
```

Daha sonra bir görev ödemeyi kontrol eder. Ödeme sayfası üzerinden geçen ödemelerde `transaction` kimliği elinizdedir ve `payments.status()` çağırabilirsiniz. Doğrudan kart çekimlerinde callback'i bekleyin veya **aynı sipariş kimliğiyle** tekrar deneyin: Epoint daha önce kabul ettiği bir kimliği reddeder, bu yüzden ikinci bir çekim olamaz. Bu denemede gelen `GatewayError`, ilk denemenin Epoint'e ulaştığını gösterir. Nasıl sonuçlandığını ise callback söyler.

## Kendiniz güvenle yeniden denemek

1. İlk çağrıdan önce sipariş kimliğini kaydedin.
2. `NotSentError` aldığınızda aynı kimlikle istediğiniz zaman tekrar deneyin.
3. `OutcomeUnknownError` aldığınızda önce kontrol edin. Yalnızca aynı kimlikle tekrar deneyin.
4. Bir hatayı "aşmak" için asla yeni bir sipariş kimliği üretmeyin. Çift çekimler tam olarak böyle olur.

## İstek boyutu sınırları

- Metin alanları göndermeden önce kontrol edilir: `order_id` en fazla 255, `description` en fazla 1000, telefon numaraları en fazla 32, e-posta adresleri en fazla 254, IBAN en fazla 34 karakter.
- 64 KB'den büyük callback `data` değerleri ve 128 karakterden uzun imzalar hiçbir hash hesaplanmadan reddedilir. Böylece devasa bir sahte istek sunucunuzu meşgul edemez.
