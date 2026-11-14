# Bölünmüş ödeme

Bölünmüş ödeme, müşteriden tek bir ödeme alır ve bir kısmını başka bir Epoint üye işyerine, yani iş ortağına verir. Pazaryerleri bunu satıcılara ödeme yapmak, platformlar ise geliri bayilerle paylaşmak için kullanır.

Her bölünmüş ödeme çağrısı iki ek değer alır:

`partner`
: İş ortağının Epoint açık anahtarı, örneğin `i000000002`. `split_user` adıyla gönderilir.

`partner_amount`
: İş ortağının payı. Geçerli bir tutar olmalı ve toplamdan büyük olmamalıdır. Daha büyük bir pay, hiçbir şey gönderilmeden `InvalidRequestError` fırlatır.

## Ödeme sayfasında

```python
checkout = ep.split.create(
    "100.00",
    "ORDER-5001",
    "i000000002",
    "85.00",
    description="Nur Stüdyo'dan el yapımı lamba",
)
redirect(checkout.redirect_url)
```

İlk dört argüman toplam tutar, sipariş kimliğiniz, iş ortağı ve iş ortağının payıdır. Anahtar kelimeli argümanlar `installment` dışında `payments.create()` ile aynıdır. Yanıt bir `Redirect` olur.

## Kayıtlı kartla

```python
tx = ep.split.charge(card_id, "100.00", "ORDER-5002", "i000000002", "85.00")
```

`cards.charge()` gibi hemen çekim yapar ve bir `Transaction` döndürür. Kart reddedildiğinde `failed` özelliği `True` olan bir işlem döner.

## Bölünmüş ödemeyle kart kaydetmek

```python
reg = ep.split.register_and_pay("100.00", "ORDER-5003", "i000000002", "85.00")
redirect(reg.redirect_url)
```

Yanıt bir `CardRegistration` olur.

## Callback'te

Bölünmüş ödemenin callback'i iş ortağının payını `split_amount` alanında taşır:

```python
tx = ep.verify_callback(request.POST)
if tx.paid:
    record_sale(tx.order_id, total=tx.amount, partner_share=tx.split_amount)
```

## Apple Pay ve Google Pay

Widget'ın da bölünmüş bir çeşidi var: `ep.widgets.split(...)`. Bkz. [Apple Pay ve Google Pay](apple-google-pay.md#widgetta-bölünmüş-ödeme).
