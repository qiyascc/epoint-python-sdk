# Üye işyeri hesabı ve anahtarlar

Epoint'e gönderilen her istek bir üye işyeri (merchant) adına yapılır. Üye işyeri iki değerle tanımlanır: açık anahtar ve gizli anahtar. Bu sayfa bunların ne olduğunu, nereden alındığını ve nasıl korunacağını anlatır.

## İki anahtar

`public_key`
: Üye işyerinin kimliği. `i000000001` gibi görünür: başta `i` harfi, ardından rakamlar. Her isteğin içinde gönderilir, bu yüzden gizli değildir.

`private_key`
: Paylaşılan sır. SDK her isteği bununla imzalar ve her callback'in imzasını bununla doğrular. Bu anahtar kimin elindeyse sizin adınıza istek gönderebilir ve gerçek ödeme gibi görünen sahte callback'ler üretebilir. Ona bir parola gibi davranın.

## Anahtarları almak

Anahtarları Epoint, sizinle üye işyeri sözleşmesi imzaladıktan sonra verir. Üye işyeri panelinde sitenizi ve Epoint'in kullanacağı adresleri kaydedersiniz:

- müşterinin başarılı ödemeden sonra döndüğü sayfa,
- müşterinin başarısız ödemeden sonra döndüğü sayfa,
- Epoint'in imzalı callback gönderdiği sonuç adresi.

Ardından anahtar çiftinizi alırsınız. Panelin görünümü değişebilir, bu yüzden bir şey belirsizse Epoint destek ekibine başvurun.

```{note}
SDK sonuç adresini istekle birlikte göndermez. Epoint bu adresi panelden bilir. Başarılı ve başarısız ödeme sayfaları ise her istekte ayrıca veya SDK ayarlarında varsayılan olarak verilebilir.
```

## Ayrıca açılması gereken özellikler

Bazı özellikleri Epoint her üye işyeri için ayrı ayrı ve talep üzerine açar. Açılana kadar Epoint isteği reddeder ve SDK `GatewayError` fırlatır. Aşağıdakilerden birine dayanan kod yazmadan önce Epoint ile görüşün:

- Apple Pay ve Google Pay (widget),
- taksit,
- dijital cüzdanlar,
- B2B banka transferleri,
- American Express kartları.

## Test ve canlı ortam

Epoint test kartı yayımlamaz. Üye işyeri hesabı olmadan entegrasyon kurup denemek için topluluk tarafından geliştirilen [epoint-sandbox](https://github.com/martian56/epoint-sandbox) projesini çalıştırın. Bu proje Epoint API'sini taklit eder ve callback'leri aynı şekilde imzalar. `base_url` ayarını ona yönlendirin, onun demo anahtarlarını kullanın, canlıya geçerken de `https://epoint.az` adresine ve kendi anahtarlarınıza dönün. Kurulumun tamamı [Test](guides/testing.md) sayfasında anlatılıyor.

## Anahtarları SDK'ya vermek

Kodda verin:

```python
from epoint_sdk import Epoint

ep = Epoint("i000000001", "PRIVATE_KEY")
```

veya ortam değişkenlerini tanımlayıp istemciyi argümansız oluşturun:

::::{tab-set}

:::{tab-item} Linux ve macOS
```console
$ export EPOINT_PUBLIC_KEY=i000000001
$ export EPOINT_PRIVATE_KEY=your-private-key
```
:::

:::{tab-item} Windows (CMD)
```bat
set EPOINT_PUBLIC_KEY=i000000001
set EPOINT_PRIVATE_KEY=your-private-key
```
:::

::::

```python
ep = Epoint()
```

Anahtarlardan biri eksik veya boşsa yapıcı hemen `ConfigurationError` fırlatır. Böylece hatalı yapılandırılmış bir uygulama ödeme sırasında değil, açılırken durur. İstemciyi yapılandırmanın diğer yolları [Yapılandırma](configuration.md) sayfasındadır.

## Gizli anahtarı korumak

- Yalnızca sunucuda tutun. Asla JavaScript koduna, mobil uygulamaya veya bir şablona koymayın.
- Sürüm kontrolüne eklemeyin. Ortam değişkenlerini veya bir gizli bilgi yöneticisini kullanın.
- SDK anahtarı pydantic'in `SecretStr` tipinde saklar. Ayarlar ekrana yazdırıldığında veya loglandığında anahtarın yerinde `**********` görünür, `repr(ep)` ise yalnızca açık anahtarı gösterir.
- Anahtar sızdıysa Epoint'ten yeni bir çift isteyin. Anahtar değiştiği anda eski imzalar geçersiz olur.

Ayrıntılar [Güvenlik](guides/security.md) sayfasında.
