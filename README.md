# Remanga Parser
**Remanga Parser** – это кроссплатформенный скрипт для получения данных с сайта [Remanga](https://remanga.org/) в формате JSON. Он позволяет записать всю информацию о конкретной манге, а также её главах и содержании глав.

## Порядок установки и использования
1. Загрузить последний релиз. Распаковать.
2. Установить Python версии не старше 3.10. Рекомендуется добавить в PATH.
3. В среду исполнения установить следующие пакеты: [dublib](https://github.com/DUB1401/dublib), [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager), [BeautifulSoup4](https://launchpad.net/beautifulsoup), [fake-useragent](https://github.com/fake-useragent/fake-useragent), [opencv-python](https://github.com/opencv/opencv-python), [selenium-wire](https://github.com/wkeeling/selenium-wire), [cloudscraper](https://github.com/VeNoMouS/cloudscraper), [scikit-image](https://github.com/scikit-image/scikit-image), [Pillow](https://github.com/python-pillow/Pillow).
```
pip install git+https://github.com/DUB1401/dublib
pip install webdriver-manager
pip install BeautifulSoup4
pip install fake-useragent
pip install opencv-python
pip install selenium-wire
pip install cloudscraper
pip install scikit-image
pip install Pillow
```
Либо установить сразу все пакеты при помощи следующей команды, выполненной из директории скрипта.
```
pip install -r requirements.txt
```
4. Настроить скрипт путём редактирования _Settings.json_ и _Proxies.json_.
5. При использовании [Selenium](https://github.com/SeleniumHQ/selenium) для отправки запросов необходимо установить браузер [Google Chrome](https://www.google.com.iq/chrome/) в стандартную директорию на Windows, либо использовать _*.deb_ или _*.rpm_ пакет на Linux.
6. Открыть директорию со скриптом в терминале. Можно использовать метод `cd` и прописать путь к папке, либо запустить терминал из проводника.
7. Указать для выполнения главный файл скрипта `rp.py`, передать ему команду вместе с параметрами, нажать кнопку ввода и дождаться завершения работы.

# Консольные команды
```
collect [FLAGS] [KEYS*]
```
Собирает коллекцию из алиасов тайтлов, соответствующих набору фильтров в каталоге [Remanga](https://remanga.org/). Собранные алиасы добавляются в файл _Collection.txt_ в порядке убывания даты публикации.

> [!IMPORTANT]  
> Такие фильтры, как _**page**_ и _**ordering**_ зарезервированы сборщиком и не могут быть использованы.

**Список специфических флагов:**
* _**-f**_ – удаляет содержимое файла коллекции перед записью.

**Список специфических ключей:**
* _**--filters**_ – задаёт набор фильтров из адресной строки, разделённых амперсантом `&` и заключённых в кавычки `"`.
___
```
convert [TARGET*] [SOURCE_FORMAT*] [OUTPUT_FORMAT*]
```
Преобразует внутреннюю структуру JSON файлов определений тайтлов согласно одному из поддерживаемых форматов: [DMP-V1](Examples/DMP-V1.md), [HTCRN-V1](Examples/HTCRN-V1.md), [HTMP-V1](Examples/HTMP-V1.md), [RN-V1](Examples/RN-V1.md).

**Описание позиций:**
* **TARGET** – цель для конвертирования. Обязательная позиция.
	* Аргумент – имя файла. Можно указывать как с расширением, так и без него.
	* Флаги:
		* _**-all**_ – указывает, что необходимо конвертировать все локальные файлы JSON.
* **SOURCE_FORMAT** – исходный формат. Обязательная позиция.
	* Аргумент – название формата из [списка](Examples/) в любом регистре.
* **OUTPUT_FORMAT** – целевой формат. Обязательная позиция.
	* Аргумент – название формата из [списка](Examples/) в любом регистре.
	* Флаги:
		* _**-auto**_ – берёт название формата из ключа `fromat` внутри описательного файла JSON.
___
```
getcov [MANGA_SLUG*] [FLAGS]
```
Загружает обложки конкретного тайтла, алиас которого передан в качестве аргумента.

**Список специфических флагов:**
* _**-f**_ – включает перезапись уже загруженных обложек.
___
```
manage [FORMAT*] [RULE*]
```
Удаляет или перемещает файлы JSON, формат которых отличается от заданного.

**Описание позиций:**
* **FORMAT** – целевой формат, которому должны принадлежать файлы, остающиеся в директории тайтлов.
	* Аргумент – название формата из [списка](Examples/) в любом регистре.
* **RULE** – правило обработки файлов, не соответствующих заданному формату.
	* Флаги:
		* _**-del**_ – указывает, что файлы JSON, формат которых отличается от заданного, необходимо удалить.
	* Ключи:
		* _**--move**_ – указывает, что файлы JSON, формат которых отличается от заданного, необходимо переместить в указанную директорию.
___
```
parse [TARGET*] [FLAGS] [KEYS]
```
Проводит парсинг тайтла с указанным алиасом в JSON формат и загружает его обложки. В случае, если файл тайтла уже существует, дополнит его новыми данными. 

**Описание позиций:**
* **TARGET** – задаёт цель для парсинга. Обязательная позиция. Может принимать следующие значения:
	* Аргумент – алиас тайтла для парсинга.
	* Флаги:
		* _**-collection**_ – указывает, что список тайтлов для парсинга необходимо взять из файла _Collection.txt_.

**Список специфических флагов:**
* _**-f**_ – включает перезапись уже загруженных обложек и существующих JSON файлов.

**Список специфических ключей:**
* _**--from**_ – указывает алиас тайтла, с момента обнаружения которого в коллекции тайтлов необходимо начать парсинг.
___
```
proxval [FLAGS]
```
Выполняет валидацию всех установленных прокси и выводит результат на экран.

**Список специфических флагов:**
* _**-f**_ – дополнительно производит сортировку прокси внутри файла определений согласно их статусам валидации.
___
```
repair [FILENAME*] [KEYS]
```
Обновляет данные конкретной главы в локальном файле. Имя файла может задаваться как с расширением, так и без него.

**Список специфических ключей:**
* _**--chapter**_ – указывает ID главы, данные которой необходимо обновить.
___
```
update [TARGET*] [MODE] [FLAGS] [KEYS]
```
Проводит парсинг тайтлов, обновлённых за интервал времени, указанный в _Settings.json_.

**Описание позиций:**
* **TARGET** – задаёт цель для обновления. Обязательная позиция. Может принимать следующие значения:
	* Аргумент – алиас обновляемого тайтла.
	* Флаги:
		* _**-local**_ – указывает для обновления все локальные файлы;
		* _**-collection**_ – указывает, что список тайтлов для парсинга необходимо взять из файла _Collection.txt_.
* **MODE** – указывает, какие данные необходимо обновлять. Может принимать следующие значения:
	* Флаги:
		* _**-onlydesc**_ – будет произведено обновление только описательных данных тайтла, не затрагивающее ветви перевода и главы.

**Список специфических флагов:**
* _**-f**_ – включает перезапись уже загруженных обложек и существующих JSON файлов.

**Список специфических ключей:**
* _**--from**_ – указывает алиас тайтла, с момента обнаружения которого в списке обновляемых тайтлов необходимо начать обработку обновлений.

## Неспецифические флаги
Данный тип флагов работает при добавлении к любой команде и выполняет отдельную от оной функцию.
* _**-s**_ – выключает компьютер после завершения работы скрипта.

# Settings.json
```JSON
"authorization-token": ""
```
Токен авторизации аккаунта [Remanga](https://remanga.org/) для доступа к 18+ произведениям. Получить можно из одноимённого поля заголовка GET-запросов на страницах с контентом для взрослых.
___
```JSON
"format": "dmp-v1"
```
Задаёт внутреннюю структуру описательных файлов тайтлов. Поддерживаются следующие форматы: [DMP-V1](Examples/DMP-V1.md), [HTCRN-V1](Examples/HTCRN-V1.md), [HTMP-V1](Examples/HTMP-V1.md), [RN-V1](Examples/RN-V1.md).
___
```JSON
"min-delay": 1
```
Задаёт минимальный интервал в секундах для паузы между GET-запросами к серверу.

Рекомендуемое значение: не менее 1 секунды.
___
```JSON
"max-delay": 3
```
Задаёт максимальный интервал в секундах для паузы между GET-запросами к серверу.

Рекомендуемое значение: не менее 3 секунд.
___
```JSON
"use-proxy": false
```
Указывает, следует ли использовать прокси-сервера.
___
```JSON
"selenium-mode": false
```
Переключает парсер в режим отправки запросов через интерпретатор Java Script в браузере [Google Chrome](https://www.google.com.iq/chrome/). Данный способ использует XHR для получения данных с сайта [Remanga](https://remanga.org/), что помогает обходить защиту от ботов при использовании прокси.
___
```JSON
"check-updates-period": 60
```
Указывает, обновления за какой период времени до запуска скрипта (в минутах) нужно получить.
___
```JSON
"use-id-instead-slug": false
```
При включении данного параметра файлы JSON и директория обложек тайтла будут названы по ID произведения, а не по алиасу. При этом уже существующие данные можно автоматически обновить командой `rp.py update -local`.
___
```JSON
"titles-directory": ""
```
Указывает, куда сохранять JSON-файлы тайтлов. При пустом значении будет создана папка Titles в исполняемой директории скрипта. Рекомендуется оформлять в соответствии с принципами путей в Linux, описанными [здесь](http://cs.mipt.ru/advanced_python/lessons/lab02.html#cd).
___
```JSON
"covers-directory": ""
```
Указывает, куда сохранять обложки тайтлов. При пустом значении будет создана папка _Covers_ в исполняемой директории скрипта. Рекомендуется оформлять в соответствии с принципами путей в Linux, описанными [здесь](http://cs.mipt.ru/advanced_python/lessons/lab02.html#cd).
___
```JSON
"filter-covers": true
```
Переключает режим фильтрации заглушек для тайтлов, не имеющих собственных обложек. В активном состоянии похожие на [шаблоны](Source/Filters/) обложки не будут сохранены и добавлены в JSON.
___
```JSON
"retry-tries": 3
```
Указывает, сколко раз проводить повторные попытки при ошибке выполнения запроса.
___
```JSON
"retry-delay": 15
```
Указывает, через какой промежуток времени (в секундах) провести повторную попытку при ошибке выполнения запроса.
___
```JSON
"debug": false
```
Переключает отображение окна браузера во время выполнения запросов через [Selenium](https://github.com/SeleniumHQ/selenium).

# Proxies.json
```JSON
"selenium-validator": {
	"url": "{IP_CHECKER_URL}",
	"tag": "{IP_CONTAIER_TAG}",
	"properties": {
		"{PROPERTY_NAME}": "{PROPERTY_VALUE}"
	}
}
```
Указывает данные сайта для валидации прокси:
* _url_ – адрес сайта, определяющего IP подключения;
* _tag_ – название HTML-тега, содержащего только IP;
* _properties_ – словарное представление свойств тега для поиска IP при помощи [BeautifulSoup4](https://launchpad.net/beautifulsoup).
___
```JSON
"example": [
	{
		"https": "http://{USER_NAME}:{PASSWORD}@{IP}:{PORT}"
	},
	{
		"https": "{IP}:{PORT}"
	}
]
```
Указывает два примера настройки для публичного и приватного (требующего логин и пароль) прокси-серверов. Не влияет на работу скрипта.

> [!WARNING]  
> Несмотря на использование протокола HTTPS, в описании приватного прокси-сервера необходимо прописывать «_http://_». Это связано с особенностями распознавания настроек прокси в библиотеке [requests](https://github.com/psf/requests).
___
```JSON
"proxies": []
```
Задаёт указанные пользователем прокси-сервера для использования скриптом. При ошибках валидации, проводящейся перед каждым запросом, записи могут быть перемещены в нижеописанные разделы.
___
```JSON
"forbidden-proxies": []
```
Сюда помещаются прокси, вызывающие ошибку 403 или срабатывание капчи Cloudflare при обращении к серверу [Remanga](https://remanga.org/).
___
```JSON
"invalid-proxies": []
```
Сюда помещаются прокси, по той или иной причине не годящиеся для установления стабильной связи с сервером или отказавшие в доступе при валидации.

_Copyright © DUB1401. 2022-2023._
