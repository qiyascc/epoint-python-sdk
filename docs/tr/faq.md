# SSS ve sorun giderme

## İstemci açılırken "Epoint public_key and private_key are required" hatası veriyor

Anahtarlar istemciye ulaşmamış. `EPOINT_PUBLIC_KEY` ve `EPOINT_PRIVATE_KEY` değişkenlerinin yalnızca kendi terminalinizde değil, uygulamayı çalıştıran sürecin ortamında da tanımlı olduğunu kontrol edin. Yapılandırma dosyası kullanıyorsanız dosyanın çalışma klasöründe olduğundan veya `EPOINT_CONFIG` ile belirtildiğinden emin olun.

## "Refusing to send signed requests over plain http"

`base_url` `http://` ile başlıyor ve localhost dışında bir adresi gösteriyor. `https` kullanın. İç ağdaki bir sandbox için `allow_insecure_http=True` ayarını yalnızca orada kullanın.

## Tüm callback'ler SignatureError ile başarısız oluyor

- Sunucudaki gizli anahtar, Epoint'in üye işyeriniz için kullandığı anahtar değil. Fazladan boşlukları veya başka bir ortamdan alınmış bir anahtarı kontrol edin.
- Epoint ile uygulamanız arasındaki bir şey gövdeyi değiştiriyor: formları yeniden yazan bir proxy veya gövdeyi view'dan önce okuyan bir çatı. Orijinal `data` ve `signature` değerlerini verin.
- Başka bir anahtarla imzalanmış bir callback ile test ediyorsunuz, örneğin canlı yapılandırmaya karşı sandbox anahtarıyla.

## İkinci ödeme denemesinde GatewayError

Epoint daha önce gördüğü bir `order_id` değerini reddeder. Yeni deneme için yeni bir kimlik kullanın, örneğin sipariş numarası artı bir deneme sayacı. Bkz. [Ödemeler](guides/payments.md#sipariş-kimlikleri).

## Apple Pay, taksit, cüzdan veya B2B transferlerde GatewayError

Bu özellikleri Epoint her üye işyeri için ayrıca açar. Hesabınız için açmalarını Epoint'ten isteyin.

## Müşteri başarılı ödeme sayfasına döndü ama sipariş hâlâ beklemede

Callback henüz gelmedi veya başarısız oldu. "Doğruluyoruz" mesajı gösterin, kendi backend'inizi belirli aralıklarla sorgulayın ve gerekirse sunucuda `payments.status()` çağırın. Bkz. [Callback'ler](guides/callbacks.md#başarılı-ödeme-sayfası-bir-onay-değildir).

## OutcomeUnknownError aldım. Müşteriden para çekildi mi?

Olabilir. İstek Epoint'e ulaştı ama net bir yanıt gelmedi. Yeni bir sipariş kimliğiyle yeniden göndermeyin. Durumu kontrol edin, callback'i bekleyin veya aynı sipariş kimliğiyle tekrar deneyin. Bkz. [Güvenilirlik](guides/reliability.md#outcomeunknownerror-ile-başa-çıkmak).

## Normal görünen bir tutar için InvalidRequestError

Tutarlar en fazla iki ondalık basamak içerebilir. `0.1 + 0.2` gibi bir float `0.30000000000000004` olur ve reddedilir. Para için string veya `Decimal` kullanın.

## SDK'yı birden fazla thread'den kullanabilir miyim?

Evet. Senkron istemci thread güvenli olan `httpx.Client` kullanır. Tek bir istemci oluşturun ve paylaşın.

## Django'nun asenkron view'larıyla çalışır mı?

Asenkron view'larda `AsyncEpoint`, senkron view'larda `Epoint` kullanın. Senkron istemciyi asenkron bir view'dan çağırmayın, olay döngüsünü bloklar.

## Ne gönderildiğini nasıl görürüm?

httpx loglarını açın:

```python
import logging

logging.basicConfig(level=logging.WARNING)
logging.getLogger("httpx").setLevel(logging.INFO)
```

Bu, her isteğin metodunu, URL'sini ve durumunu loglar. İmzalı gövde loglanmaz.

## Bir hatayı nereye bildiririm?

[github.com/qiyascc/epoint-python-sdk/issues](https://github.com/qiyascc/epoint-python-sdk/issues) adresinde bir issue açın. SDK sürümünü, çağırdığınız metodu ve varsa `trace_id` değerini yazın. Gizli anahtarınızı asla eklemeyin.
