# İnkişaf

SDK-nın özü üzərində necə işləmək olar.

## Hazırlıq

```console
$ git clone https://github.com/qiyascc/epoint-python-sdk.git
$ cd epoint-python-sdk
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -e ".[dev]"
```

## Yoxlamalar

```console
$ pytest
$ ruff check .
$ mypy src
```

Testlər `httpx.MockTransport` və `tests/conftest.py` faylındakı kiçik saxta ödəniş sistemindən istifadə edir, ona görə real API-yə heç vaxt müraciət etmir. CI onları Python 3.10, 3.11, 3.12 və 3.13 üzərində işə salır.

## Layihənin quruluşu

| Yol | Məzmun |
| --- | --- |
| `src/epoint_sdk/client.py` | `Epoint` və `AsyncEpoint` |
| `src/epoint_sdk/_core.py` | Göndərmə, təkrar cəhdlər və xətaların müəyyənləşdirilməsi |
| `src/epoint_sdk/resources.py` | Bölmələr: payments, cards, split və digərləri |
| `src/epoint_sdk/models.py` | Nəticə dataclass-ları |
| `src/epoint_sdk/signing.py` | `data` və `signature` dəyərlərinin imzalanması və yoxlanması |
| `src/epoint_sdk/callbacks.py` | `verify_callback` və `callback_form` |
| `src/epoint_sdk/money.py` | Məbləğlərin oxunması |
| `src/epoint_sdk/config.py` | `Settings` və endpoint yolları |
| `src/epoint_sdk/messages.yaml` | Bütün mesaj mətnləri |
| `tests/` | Testlər |
| `docs/` | Bu sənədlər, azərbaycan, ingilis və türk dillərində |

## Sənədlərin yığılması

```console
$ pip install -r docs/requirements.txt
$ sphinx-build -W -b html docs/az docs/az/_build/html
$ sphinx-build -W -b html docs/en docs/en/_build/html
$ sphinx-build -W -b html docs/tr docs/tr/_build/html
```

Hər dil öz `conf.py` faylı olan ayrıca Sphinx layihəsidir. Ortaq ayarlar, şablonlar və üslublar `docs/_common/` qovluğundadır.

## Dəyişikliklər üçün qaydalar

- Pul hərəkət etdirən çağırış nəticəsi bəlli olmayan xətadan sonra heç vaxt təkrarlanmamalıdır. Hər yeni çağırış üçün onun hansı qrupa aid olduğunu yoxlayan test əlavə edin.
- İstifadəçiyə görünən hər mesaj `messages.yaml` faylına yazılır.
- Yeni endpoint yolları onları çağıran koda yox, `config.py` faylındakı `Endpoints` sinfinə əlavə olunur.
- `CHANGELOG.md` faylını və sənədlərin hər üç dildəki versiyasını yeniləyin.
