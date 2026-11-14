# Taksit

Taksitte müşteri, bunu destekleyen bir banka kartıyla aylık parçalar halinde öder, siz ise ödemeyi her zamanki gibi alırsınız. Taksit özelliğinin üye işyeri hesabınız için açılmış olması gerekir.

Taksiti iki şekilde sunabilirsiniz.

## Müşteri Epoint sayfasında seçer

Normal bir ödemeye `installment=True` ekleyin:

```python
ep.payments.create("1200.00", "ORDER-6001", description="Dizüstü bilgisayar", installment=True)
```

Epoint uygun planları kendi sayfasında gösterir.

## Planları kendi sayfanızda göstermek

### 1. adım. Planları yükleyin

```python
plans = ep.installments.plans("ORDER-6002", "1200.00")
for plan in plans:
    print(plan.card_id, plan.name, plan.months)
```

`plans()` sipariş kimliğinizi ve isteğe bağlı olarak tutarı, ayrıca anahtar kelimeli `language` ve `currency` argümanlarını alır. Bir {py:class}`~epoint_sdk.InstallmentPlan` listesi döndürür:

| Alan | Anlamı |
| --- | --- |
| `card_id` | Taksit kartı programı, ödeme yaparken geri gönderilir |
| `name` | Görünen adı |
| `months` | Desteklediği ay sayıları, tam sayılardan oluşan bir tuple olarak |

Planları yüklemek tekrarlanması güvenli bir işlemdir, bu yüzden SDK onu ağ hatalarında yeniden dener.

### 2. adım. Planları gösterin

```html
{% for plan in plans %}
  <fieldset>
    <legend>{{ plan.name }}</legend>
    {% for m in plan.months %}
      <label>
        <input type="radio" name="plan" value="{{ plan.card_id }}:{{ m }}">
        {{ m }} ay
      </label>
    {% endfor %}
  </fieldset>
{% endfor %}
```

### 3. adım. Seçilen planla ödeyin

```python
card_id, months = request.POST["plan"].split(":")
checkout = ep.installments.create(
    "1200.00",
    "ORDER-6002",
    card_id,
    int(months),
    description="Dizüstü bilgisayar",
)
redirect(checkout.redirect_url)
```

`months` pozitif bir tam sayı olmalıdır, aksi halde `InvalidRequestError` fırlatılır. Diğer anahtar kelimeli argümanlar `payments.create()` ile aynıdır. Yanıt bir `Redirect` olur ve sonuç her zamanki callback ile gelir.

Müşterinin gönderdiği plan ve ay sayısının gerçekten `plans()` yanıtında olduğunu her zaman sunucuda kontrol edin. Form değerleri tarayıcıda değiştirilebilir.
