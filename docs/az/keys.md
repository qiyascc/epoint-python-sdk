# Tacir hesabı və açarlar

Epoint-ə göndərilən hər sorğu hansısa tacirin (merchant) adından göndərilir. Tacir iki dəyərlə tanınır: açıq açar və məxfi açar. Bu səhifədə onların nə olduğu, haradan alındığı və necə qorunduğu izah olunur.

## İki açar

`public_key`
: Tacirin identifikatoru. `i000000001` kimi görünür: əvvəlində `i` hərfi, ardınca rəqəmlər. Hər sorğunun içində göndərilir, ona görə də sirr deyil.

`private_key`
: Ortaq sirr. SDK onunla hər sorğunu imzalayır və hər callback-in imzasını yoxlayır. Bu açar kimdədirsə, sizin adınızdan sorğu göndərə və real ödənişə oxşayan saxta callback hazırlaya bilər. Ona parol kimi yanaşın.

## Açarları necə almaq olar

Açarları Epoint sizinlə tacir müqaviləsi bağlayandan sonra verir. Tacir kabinetində saytınızı və Epoint-in istifadə edəcəyi ünvanları qeyd edirsiniz:

- müştərinin uğurlu ödənişdən sonra qayıtdığı səhifə,
- müştərinin uğursuz ödənişdən sonra qayıtdığı səhifə,
- Epoint-in imzalı callback göndərdiyi nəticə ünvanı.

Bundan sonra açar cütünü alırsınız. Kabinetin görünüşü dəyişə bilər, ona görə nəsə aydın olmasa, Epoint-in dəstək xidmətinə müraciət edin.

```{note}
SDK nəticə ünvanını sorğu ilə göndərmir. Epoint onu kabinetdən bilir. Uğurlu və uğursuz ödəniş səhifələrini isə həm hər sorğuda ayrıca, həm də SDK ayarlarında standart dəyər kimi vermək olar.
```

## Ayrıca aktivləşdirilən imkanlar

Bəzi imkanları Epoint hər tacir üçün ayrıca, müraciət əsasında açır. İmkan açılana qədər Epoint sorğunu rədd edir və SDK `GatewayError` qaldırır. Aşağıdakılardan birinə əsaslanan kod yazmazdan əvvəl Epoint ilə danışın:

- Apple Pay və Google Pay (vidjet),
- taksit,
- elektron pul kisələri,
- B2B bank köçürmələri,
- American Express kartları.

## Test və real rejim

Epoint test kartları dərc etmir. Tacir hesabı olmadan inteqrasiya qurub sınamaq üçün icma tərəfindən hazırlanmış [epoint-sandbox](https://github.com/martian56/epoint-sandbox) layihəsini işə salın. O, Epoint API-sini təkrarlayır və callback-ləri eyni qaydada imzalayır. `base_url` ayarını ona yönəldin, onun demo açarlarını işlədin, real işə keçəndə isə `https://epoint.az` ünvanına və öz açarlarınıza qayıdın. Tam quraşdırma qaydası [Test](guides/testing.md) səhifəsindədir.

## Açarları SDK-ya ötürmək

Kodda ötürün:

```python
from epoint_sdk import Epoint

ep = Epoint("i000000001", "PRIVATE_KEY")
```

və ya mühit dəyişənləri təyin edib klienti arqumentsiz yaradın:

::::{tab-set}

:::{tab-item} Linux və macOS
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

Açarlardan biri yoxdursa və ya boşdursa, konstruktor dərhal `ConfigurationError` qaldırır. Beləliklə, səhv quraşdırılmış tətbiq ödəniş prosesinin ortasında yox, elə işə düşəndə dayanır. Klienti konfiqurasiya etməyin digər yolları [Konfiqurasiya](configuration.md) səhifəsindədir.

## Məxfi açarı necə qorumalı

- Onu yalnız serverdə saxlayın. Heç vaxt JavaScript koduna, mobil tətbiqə və ya şablona qoymayın.
- Onu versiya nəzarəti sisteminə əlavə etməyin. Mühit dəyişənlərindən və ya sirr meneceri xidmətindən istifadə edin.
- SDK açarı pydantic-in `SecretStr` tipində saxlayır. Ayarlar ekrana çıxarılanda və ya loqa yazılanda açarın yerində `**********` görünür, `repr(ep)` isə yalnız açıq açarı göstərir.
- Açar sızıbsa, Epoint-dən yeni cüt istəyin. Açar dəyişən kimi köhnə imzalar işləmir.

Ətraflı məlumat [Təhlükəsizlik](guides/security.md) səhifəsindədir.
