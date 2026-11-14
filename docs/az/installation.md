# Quraşdırma

Bu səhifə quraşdırmanı sıfırdan göstərir: virtual mühit, paketin özü, işlədiyinin yoxlanması, sonra isə paketin yenilənməsi və silinməsi.

## Tələblər

- Python 3.10, 3.11, 3.12 və ya 3.13.
- Sorğuları göndərən serverdən `https://epoint.az` ünvanına şəbəkə çıxışı.
- Real ödənişlər üçün Epoint tacir hesabı. İnteqrasiyanı yazarkən [lokal sandbox](guides/testing.md) kifayətdir.

Əvvəlcə Python versiyasını yoxlayın:

::::{tab-set}

:::{tab-item} Linux və macOS
```console
$ python3 --version
Python 3.12.3
```
:::

:::{tab-item} Windows (CMD)
```bat
py --version
```
:::

::::

## 1-ci addım. Virtual mühit yaradın

Virtual mühit bir layihənin paketlərini kompüterdəki digər hər şeydən ayrı saxlayır. Layihə qovluğunuzda yeni mühit yaradın:

::::{tab-set}

:::{tab-item} Linux və macOS
```console
$ cd my-shop
$ python3 -m venv .venv
$ source .venv/bin/activate
```
:::

:::{tab-item} Windows (CMD)
```bat
cd my-shop
py -m venv .venv
.venv\Scripts\activate.bat
```
:::

::::

Mühit aktiv olanda əmr sətrinin əvvəlində `(.venv)` görünür. Bundan sonra hər `pip install` əmri paketləri yalnız bu qovluğa quraşdırır.

## 2-ci addım. Paketi quraşdırın

::::{tab-set}

:::{tab-item} pip
```console
$ pip install epoint-python-sdk
```
:::

:::{tab-item} uv
```console
$ uv add epoint-python-sdk
```
Layihəni uv idarə etmirsə, `uv pip install epoint-python-sdk` yazın.
:::

:::{tab-item} Poetry
```console
$ poetry add epoint-python-sdk
```
:::

::::

Paketin PyPI adı `epoint-python-sdk`, Python-da import adı isə `epoint_sdk` olur:

```python
from epoint_sdk import Epoint
```

### Əlavə paketlər

Ayarları fayldan da oxumaq olar (bax: [Konfiqurasiya](configuration.md)). JSON faylları əlavə heç nə tələb etmir. Digər formatlar üçün iki əlavə var:

| Əlavə | Quraşdırma | Nə vaxt lazımdır |
| --- | --- | --- |
| `yaml` | `pip install "epoint-python-sdk[yaml]"` | Ayarları `epoint.yaml` və ya `epoint.yml` faylında saxlayırsınız |
| `toml` | `pip install "epoint-python-sdk[toml]"` | Ayarları `epoint.toml` faylında saxlayırsınız və Python 3.10 işlədirsiniz. Python 3.11 və daha yeni versiyalar TOML faylını bu əlavə olmadan oxuyur |

## 3-cü addım. Quraşdırmanı yoxlayın

```console
$ python -c "import epoint_sdk; print(epoint_sdk.__version__)"
0.2.0
```

Açarlarınız artıq varsa, ödəniş sisteminin işlək olub-olmadığını da soruşa bilərsiniz. `heartbeat()` imzasız sorğudur və Epoint `ok` cavabı verəndə `True` qaytarır:

```python
from epoint_sdk import Epoint

with Epoint("i000000001", "PRIVATE_KEY") as ep:
    print(ep.heartbeat())
```

## 4-cü addım. Versiyanı sabitləyin

Ödəniş kodu xəbəriniz olmadan dəyişməməlidir. Versiyanı asılılıqlar faylında sabitləyin və yeniləməni şüurlu şəkildə edin:

```text
epoint-python-sdk==0.2.0
```

## Yeniləmə

```console
$ pip install --upgrade epoint-python-sdk
```

Yeniləməzdən əvvəl [dəyişikliklər siyahısını](reference/changelog.md) oxuyun, sonra isə ödəniş testlərinizi işə salın.

## Silmə

```console
$ pip uninstall epoint-python-sdk
```

## Mənbə kodundan quraşdırma

Hələ buraxılmamış dəyişikliyi sınamaq üçün paketi birbaşa GitHub-dan quraşdırın:

```console
$ pip install "git+https://github.com/qiyascc/epoint-python-sdk.git"
```

SDK-nın özü üzərində işləmək üçün [İnkişaf](development.md) səhifəsinə baxın.

## Növbəti addım

[Tacir hesabı və açarlar](keys.md) səhifəsində açarlarınızı hazırlayın, sonra [Sürətli başlanğıc](quickstart.md) ilə ilk ödənişi edin.
