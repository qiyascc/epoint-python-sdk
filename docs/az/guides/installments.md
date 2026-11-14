# Taksit

Taksitlə müştəri bunu dəstəkləyən bank kartı ilə hissə-hissə, aylıq ödəyir, siz isə ödənişi adi qaydada alırsınız. Taksit tacir hesabınız üçün aktivləşdirilmiş olmalıdır.

Taksiti iki yolla təklif etmək olar.

## Müştəri Epoint səhifəsində seçir

Adi ödənişə `installment=True` əlavə edin:

```python
ep.payments.create("1200.00", "ORDER-6001", description="Noutbuk", installment=True)
```

Epoint mövcud planları öz səhifəsində göstərir.

## Planları öz səhifənizdə göstərmək

### 1-ci addım. Planları yükləyin

```python
plans = ep.installments.plans("ORDER-6002", "1200.00")
for plan in plans:
    print(plan.card_id, plan.name, plan.months)
```

`plans()` sifariş identifikatorunu və istəyə görə məbləği, həmçinin açar sözlü `language` və `currency` arqumentlərini qəbul edir. O, {py:class}`~epoint_sdk.InstallmentPlan` siyahısı qaytarır:

| Sahə | Mənası |
| --- | --- |
| `card_id` | Taksit kartı proqramı, ödəniş zamanı geri göndərilir |
| `name` | Ekranda göstərilən adı |
| `months` | Dəstəklədiyi ay sayları, tam ədədlərdən ibarət kortej (tuple) şəklində |

Planları yükləmək təkrarlana bilən əməliyyatdır, ona görə SDK onu şəbəkə xətalarında yenidən göndərir.

### 2-ci addım. Planları göstərin

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

### 3-cü addım. Seçilmiş planla ödəyin

```python
card_id, months = request.POST["plan"].split(":")
checkout = ep.installments.create(
    "1200.00",
    "ORDER-6002",
    card_id,
    int(months),
    description="Noutbuk",
)
redirect(checkout.redirect_url)
```

`months` müsbət tam ədəd olmalıdır, əks halda `InvalidRequestError` qaldırılır. Digər açar sözlü arqumentlər `payments.create()` ilə eynidir. Cavab `Redirect` olur, nəticə isə adi callback ilə gəlir.

Müştərinin göndərdiyi plan və ay sayının həqiqətən `plans()` cavabında olduğunu həmişə serverdə yoxlayın. Forma dəyərlərini brauzerdə dəyişmək olur.
