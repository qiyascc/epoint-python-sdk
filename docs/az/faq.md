# Tez-tez verilən suallar və problemlərin həlli

## Klient işə düşəndə "Epoint public_key and private_key are required" xətası verir

Açarlar klientə çatmayıb. `EPOINT_PUBLIC_KEY` və `EPOINT_PRIVATE_KEY` dəyişənlərinin yalnız terminalınızda deyil, tətbiqi işə salan prosesin mühitində də təyin olunduğunu yoxlayın. Konfiqurasiya faylı işlədirsinizsə, onun işçi qovluqda olduğuna və ya `EPOINT_CONFIG` dəyişənində göstərildiyinə əmin olun.

## "Refusing to send signed requests over plain http"

`base_url` `http://` ilə başlayır və localhost olmayan ünvana yönəlib. `https` işlədin. Daxili şəbəkədəki sandbox üçün `allow_insecure_http=True` ayarını yalnız orada təyin edin.

## Bütün callback-lər SignatureError ilə uğursuz olur

- Serverdəki məxfi açar Epoint-in tacir hesabınız üçün istifadə etdiyi açar deyil. Artıq boşluqları və ya başqa mühitdən götürülmüş açarı yoxlayın.
- Epoint ilə tətbiqiniz arasında nəsə gövdəni dəyişir: formaları yenidən yazan proksi və ya gövdəni view-dan əvvəl oxuyan freymvork. Orijinal `data` və `signature` dəyərlərini ötürün.
- Başqa açarla imzalanmış callback ilə test edirsiniz, məsələn real konfiqurasiyaya qarşı sandbox açarı ilə.

## İkinci ödəniş cəhdində GatewayError

Epoint artıq gördüyü `order_id` dəyərini rədd edir. Yeni cəhd üçün yeni identifikator işlədin, məsələn sifariş nömrəsi və cəhd sayğacı. Bax: [Ödənişlər](guides/payments.md#sifariş-identifikatorları).

## Apple Pay, taksit, pul kisələri və ya B2B köçürmələrdə GatewayError

Bu imkanları Epoint hər tacir üçün ayrıca aktivləşdirir. Epoint-dən onları hesabınız üçün açmasını xahiş edin.

## Müştəri uğurlu ödəniş səhifəsinə qayıdıb, amma sifariş hələ gözləmədədir

Callback hələ gəlməyib və ya uğursuz olub. "Təsdiqləyirik" mesajı göstərin, öz backend-inizi dövri olaraq soruşun, ehtiyac olanda isə serverdə `payments.status()` çağırın. Bax: [Callback-lər](guides/callbacks.md#uğurlu-ödəniş-səhifəsi-təsdiq-deyil).

## OutcomeUnknownError aldım. Müştəridən pul çıxılıb?

Ola bilər. Sorğu Epoint-ə çatıb, amma aydın cavab gəlməyib. Sorğunu yeni sifariş identifikatoru ilə yenidən göndərməyin. Vəziyyəti yoxlayın, callback-i gözləyin və ya eyni sifariş identifikatoru ilə təkrarlayın. Bax: [Etibarlılıq](guides/reliability.md#outcomeunknownerror-ilə-necə-davranmalı).

## Normal görünən məbləğ üçün InvalidRequestError

Məbləğlərdə ən çox iki onluq rəqəm ola bilər. `0.1 + 0.2` kimi float `0.30000000000000004` olur və rədd edilir. Pul üçün sətir və ya `Decimal` işlədin.

## SDK-nı bir neçə thread-dən istifadə etmək olar?

Bəli. Sinxron klient thread-safe olan `httpx.Client` işlədir. Bir klient yaradın və onu paylaşın.

## Django-nun asinxron view-larında işləyir?

Asinxron view-larda `AsyncEpoint`, sinxron view-larda isə `Epoint` işlədin. Sinxron klienti asinxron view-dan çağırmayın, o, event loop-u bloklayır.

## Nəyin göndərildiyini necə görmək olar?

httpx loqlarını aktiv edin:

```python
import logging

logging.basicConfig(level=logging.WARNING)
logging.getLogger("httpx").setLevel(logging.INFO)
```

Bu, hər sorğunun metodunu, URL-ini və statusunu loqa yazır. İmzalı gövdə loqa yazılmır.

## Xətanı harada bildirmək olar?

[github.com/qiyascc/epoint-python-sdk/issues](https://github.com/qiyascc/epoint-python-sdk/issues) ünvanında issue açın. SDK versiyasını, çağırdığınız metodu və əlinizdədirsə `trace_id` dəyərini yazın. Məxfi açarınızı heç vaxt əlavə etməyin.
