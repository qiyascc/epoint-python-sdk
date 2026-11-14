# Güvenlik

Ödeme entegrasyonlarına yönelik saldırılar genellikle birkaç bilinen noktayı hedefler. Bu sayfa bu noktaları, SDK'nın her biri için ne yaptığını ve size ne kaldığını listeler.

## 1. Yalnızca imzalı callback'e güvenin

`success_url` sayfanıza yapılan yönlendirme hiçbir şey kanıtlamaz. O adresi herkes tarayıcıya yazabilir. Siparişi yalnızca şunlardan biri olduktan sonra ödendi olarak işaretleyin:

- `verify_callback` kontrolünden geçmiş bir callback veya
- sunucunuzun yaptığı bir `payments.status()` çağrısı.

## 2. Callback'in bu siparişe ait olduğunu kontrol edin

Geçerli bir imza, callback'i Epoint'in gönderdiğini gösterir. Açmak üzere olduğunuz siparişe ait olduğunu göstermez. Bir saldırgan ucuz bir sipariş için 1 AZN ödeyip aynı callback'i pahalı bir sipariş için tekrar göndermeyi deneyebilir. Kayıtlarınızla karşılaştırın:

```python
if tx.paid and tx.matches(order_id=order.number, amount=order.total, transaction=order.epoint_transaction):
    order.mark_paid()
```

## 3. Gizli anahtarı sunucuda tutun

- Asla bir tarayıcıya veya mobil uygulamaya göndermeyin. İmzalama yalnızca sunucuda yapılır.
- Deponuzdan ve loglardan uzak tutun. SDK anahtarı `SecretStr` olarak saklar, bu yüzden ayarlar yazdırıldığında `**********` görünür ve `repr(ep)` yalnızca açık anahtarı gösterir.
- Anahtarı ortamdan veya bir gizli bilgi yöneticisinden yükleyin.
- Sızmış olabileceğinden şüpheleniyorsanız hemen Epoint'ten yeni bir anahtar çifti isteyin.

## 4. Yalnızca https

İmzalı istekler düz `http` üzerinden gönderilmez. İstisnalar localhost ve özel bir sandbox için açıkça ayarladığınız `allow_insecure_http` seçeneğidir. Bu seçeneği canlı ortamda asla açmayın.

## 5. Göndermeden önce doğrulayın

Tutarlar sunucunuzdan herhangi bir istek çıkmadan önce kontrol edilir: gizli yuvarlama içeren float'lar, `NaN`, negatif değerler ve `1` gibi görünen bool'lar geçemez. Sipariş kimliklerinin ve metinlerin uzunluk sınırları vardır. Bu hatalar müşteriye değil geliştiriciye görünmelidir.

## 6. Callback adresini kötüye kullanıma karşı koruyun

- SDK, 64 KB'den büyük callback verisini ve 128 karakterden uzun imzaları hash hesaplamadan reddeder.
- İmzalar `hmac.compare_digest` ile karşılaştırılır, böylece yanıt süresi saldırgana bir şey söylemez.
- Geçersiz callback'lere HTTP 400 ile yanıt verin ve başka hiçbir iş yapmayın.
- Adres internete açıksa proxy düzeyinde istek sınırı koyun.

## 7. Tarayıcı mesajlarını ipucu olarak görün

Apple Pay ve Google Pay widget'ı sonucunu `postMessage` ile bildirir. `event.origin` değerini `widget.origin` ile kontrol edin ve o zaman bile mesajı yalnızca kendi sunucunuzdan ödemeyi kontrol etmesini istemek için kullanın. `WidgetMessage.looks_paid` adı bunu hatırlatmak için seçildi.

## 8. Asla çift çekim yapmayın

Para hareketi yaratan çağrılar, sonucu belirsiz bir hatadan sonra yeniden denenmez. Kendi kodunuzda da böyle kalsın: `OutcomeUnknownError` aldığınızda önce kontrol edin ve yalnızca aynı sipariş kimliğiyle tekrar deneyin. Bkz. [Güvenilirlik](reliability.md).

## 9. Dikkatli loglayın

`order_id`, `transaction`, `trace_id`, durum ve tutarları loglayın. Gizli anahtarı, canlı ortamda callback gövdelerinin tamamını ve müşterinin yazdığı hiçbir şeyi loglamayın. Epoint desteği sizden `trace_id` değerini isteyecektir.

## Canlıya çıkmadan önce kontrol listesi

- [ ] `base_url` `https://epoint.az` ve `allow_insecure_http` ayarlanmamış.
- [ ] Gizli anahtar ortam değişkeninden veya bir gizli bilgi yöneticisinden geliyor.
- [ ] Callback view'ı imzayı doğruluyor ve `matches()` çağırıyor.
- [ ] Siparişler yalnızca callback'te veya bir `payments.status()` çağrısından sonra ödendi olarak işaretleniyor.
- [ ] Callback handler'ı idempotent.
- [ ] `OutcomeUnknownError` yeni bir sipariş kimliğine değil, bir durum kontrolüne yol açıyor.
- [ ] Uzun süre beklemede kalan siparişleri kontrol eden bir görev var.
- [ ] Widget sayfası `Permissions-Policy: payment=(self "https://epoint.az")` başlığını gönderiyor.
