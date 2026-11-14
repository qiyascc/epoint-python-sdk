# Geliştirme

SDK'nın kendisi üzerinde nasıl çalışılır.

## Hazırlık

```console
$ git clone https://github.com/qiyascc/epoint-python-sdk.git
$ cd epoint-python-sdk
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -e ".[dev]"
```

## Kontroller

```console
$ pytest
$ ruff check .
$ mypy src
```

Testler `httpx.MockTransport` ve `tests/conftest.py` içindeki küçük bir sahte ödeme altyapısı kullanır, bu yüzden gerçek API'ye hiç dokunmaz. CI testleri Python 3.10, 3.11, 3.12 ve 3.13 üzerinde çalıştırır.

## Proje yapısı

| Yol | İçerik |
| --- | --- |
| `src/epoint_sdk/client.py` | `Epoint` ve `AsyncEpoint` |
| `src/epoint_sdk/_core.py` | Gönderim, yeniden denemeler ve hataların eşlenmesi |
| `src/epoint_sdk/resources.py` | Bölümler: payments, cards, split ve diğerleri |
| `src/epoint_sdk/models.py` | Sonuç dataclass'ları |
| `src/epoint_sdk/signing.py` | `data` ve `signature` değerlerinin imzalanması ve doğrulanması |
| `src/epoint_sdk/callbacks.py` | `verify_callback` ve `callback_form` |
| `src/epoint_sdk/money.py` | Tutarların ayrıştırılması |
| `src/epoint_sdk/config.py` | `Settings` ve uç nokta yolları |
| `src/epoint_sdk/messages.yaml` | Tüm mesaj metinleri |
| `tests/` | Test paketi |
| `docs/` | Bu belgeler, Azerbaycanca, İngilizce ve Türkçe |

## Belgeleri derlemek

```console
$ pip install -r docs/requirements.txt
$ sphinx-build -W -b html docs/tr docs/tr/_build/html
$ sphinx-build -W -b html docs/az docs/az/_build/html
$ sphinx-build -W -b html docs/en docs/en/_build/html
```

Her dil kendi `conf.py` dosyası olan ayrı bir Sphinx projesidir. Ortak ayarlar, şablonlar ve stiller `docs/_common/` klasöründedir.

## Değişiklik kuralları

- Para hareketi yaratan bir çağrı, sonucu belirsiz bir hatadan sonra asla yeniden denenmemelidir. Her yeni çağrı için hangi gruba ait olduğunu kontrol eden bir test ekleyin.
- Kullanıcıya görünen her mesaj `messages.yaml` dosyasına yazılır.
- Yeni uç nokta yolları onları çağıran koda değil, `config.py` içindeki `Endpoints` sınıfına eklenir.
- `CHANGELOG.md` dosyasını ve belgelerin üç dildeki halini de güncelleyin.
