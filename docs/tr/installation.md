# Kurulum

Bu sayfa kurulumu sıfırdan anlatır: sanal ortam, paketin kendisi, çalıştığının kontrolü ve daha sonra paketin nasıl güncelleneceği veya kaldırılacağı.

## Gereksinimler

- Python 3.10, 3.11, 3.12 veya 3.13.
- İstekleri gönderen sunucudan `https://epoint.az` adresine ağ erişimi.
- Gerçek ödemeler için bir Epoint üye işyeri hesabı. Entegrasyonu geliştirirken [yerel sandbox](guides/testing.md) yeterlidir.

Önce Python sürümünüzü kontrol edin:

::::{tab-set}

:::{tab-item} Linux ve macOS
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

## 1. adım. Sanal ortam oluşturun

Sanal ortam, bir projenin paketlerini bilgisayardaki diğer her şeyden ayrı tutar. Proje klasörünüzde yeni bir ortam oluşturun:

::::{tab-set}

:::{tab-item} Linux ve macOS
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

Ortam etkinken komut satırının başında `(.venv)` görünür. Bundan sonra her `pip install` komutu paketleri yalnızca bu klasöre kurar.

## 2. adım. Paketi kurun

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
Proje uv ile yönetilmiyorsa `uv pip install epoint-python-sdk` yazın.
:::

:::{tab-item} Poetry
```console
$ poetry add epoint-python-sdk
```
:::

::::

Paketin PyPI adı `epoint-python-sdk`, Python'daki içe aktarma adı ise `epoint_sdk`'dir:

```python
from epoint_sdk import Epoint
```

### Ek paketler

Ayarlar bir dosyadan da okunabilir (bkz. [Yapılandırma](configuration.md)). JSON dosyaları için ek bir şey gerekmez. Diğer biçimler için iki ek paket vardır:

| Ek | Kurulum | Ne zaman gerekir |
| --- | --- | --- |
| `yaml` | `pip install "epoint-python-sdk[yaml]"` | Ayarları `epoint.yaml` veya `epoint.yml` dosyasında tutuyorsanız |
| `toml` | `pip install "epoint-python-sdk[toml]"` | Ayarları `epoint.toml` dosyasında tutuyor ve Python 3.10 kullanıyorsanız. Python 3.11 ve sonrası TOML dosyasını bu ek olmadan okur |

## 3. adım. Kurulumu kontrol edin

```console
$ python -c "import epoint_sdk; print(epoint_sdk.__version__)"
0.2.0
```

Anahtarlarınız hazırsa ödeme altyapısının çalışıp çalışmadığını da sorabilirsiniz. `heartbeat()` imzasız bir istektir ve Epoint `ok` yanıtı verdiğinde `True` döndürür:

```python
from epoint_sdk import Epoint

with Epoint("i000000001", "PRIVATE_KEY") as ep:
    print(ep.heartbeat())
```

## 4. adım. Sürümü sabitleyin

Ödeme kodu siz farkında olmadan değişmemelidir. Sürümü bağımlılık dosyanızda sabitleyin ve güncellemeyi bilerek yapın:

```text
epoint-python-sdk==0.2.0
```

## Güncelleme

```console
$ pip install --upgrade epoint-python-sdk
```

Güncellemeden önce [değişiklik günlüğünü](reference/changelog.md) okuyun, ardından ödeme testlerinizi çalıştırın.

## Kaldırma

```console
$ pip uninstall epoint-python-sdk
```

## Kaynak koddan kurulum

Henüz yayımlanmamış bir değişikliği denemek için paketi doğrudan GitHub'dan kurun:

```console
$ pip install "git+https://github.com/qiyascc/epoint-python-sdk.git"
```

SDK'nın kendisi üzerinde çalışmak için [Geliştirme](development.md) sayfasına bakın.

## Sonraki adım

[Üye işyeri hesabı ve anahtarlar](keys.md) sayfasında anahtarlarınızı hazırlayın, ardından [Hızlı başlangıç](quickstart.md) ile ilk ödemenizi yapın.
