# Dijital cüzdanlar

Epoint, birlikte çalıştığı dijital cüzdanlar üzerinden ödeme alabilir. Cüzdanla ödemenin üye işyeri hesabınız için açılmış olması gerekir.

## Cüzdanları listelemek

```python
for wallet in ep.wallets.list():
    print(wallet.id, wallet.name)
```

Her öğe `id` ve `name` alanlarına sahip bir {py:class}`~epoint_sdk.Wallet` nesnesidir. Listeyi tekrar tekrar yüklemek güvenlidir, bu yüzden birkaç dakika önbellekte tutup ödeme sayfanızda gösterebilirsiniz.

## Cüzdanla ödeme

```python
checkout = ep.wallets.pay(wallet_id, "25.00", "ORDER-7001", description="Hediye kartı")
redirect(checkout.redirect_url)
```

Argümanlar cüzdan kimliği, tutar ve sipariş kimliğinizdir. Ayrıca anahtar kelimeli `description`, `language` ve `currency` vardır. Yanıt bir `Redirect` olur: müşteriyi `redirect_url` adresine gönderin ve kartlı ödemede olduğu gibi callback'i bekleyin.
