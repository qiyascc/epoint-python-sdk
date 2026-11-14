# Yapılandırma

Ayarlar [goodconf](https://github.com/lincolnloop/goodconf) ile yüklenir. Bunları kodda verebilir, ortam değişkenlerine yazabilir, bir dosyada tutabilir veya üçünü birlikte kullanabilirsiniz.

## Öncelik sırası

Aynı ayar birden fazla yerden geldiğinde listede üstte olan kazanır:

1. `Epoint(...)` veya `AsyncEpoint(...)` çağrısına verilen argümanlar.
2. `EPOINT_` ile başlayan ortam değişkenleri.
3. Yapılandırma dosyası.
4. Yerleşik varsayılan değer.

## Kodda

```python
from epoint_sdk import Epoint

ep = Epoint(
    "i000000001",
    "PRIVATE_KEY",
    success_url="https://shop.az/payment/ok",
    error_url="https://shop.az/payment/fail",
    language="en",
    timeout=20,
)
```

Aşağıdaki tablodaki her ayar anahtar kelimeli argüman olarak verilebilir.

## Ortam değişkenleri

Her ayarın, `EPOINT_` önekine ayar adının büyük harfli halinin eklenmesiyle oluşan bir değişkeni vardır:

```console
$ export EPOINT_PUBLIC_KEY=i000000001
$ export EPOINT_PRIVATE_KEY=your-private-key
$ export EPOINT_SUCCESS_URL=https://shop.az/payment/ok
$ export EPOINT_ERROR_URL=https://shop.az/payment/fail
$ export EPOINT_LANGUAGE=az
$ export EPOINT_TIMEOUT=30
$ export EPOINT_MAX_RETRIES=2
```

Windows CMD'de `export` yerine `set AD=değer` yazın.

Değişkenler tanımlıysa istemcinin argümana ihtiyacı yoktur:

```python
ep = Epoint()
```

## Yapılandırma dosyası

Argüman verilmediğinde istemci çalışma klasöründe sırasıyla `epoint.toml`, `epoint.yaml`, `epoint.yml` veya `epoint.json` dosyasını da arar:

```toml
public_key = "i000000001"
private_key = "your-private-key"
success_url = "https://shop.az/payment/ok"
error_url = "https://shop.az/payment/fail"
language = "az"
timeout = 30
```

Dosyayı başka bir yerden okumak için ya `EPOINT_CONFIG` değişkeninde yolunu belirtin ya da `config_file` argümanını verin:

```console
$ export EPOINT_CONFIG=/etc/myshop/epoint.toml
```

```python
ep = Epoint(config_file="/etc/myshop/epoint.toml")
```

YAML için `yaml` eki, Python 3.10'da TOML için ise `toml` eki gerekir. Bkz. [Kurulum](installation.md#ek-paketler).

```{warning}
Gizli anahtarı içeren bir yapılandırma dosyası deponuza girmemelidir. Dosyayı `.gitignore`'a ekleyin veya dosyada yalnızca gizli olmayan ayarları tutup anahtarları ortam değişkenlerine taşıyın.
```

## Tüm ayarlar

| Ayar | Ortam değişkeni | Varsayılan | Anlamı |
| --- | --- | --- | --- |
| `public_key` | `EPOINT_PUBLIC_KEY` | (boş) | Üye işyerinin açık anahtarı, örneğin `i000000001`. Zorunlu |
| `private_key` | `EPOINT_PRIVATE_KEY` | (boş) | Üye işyerinin gizli anahtarı. İstekleri imzalar ve callback'leri doğrular. Zorunlu |
| `base_url` | `EPOINT_BASE_URL` | `https://epoint.az` | Ödeme altyapısının adresi. Test sırasında bir sandbox'a yönlendirin |
| `endpoints.*` | `EPOINT_ENDPOINTS__<AD>` | bkz. [Uç noktalar](reference/endpoints.md) | Her API çağrısının `base_url`'e göre yolu |
| `language` | `EPOINT_LANGUAGE` | `az` | Ödeme sayfasının dili: `az`, `en` veya `ru` |
| `currency` | `EPOINT_CURRENCY` | `AZN` | Varsayılan para birimi: `AZN`, `USD`, `EUR` veya `RUB` |
| `success_url` | `EPOINT_SUCCESS_URL` | yok | Müşterinin başarılı ödemeden sonra döndüğü sayfa |
| `error_url` | `EPOINT_ERROR_URL` | yok | Müşterinin başarısız ödemeden sonra döndüğü sayfa |
| `timeout` | `EPOINT_TIMEOUT` | `30` | Yanıt için bekleme süresi, saniye. Sıfırdan büyük olmalı |
| `connect_timeout` | `EPOINT_CONNECT_TIMEOUT` | `10` | Bağlantı için bekleme süresi, saniye. Sıfırdan büyük olmalı |
| `max_retries` | `EPOINT_MAX_RETRIES` | `2` | Tekrarlanması güvenli çağrılar için ek deneme sayısı. 0 ile 10 arası |
| `backoff_base` | `EPOINT_BACKOFF_BASE` | `0.5` | Denemeler arasındaki ilk bekleme, saniye |
| `backoff_cap` | `EPOINT_BACKOFF_CAP` | `8` | Denemeler arasındaki en uzun bekleme, saniye |
| `user_agent` | `EPOINT_USER_AGENT` | `epoint-python-sdk/{version}` | `User-Agent` başlığı. `{version}` SDK sürümüyle değiştirilir |
| `allow_insecure_http` | `EPOINT_ALLOW_INSECURE_HTTP` | `False` | localhost dışında düz `http` adresine izin verir. Yalnızca iç ağdaki bir sandbox için |

Yeniden denemeler ve zaman aşımları [Güvenilirlik](guides/reliability.md) sayfasında ayrıntılı anlatılıyor.

Değerler istemci oluşturulurken doğrulanır. Bilinmeyen bir dil, küçük harfle yazılmış bir para birimi (`USD` yerine `usd`), sıfır zaman aşımı veya 10'dan büyük bir `max_retries` pydantic'in `ValidationError` hatasını fırlatır. Böylece ortam değişkenindeki bir yazım hatası uygulamayı açılışta durdurur.

## Tek bir çağrıda değiştirilebilen varsayılanlar

`language`, `currency`, `success_url` ve `error_url` varsayılan değerlerdir. Ödeme metotlarının çoğu aynı adlı anahtar kelimeli argümanları kabul eder ve çağrıya verilen değer önceliklidir:

```python
ep.payments.create("10", "ORDER-7", language="en", currency="USD",
                   success_url="https://shop.az/en/thanks")
```

## Ayarları kendiniz oluşturmak

`load_settings` ortam değişkenlerini ve dosyaları istemciyle aynı şekilde okur ve inceleyip tekrar kullanabileceğiniz bir `Settings` nesnesi döndürür:

```python
from epoint_sdk import Epoint, load_settings

settings = load_settings("/etc/myshop/epoint.toml", timeout=15)
print(settings.base_url, settings.timeout)

ep = Epoint(settings=settings)
```

Hem `settings` hem de anahtar kelimeli argümanlar verilirse argümanlar ayarların üzerine uygulanır:

```python
staging = Epoint(settings=settings, base_url="http://localhost:8181")
```

## Düz http reddedilir

İmzalı istekler yalnızca `https` üzerinden gönderilir. `http://` ile başlayan bir `base_url` istemci oluşturulurken `ConfigurationError` fırlatır. İki istisna vardır:

- `localhost`, `127.0.0.1` ve `::1` her zaman izinlidir, böylece kendi bilgisayarınızdaki sandbox çalışır.
- `allow_insecure_http=True` her sunucuya izin verir. Yalnızca iç ağdaki bir sandbox için kullanın.

## Kendi HTTP istemciniz

Proxy, özel sertifikalar veya testlerde sahte bir transport kullanmak için bir `httpx.Client` (`AsyncEpoint` için `httpx.AsyncClient`) verin:

```python
import httpx
from epoint_sdk import Epoint

http = httpx.Client(proxy="http://proxy.internal:3128", timeout=20)
ep = Epoint(http_client=http)
```

Kendi istemcinizi verdiğinizde `timeout` ve `connect_timeout` yerine onun zaman aşımı ayarları geçerli olur ve onu kapatmak size kalır. `ep.close()` yalnızca SDK'nın kendi oluşturduğu istemciyi kapatır.
