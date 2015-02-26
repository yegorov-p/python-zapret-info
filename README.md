python-zapret-info
==================

[![Code Health](https://landscape.io/github/yegorov-p/python-zapret-info/master/landscape.svg?style=flat)](https://landscape.io/github/yegorov-p/python-zapret-info/master)

Python class for http://zapret-info.gov.ru/ API

Для работы требуется сгенерировать XML вида

```python
<?xml version="1.0" encoding="windows-1251"?>
<request>
<requestTime>2012-01-01T01:01:01.000+04:00</requestTime>
<operatorName>Наименование оператора</operatorName>
<inn>1234567890</inn>
<ogrn>1234567890123</ogrn>
<email>email@email.ru</email>
</request>
```

Перегенерирование файла для каждого запуска, с исправлением requestTime на актуальный, не требуется.

Также требуется отсоединенная электронная подпись в формате PKCS#7

Описание текущего API http://vigruzki.rkn.gov.ru/docs/description_for_operators_actual.pdf
