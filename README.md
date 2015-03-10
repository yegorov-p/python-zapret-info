python-zapret-info
==================

[![Code Health](https://landscape.io/github/yegorov-p/python-zapret-info/master/landscape.svg?style=flat)](https://landscape.io/github/yegorov-p/python-zapret-info/master)

Python class for http://vigruzki.rkn.gov.ru/ API

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

Перегенерирование файла для каждого запуска, с исправлением requestTime на актуальный, на данный момент не требуется.  
Также требуется отсоединенная электронная подпись в формате PKCS#7 (PEM или DER)  

Описание текущего API http://vigruzki.rkn.gov.ru/docs/description_for_operators_actual.pdf

##Запуск##
python zapret_checker.py 
###Ключи###
**-r, --request** файл, содержащий данные об операторе  
**-s, --signature** файл, содержащий отсоединенную электронную подпись в формате PKCS#7 (PEM или DER)  
**-l, --log** файл, в который будет записываться лог (по умолчанию *rkn_dump.log*)

###crontab -e###
*/10 * * * * /путь_к_папке_со_скриптом && python zapret_checker.py -r req.xml -s req.der

###При обновлении 10 марта###
При переходе на версию реестра 2.1 10 марта, либо если Вы получаете ошибку вида 

    Exception: '<operatorName/>' not mapped to message part
следует очистить кэш, например так:

    rm /tmp/suds/*
