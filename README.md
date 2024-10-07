# remanga
**remanga** – это модуль системы управления парсерами [Melon](https://github.com/DUB1401/Melon), включающий поддержку источника: [Remanga](https://remanga.org/).

## Порядок установки и использования
Все парсеры от [@DUB1401](https://github.com/DUB1401) поставляются в Melon по умолчанию. Для повторной загрузки файлов или обновления модуля используйте встроенную команду `install`.

# settings.json
Данный раздел описывает специфичные для этого модуля настройки.
___
```JSON
"token": ""
```
Токен аккаунта [Remanga](https://remanga.org/).
___
```JSON
"ru_links": false
```
Сайт имеет два типа ссылок на слайды: для РФ и для других стран. Данная настройка позволяет выбрать, какой регион вы будете использовать для доступа к контенту.
___
```JSON
"unstub": false
```
Включает фильтрацию заглушек обложек. Дополнительные фильтры по формату можно добавлять в эту [директорию](Filters/).
___
```JSON
"add_free_publication_date": false
```
Указывает, нужно ли в информацию о главе добавлять дату бесплатной публикации.