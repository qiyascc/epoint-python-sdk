# Elektron pul kisələri

Epoint əməkdaşlıq etdiyi elektron pul kisələri vasitəsilə ödəniş qəbul edə bilir. Pul kisəsi ilə ödəniş tacir hesabınız üçün aktivləşdirilmiş olmalıdır.

## Pul kisələrinin siyahısı

```python
for wallet in ep.wallets.list():
    print(wallet.id, wallet.name)
```

Hər element `id` və `name` sahələri olan {py:class}`~epoint_sdk.Wallet` obyektidir. Siyahını təkrar-təkrar yükləmək təhlükəsizdir, ona görə onu bir neçə dəqiqəlik keşdə saxlayıb ödəniş səhifənizdə göstərə bilərsiniz.

## Pul kisəsi ilə ödəniş

```python
checkout = ep.wallets.pay(wallet_id, "25.00", "ORDER-7001", description="Hədiyyə kartı")
redirect(checkout.redirect_url)
```

Arqumentlər pul kisəsinin identifikatoru, məbləğ və sifariş identifikatorudur. Bunlardan əlavə açar sözlü `description`, `language` və `currency` var. Cavab `Redirect` olur: müştərini `redirect_url` ünvanına göndərin və kartla ödənişdə olduğu kimi callback-i gözləyin.
