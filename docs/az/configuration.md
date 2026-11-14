# Konfiqurasiya

Ayarlar [goodconf](https://github.com/lincolnloop/goodconf) ilə yüklənir. Onları kodda ötürmək, mühit dəyişənlərində təyin etmək, faylda saxlamaq və ya bu üç yolu birlikdə işlətmək olar.

## Üstünlük sırası

Eyni ayar bir neçə yerdən gələndə siyahıda yuxarıda olan üstün tutulur:

1. `Epoint(...)` və ya `AsyncEpoint(...)` çağırışına verilən arqumentlər.
2. `EPOINT_` ilə başlayan mühit dəyişənləri.
3. Konfiqurasiya faylı.
4. Daxili standart dəyər.

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

Aşağıdakı cədvəldəki istənilən ayarı açar sözlü arqument kimi vermək olar.

## Mühit dəyişənləri

Hər ayarın `EPOINT_` və böyük hərflərlə ayar adından ibarət dəyişəni var:

```console
$ export EPOINT_PUBLIC_KEY=i000000001
$ export EPOINT_PRIVATE_KEY=your-private-key
$ export EPOINT_SUCCESS_URL=https://shop.az/payment/ok
$ export EPOINT_ERROR_URL=https://shop.az/payment/fail
$ export EPOINT_LANGUAGE=az
$ export EPOINT_TIMEOUT=30
$ export EPOINT_MAX_RETRIES=2
```

Windows CMD-də `export` əvəzinə `set AD=dəyər` yazın.

Dəyişənlər təyin olunubsa, klientə arqument lazım deyil:

```python
ep = Epoint()
```

## Konfiqurasiya faylı

Arqument verilməyəndə klient işçi qovluqda bu sıra ilə `epoint.toml`, `epoint.yaml`, `epoint.yml` və ya `epoint.json` faylını da axtarır:

```toml
public_key = "i000000001"
private_key = "your-private-key"
success_url = "https://shop.az/payment/ok"
error_url = "https://shop.az/payment/fail"
language = "az"
timeout = 30
```

Faylı başqa yerdən oxumaq üçün ya `EPOINT_CONFIG` dəyişənində onun yolunu göstərin, ya da `config_file` arqumentini verin:

```console
$ export EPOINT_CONFIG=/etc/myshop/epoint.toml
```

```python
ep = Epoint(config_file="/etc/myshop/epoint.toml")
```

YAML üçün `yaml` əlavəsi, Python 3.10-da TOML üçün isə `toml` əlavəsi lazımdır. Bax: [Quraşdırma](installation.md#əlavə-paketlər).

```{warning}
Məxfi açar olan konfiqurasiya faylı repozitoriyanıza düşməməlidir. Onu `.gitignore` faylına əlavə edin, ya da faylda yalnız məxfi olmayan ayarları saxlayıb açarları mühit dəyişənlərinə köçürün.
```

## Bütün ayarlar

| Ayar | Mühit dəyişəni | Standart dəyər | Mənası |
| --- | --- | --- | --- |
| `public_key` | `EPOINT_PUBLIC_KEY` | (boş) | Tacirin açıq açarı, məsələn `i000000001`. Mütləqdir |
| `private_key` | `EPOINT_PRIVATE_KEY` | (boş) | Tacirin məxfi açarı. Sorğuları imzalayır və callback-ləri yoxlayır. Mütləqdir |
| `base_url` | `EPOINT_BASE_URL` | `https://epoint.az` | Ödəniş sisteminin ünvanı. Test zamanı onu sandbox-a yönəldin |
| `endpoints.*` | `EPOINT_ENDPOINTS__<AD>` | bax: [Endpoint-lər](reference/endpoints.md) | Hər API çağırışının `base_url` ünvanına nisbətən yolu |
| `language` | `EPOINT_LANGUAGE` | `az` | Ödəniş səhifəsinin dili: `az`, `en` və ya `ru` |
| `currency` | `EPOINT_CURRENCY` | `AZN` | Standart valyuta: `AZN`, `USD`, `EUR` və ya `RUB` |
| `success_url` | `EPOINT_SUCCESS_URL` | yoxdur | Müştərinin uğurlu ödənişdən sonra qayıtdığı səhifə |
| `error_url` | `EPOINT_ERROR_URL` | yoxdur | Müştərinin uğursuz ödənişdən sonra qayıtdığı səhifə |
| `timeout` | `EPOINT_TIMEOUT` | `30` | Cavab üçün gözləmə müddəti, saniyə ilə. Sıfırdan böyük olmalıdır |
| `connect_timeout` | `EPOINT_CONNECT_TIMEOUT` | `10` | Bağlantı üçün gözləmə müddəti, saniyə ilə. Sıfırdan böyük olmalıdır |
| `max_retries` | `EPOINT_MAX_RETRIES` | `2` | Təkrarlanması təhlükəsiz olan sorğular üçün əlavə cəhdlərin sayı. 0-dan 10-a qədər |
| `backoff_base` | `EPOINT_BACKOFF_BASE` | `0.5` | Təkrar cəhdlər arasında ilk gözləmə, saniyə ilə |
| `backoff_cap` | `EPOINT_BACKOFF_CAP` | `8` | Təkrar cəhdlər arasında ən uzun gözləmə, saniyə ilə |
| `user_agent` | `EPOINT_USER_AGENT` | `epoint-python-sdk/{version}` | `User-Agent` başlığı. `{version}` SDK versiyası ilə əvəz olunur |
| `allow_insecure_http` | `EPOINT_ALLOW_INSECURE_HTTP` | `False` | localhost xaricində adi `http` ünvanına icazə verir. Yalnız daxili şəbəkədəki sandbox üçündür |

Təkrar cəhdlər və gözləmə müddətləri [Etibarlılıq](guides/reliability.md) səhifəsində ətraflı izah olunur.

Dəyərlər klient yaradılanda yoxlanılır. Naməlum dil, kiçik hərflə yazılmış valyuta (`USD` əvəzinə `usd`), sıfır gözləmə müddəti və ya 10-dan böyük `max_retries` pydantic-in `ValidationError` xətasını qaldırır. Beləcə mühit dəyişənindəki hərf səhvi tətbiqi elə işə düşəndə dayandırır.

## Hər sorğuda dəyişdirilə bilən standart dəyərlər

`language`, `currency`, `success_url` və `error_url` standart dəyərlərdir. Ödəniş metodlarının çoxu eyni adlı açar sözlü arqumentləri qəbul edir və sorğuya verilən dəyər üstün tutulur:

```python
ep.payments.create("10", "ORDER-7", language="en", currency="USD",
                   success_url="https://shop.az/en/thanks")
```

## Ayarları özünüz yaratmaq

`load_settings` mühit dəyişənlərini və faylları klientlə eyni qaydada oxuyur. Nəticədə baxa və ya təkrar istifadə edə biləcəyiniz `Settings` obyekti alırsınız:

```python
from epoint_sdk import Epoint, load_settings

settings = load_settings("/etc/myshop/epoint.toml", timeout=15)
print(settings.base_url, settings.timeout)

ep = Epoint(settings=settings)
```

Həm `settings`, həm də açar sözlü arqumentlər verilsə, arqumentlər ayarların üzərinə yazılır:

```python
staging = Epoint(settings=settings, base_url="http://localhost:8181")
```

## Adi http qəbul edilmir

İmzalı sorğular yalnız `https` ilə göndərilir. `http://` ilə başlayan `base_url` klient yaradılanda `ConfigurationError` qaldırır. İki istisna var:

- `localhost`, `127.0.0.1` və `::1` həmişə icazəlidir, ona görə öz kompüterinizdəki sandbox işləyir.
- `allow_insecure_http=True` istənilən hosta icazə verir. Ondan yalnız daxili şəbəkədəki sandbox üçün istifadə edin.

## Öz HTTP klientiniz

Proksi, xüsusi sertifikatlar və ya testlərdə saxta transport işlətmək üçün `httpx.Client` (`AsyncEpoint` üçün `httpx.AsyncClient`) ötürün:

```python
import httpx
from epoint_sdk import Epoint

http = httpx.Client(proxy="http://proxy.internal:3128", timeout=20)
ep = Epoint(http_client=http)
```

Öz klientinizi verəndə `timeout` və `connect_timeout` əvəzinə onun gözləmə ayarları işləyir və onu bağlamaq sizin üzərinizə düşür. `ep.close()` yalnız SDK-nın özünün yaratdığı klienti bağlayır.
