from Source.Core.Formats.Manga import BaseStructs, Manga, Statuses, Types
from Source.Core.ParserSettings import ParserSettings
from Source.Core.Downloader import Downloader
from Source.Core.Objects import Objects
from Source.Core.Exceptions import *
from Source.CLI.Templates import *

from dublib.WebRequestor import Protocols, WebConfig, WebLibs, WebRequestor
from dublib.Methods.Data import RemoveRecurringSubstrings, Zerotify
from skimage.metrics import structural_similarity
from dublib.Methods.JSON import ReadJSON
from dublib.Polyglot import HTML
from skimage import io
from time import sleep

import cv2
import os

#==========================================================================================#
# >>>>> ОПРЕДЕЛЕНИЯ <<<<< #
#==========================================================================================#

VERSION = "2.0.0"
NAME = "remanga"
SITE = "remanga.org"
STRUCT = Manga()

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Parser:
	"""Модульный парсер."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

	@property
	def site(self) -> str:
		"""Домен целевого сайта."""

		return self.__Title["site"]

	@property
	def id(self) -> int:
		"""Целочисленный идентификатор."""

		return self.__Title["id"]

	@property
	def slug(self) -> str:
		"""Алиас."""

		return self.__Title["slug"]

	@property
	def content_language(self) -> str | None:
		"""Код языка контента по стандарту ISO 639-3."""

		return self.__Title["content_language"]

	@property
	def localized_name(self) -> str | None:
		"""Локализованное название."""

		return self.__Title["localized_name"]

	@property
	def en_name(self) -> str | None:
		"""Название на английском."""

		return self.__Title["en_name"]

	@property
	def another_names(self) -> list[str]:
		"""Список альтернативных названий."""

		return self.__Title["another_names"]

	@property
	def covers(self) -> list[dict]:
		"""Список описаний обложки."""

		return self.__Title["covers"]

	@property
	def authors(self) -> list[str]:
		"""Список авторов."""

		return self.__Title["authors"]

	@property
	def publication_year(self) -> int | None:
		"""Год публикации."""

		return self.__Title["publication_year"]

	@property
	def description(self) -> str | None:
		"""Описание."""

		return self.__Title["description"]

	@property
	def age_limit(self) -> int | None:
		"""Возрастное ограничение."""

		return self.__Title["age_limit"]

	@property
	def genres(self) -> list[str]:
		"""Список жанров."""

		return self.__Title["genres"]

	@property
	def tags(self) -> list[str]:
		"""Список тегов."""

		return self.__Title["tags"]

	@property
	def franchises(self) -> list[str]:
		"""Список франшиз."""

		return self.__Title["franchises"]

	@property
	def type(self) -> Types | None:
		"""Тип тайтла."""

		return self.__Title["type"]

	@property
	def status(self) -> Statuses | None:
		"""Статус тайтла."""

		return self.__Title["status"]

	@property
	def is_licensed(self) -> bool | None:
		"""Состояние: лицензирован ли тайтл на данном ресурсе."""

		return self.__Title["is_licensed"]

	@property
	def content(self) -> dict:
		"""Содержимое тайтла."""

		return self.__Title["content"]

	#==========================================================================================#
	# >>>>> СТАНДАРТНЫЕ ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CalculateEmptyChapters(self, content: dict) -> int:
		"""Подсчитывает количество глав без слайдов."""

		# Количество глав.
		ChaptersCount = 0

		# Для каждой ветви.
		for BranchID in content.keys():

			# Для каждой главы.
			for Chapter in content[BranchID]:
				# Если глава не содержит слайдов, подсчитать её.
				if not Chapter["slides"]: ChaptersCount += 1

		return ChaptersCount

	def __InitializeRequestor(self) -> WebRequestor:
		"""Инициализирует модуль WEB-запросов."""

		# Инициализация и настройка объекта.
		Config = WebConfig()
		Config.select_lib(WebLibs.requests)
		Config.set_tries_count(self.__Settings.common.tries)
		Config.add_header("Authorization", self.__Settings.custom["token"])
		WebRequestorObject = WebRequestor(Config)

		# Установка прокси.
		if self.__Settings.proxy.enable: WebRequestorObject.add_proxy(
			Protocols.HTTPS,
			host = self.__Settings.proxy.host,
			port = self.__Settings.proxy.port,
			login = self.__Settings.proxy.login,
			password = self.__Settings.proxy.password
		)

		return WebRequestorObject
	
	def __InitializeCoversRequestor(self) -> WebRequestor:
		"""Инициализирует модуль WEB-запросов обложек."""

		# Инициализация и настройка объекта.
		Config = WebConfig()
		Config.select_lib(WebLibs.requests)
		Config.set_tries_count(self.__Settings.common.tries)
		Config.requests.enable_proxy_protocol_switching(True)
		Config.add_header("Referer", f"https://{SITE}/")
		WebRequestorObject = WebRequestor(Config)

		# Установка прокси.
		if self.__Settings.proxy.enable: WebRequestorObject.add_proxy(
			Protocols.HTTP,
			host = self.__Settings.proxy.host,
			port = self.__Settings.proxy.port,
			login = self.__Settings.proxy.login,
			password = self.__Settings.proxy.password
		)

		return WebRequestorObject

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CheckForStubs(self, url: str) -> bool:
		"""
		Проверяет, является ли обложка заглушкой.
			url – ссылка на обложку.
		"""

		# Список индексов фильтров.
		FiltersDirectories = os.listdir(f"Parsers/{NAME}/Filters")

		# Для каждого фильтра.
		for FilterIndex in FiltersDirectories:
			# Список щаблонов.
			Patterns = os.listdir(f"Parsers/{NAME}/Filters/{FilterIndex}")
			
			# Для каждого фильтра.
			for Pattern in Patterns:
				# Сравнение изображений.
				Result = self.__CompareImages(f"Parsers/{NAME}/Filters/{FilterIndex}/{Pattern}")
				# Если разница между обложкой и шаблоном составляет менее 50%.
				if Result != None and Result < 50.0: return True
		
		return False

	def __CompareImages(self, pattern_path: str) -> float | None:
		"""
		Сравнивает изображение с фильтром.
			url – ссылка на обложку;\n
			pattern_path – путь к шаблону.
		"""

		# Процент отличия.
		Differences = None

		try:
			# Получение пути к каталогу временных файлов.
			Temp = self.__SystemObjects.temper.get_parser_temp(NAME)
			# Чтение изображений.
			Pattern = io.imread(f"{Temp}cover")
			Image = cv2.imread(pattern_path)
			# Преобразование изображений в чёрно-белый формат.
			Pattern = cv2.cvtColor(Pattern, cv2.COLOR_BGR2GRAY)
			Image = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY)
			# Получение разрешений изображений.
			PatternHeight, PatternWidth = Pattern.shape
			ImageHeight, ImageWidth = Image.shape
		
			# Если шаблон и изображение имеют одинаковое разрешение.
			if PatternHeight == ImageHeight and PatternWidth == ImageWidth:
				# Сравнение двух изображений.
				(Similarity, Differences) = structural_similarity(Pattern, Image, full = True)
				# Конвертирование в проценты.
				Differences = 100.0 - (float(Similarity) * 100.0)

		except Exception as ExceptionData:
			# Запись в лог ошибки: исключение.
			self.__SystemObjects.logger.error("Problem occurred during filtering stubs: \"" + str(ExceptionData) + "\".")		
			# Обнуление процента отличий.
			Differences = None

		return Differences

	def __GetAgeLimit(self, data: dict) -> int:
		"""
		Получает возрастной рейтинг.
			data – словарь данных тайтла.
		"""

		# Определения возрастных ограничений.
		Ratings = {
			0: 0,
			1: 16,
			2: 18
		}
		# Возрастной рейтинг.
		Rating = Ratings[data["age_limit"]]

		return Rating 

	def __GetContent(self, data: str) -> dict:
		"""Получает содержимое тайтла."""

		# Структура содержимого.
		Content = dict()

		# Для каждой ветви.
		for Branch in data["branches"]:
			# ID ветви и количество глав.
			BranchID = Branch["id"]
			ChaptersCount = Branch["count_chapters"]

			# Для каждой страницы ветви.
			for BranchPage in range(0, int(ChaptersCount / 100) + 1):
				# Выполнение запроса.
				Response = self.__Requestor.get(f"https://api.remanga.org/api/titles/chapters/?branch_id={BranchID}&count=100&ordering=-index&page=" + str(BranchPage + 1) + "&user_data=1")

				# Если запрос успешен.
				if Response.status_code == 200:
					# Парсинг данных в JSON.
					Data = Response.json["content"]
					
					# Для каждой главы.
					for Chapter in Data:
						# Если ветвь не существует, создать её.
						if str(BranchID) not in Content.keys(): Content[str(BranchID)] = list()
						# Переводчики.
						Translators = [sub["name"] for sub in Chapter["publishers"]]
						# Буфер главы.
						Buffer = {
							"id": Chapter["id"],
							"volume": str(Chapter["tome"]),
							"number": Chapter["chapter"],
							"name": Zerotify(Chapter["name"]),
							"is_paid": Chapter["is_paid"],
							"free-publication-date": None,
							"translators": Translators,
							"slides": []	
						}

						# Если включено добавление времени бесплатного времени публикации.
						if self.__Settings.custom["add_free_publication_date"]:
							# Если глава платная, записать время публикации.
							if Buffer["is_paid"]: Buffer["free-publication-date"] = Chapter["pub_date"]

						else:
							# Удаление ключа. 
							del Buffer["free-publication-date"]

						# Запись главы.
						Content[str(BranchID)].append(Buffer)

				else:
					# Запись в лог ошибки.
					self.__SystemObjects.logger.request_error(Response, "Unable to request chapter.")

		return Content			

	def __GetCovers(self, data: dict) -> list[str]:
		"""Получает список обложек."""

		# Список обложек.
		Covers = list()

		# Для каждой обложки.
		for CoverURI in data["img"].values():

			# Если обложка имеет правильный URI.
			if CoverURI not in ["/media/None"]:
				# Буфер.
				Buffer = {
					"link": f"https://{SITE}{CoverURI}",
					"filename": CoverURI.split("/")[-1]
				}

				# Если включен режим получения размеров обложек.
				if self.__Settings.common.sizing_images:
					# Дополнение структуры размерами.
					Buffer["width"] = None
					Buffer["height"] = None

				# Дополнение структуры.
				Covers.append(Buffer)

				# Если включена фильтрация заглушек.
				if self.__Settings.custom["unstub"]:
					# Скачивание обложки.
					Downloader(self.__SystemObjects, self.__CoversRequestor).image(
						url = Buffer["link"],
						directory = self.__SystemObjects.temper.get_parser_temp(NAME),
						filename = "cover",
						is_full_filename = True,
						referer = SITE
					)
					
					# Если обложка является заглушкой.
					if self.__CheckForStubs(Buffer["link"]):
						# Очистка данных обложек.
						Covers = list()
						# Запись в лог информации обложки помечены как заглушки.
						self.__SystemObjects.logger.covers_unstubbed(self.__Slug, self.__Title["id"])
						# Прерывание цикла.
						break

		return Covers

	def __GetDescription(self, data: dict) -> str | None:
		"""
		Получает описание.
			data – словарь данных тайтла.
		"""

		# Описание.
		Description = None
		# Удаление тегов и спецсимволов HTML. 
		Description = HTML(data["description"]).plain_text
		# Удаление ненужных символов.
		Description = Description.replace("\r", "").replace("\xa0", " ").strip()
		# Удаление повторяющихся символов новой строки.
		Description = RemoveRecurringSubstrings(Description, "\n")
		# Обнуление пустого описания.
		Description = Zerotify(Description)

		return Description

	def __GetGenres(self, data: dict) -> list[str]:
		"""
		Получает список жанров.
			data – словарь данных тайтла.
		"""

		# Описание.
		Genres = list()
		# Для каждого жанра записать имя.
		for Genre in data["genres"]: Genres.append(Genre["name"])

		return Genres

	def __GetSlides(self, chapter_id: int) -> list[dict]:
		"""
		Получает данные о слайдах главы.
			chapter_id – идентификатор главы.
		"""

		# Список слайдов.
		Slides = list()
		# Выполнение запроса.
		Response = self.__Requestor.get(f"https://api.remanga.org/api/titles/chapters/{chapter_id}")

		# Если запрос успешен.
		if Response.status_code == 200:
			# Парсинг данных в JSON.
			Data = Response.json["content"]
			# Объединение групп страниц.
			Data["pages"] = self.__MergeListOfLists(Data["pages"])

			# Для каждого слайда.
			for SlideIndex in range(len(Data["pages"])):
				# Буфер слайда.
				Buffer = {
					"index": SlideIndex + 1,
					"link": Data["pages"][SlideIndex]["link"]
				}
				# Состояние: отфильтрован ли слайд.
				IsFiltered = False
				# Если указано настройками, русифицировать ссылку на слайд.
				if self.__Settings.custom["ru_links"]: Buffer["link"] = self.__RusificateLink(Buffer["link"])

				# Если включен режим получения размеров обложек.
				if self.__Settings.common.sizing_images:
					# Дополнение структуры размерами.
					Buffer["width"] = Data["pages"][SlideIndex]["width"]
					Buffer["height"] = Data["pages"][SlideIndex]["height"]

				# Если включена фильтрация узких слайдов и высота меньше требуемой, отфильтровать слайд.
				if self.__Settings.custom["min_height"] and Data["pages"][SlideIndex]["height"] <= self.__Settings.custom["min_height"]: IsFiltered = True
				# Если слайд не отфильтрован, записать его.
				if not IsFiltered: Slides.append(Buffer)

		# Если глава является платной или лицензированной.
		elif Response.status_code in [401, 423]:
			# Запись в лог информации: глава пропущена.
			self.__SystemObjects.logger.chapter_skipped(self.__Slug, self.__Title["id"], chapter_id, True)

		else:
			# Запись в лог ошибки.
			self.__SystemObjects.logger.request_error(Response, "Unable to request chapter content.")

		return Slides

	def __GetStatus(self, data: dict) -> str:
		"""
		Получает статус.
			data – словарь данных тайтла.
		"""

		# Статус тайтла.
		Status = None
		# Статусы тайтлов.
		StatusesDetermination = {
			"Продолжается": Statuses.ongoing,
			"Закончен": Statuses.completed,
			"Анонс": Statuses.announced,
			"Заморожен": Statuses.dropped,
			"Нет переводчика": Statuses.dropped,
			"Не переводится (лицензировано)": Statuses.dropped
		}
		# Индекс статуса на сайте.
		SiteStatusIndex = data["status"]["name"]
		# Если индекс статуса валиден, преобразовать его в поддерживаемый статус.
		if SiteStatusIndex in StatusesDetermination.keys(): Status = StatusesDetermination[SiteStatusIndex]

		return Status

	def __GetTags(self, data: dict) -> list[str]:
		"""
		Получает список тегов.
			data – словарь данных тайтла.
		"""

		# Описание.
		Tags = list()
		# Для каждого тега записать имя.
		for Tag in data["categories"]: Tags.append(Tag["name"])

		return Tags

	def __GetTitleData(self) -> dict | None:
		"""
		Получает данные тайтла.
			slug – алиас.
		"""
		
		# Выполнение запроса.
		Response = self.__Requestor.get(f"https://api.remanga.org/api/titles/{self.__Slug}")
		
		# Если запрос успешен.
		if Response.status_code == 200:
			# Парсинг ответа.
			Response = Response.json["content"]
			# Запись в лог информации: начало парсинга.
			self.__SystemObjects.logger.parsing_start(self.__Slug, Response["id"])

		# Если тайтл не найден.
		elif Response.status_code == 404:
			# Запись в лог ошибки: не удалось найти тайтл в источнике.
			self.__SystemObjects.logger.title_not_found(self.__Slug)
			# Выброс исключения.
			raise TitleNotFound(self.__Slug)

		else:
			# Запись в лог ошибки.
			self.__SystemObjects.logger.request_error(Response, "Unable to request title data.")
			# Обнуление ответа.
			Response = None

		return Response

	def __GetType(self, data: dict) -> str:
		"""
		Получает тип тайтла.
			data – словарь данных тайтла.
		"""

		# Тип тайтла.
		Type = None
		# Типы тайтлов.
		TypesDeterminations = {
			"Манга": Types.manga,
			"Манхва": Types.manhwa,
			"Маньхуа": Types.manhua,
			"Рукомикс": Types.russian_comic,
			"Западный комикс": Types.western_comic,
			"Индонезийский комикс": Types.indonesian_comic
		}
		# Определение с сайта.
		SiteType = data["type"]["name"]
		# Если определение с сайта валидно, преобразовать его.
		if SiteType in TypesDeterminations.keys(): Type = TypesDeterminations[SiteType]

		return Type

	def __MergeListOfLists(self, list_of_lists: list) -> list:
		"""
		Объединяет список списков в один список.
			list_of_lists – список списоков.
		"""
		
		# Если список не пустой и включает списки, то объединить.
		if len(list_of_lists) > 0 and type(list_of_lists[0]) is list:
			# Результат объединения.
			Result = list()
			# Объединить все списки в один список.
			for List in list_of_lists: Result.extend(List)

			return Result

		# Если список включет словари, то вернуть без изменений.
		else: return list_of_lists

	def __RusificateLink(self, link: str) -> str:
		"""
		Задаёт домен российского сервера для ссылки на слайд.
			link – ссылка на слайд.
		"""

		# Если слайд на пятом международном сервере, заменить его.
		if link.startswith("https://img5.reimg.org"): link = link.replace("https://img5.reimg.org", "https://reimg2.org")
		# Замена других серверов.
		link = link.replace("reimg.org", "reimg2.org")

		return link

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, system_objects: Objects, settings: ParserSettings):
		"""
		Модульный парсер.
			system_objects – коллекция системных объектов;\n
			settings – настройки парсера.
		"""

		# Выбор парсера для системы логгирования.
		system_objects.logger.select_parser(NAME)

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Настройки парсера.
		self.__Settings = settings
		# Менеджер WEB-запросов.
		self.__Requestor = self.__InitializeRequestor()
		# Менеджер WEB-запросов обложек.
		self.__CoversRequestor = self.__InitializeCoversRequestor()
		# Структура данных.
		self.__Title = None
		# Алиас тайтла.
		self.__Slug = None
		# Коллекция системных объектов.
		self.__SystemObjects = system_objects

	def amend(self, content: dict | None = None, message: str = "") -> dict:
		"""
		Дополняет каждую главу в кажой ветви информацией о содержимом.
			content – содержимое тайтла для дополнения;\n
			message – сообщение для портов CLI.
		"""

		# Если содержимое не указано, использовать текущее.
		if content == None: content = self.content
		# Подсчёт количества глав для дополнения.
		ChaptersToAmendCount = self.__CalculateEmptyChapters(content)
		# Количество дополненных глав.
		AmendedChaptersCount = 0
		# Индекс прогресса.
		ProgressIndex = 0

		# Для каждой ветви.
		for BranchID in content.keys():
			
			# Для каждый главы.
			for ChapterIndex in range(0, len(content[BranchID])):
				
				# Если слайды не описаны или включён режим перезаписи.
				if content[BranchID][ChapterIndex]["slides"] == []:
					# Инкремент прогресса.
					ProgressIndex += 1
					# Получение списка слайдов главы.
					Slides = self.__GetSlides(content[BranchID][ChapterIndex]["id"])

					# Если получены слайды.
					if Slides:
						# Инкремент количества дополненных глав.
						AmendedChaptersCount += 1
						# Запись информации о слайде.
						content[BranchID][ChapterIndex]["slides"] = Slides
						# Запись в лог информации: глава дополнена.
						self.__SystemObjects.logger.chapter_amended(self.__Slug, self.__Title["id"], content[BranchID][ChapterIndex]["id"], content[BranchID][ChapterIndex]["is_paid"])

					# Вывод в консоль: прогресс дополнения.
					PrintAmendingProgress(message, ProgressIndex, ChaptersToAmendCount)
					# Выжидание интервала.
					sleep(self.__Settings.common.delay)

		# Запись в лог информации: количество дополненных глав.
		self.__SystemObjects.logger.amending_end(self.__Slug, self.__Title["id"], AmendedChaptersCount)

		return content

	def collect(self, filters: str | None = None, pages_count: int | None = None) -> list[str]:
		"""
		Собирает список тайтлов по заданным параметром из каталога источника.
			filters – строка из URI каталога, описывающая параметры запроса;\n
			pages_count – количество запрашиваемых страниц.
		"""

		# Список тайтлов.
		Slugs = list()
		# Состояние: достигнута ли последняя страница католога.
		IsLastPage = False		
		# Текущая страница каталога.
		Page = 1

		# Пока не достигнута последняя страница или не получены все требуемые страницы.
		while not IsLastPage:
			# Выполнение запроса.
			Response = self.__Requestor.get(f"https://api.remanga.org/api/search/catalog/?page={Page}&count=30&ordering=-id&{filters}")
			
			# Если запрос успешен.
			if Response.status_code == 200:
				# Вывод в консоль: прогресс сбора коллекции.
				PrintCollectingStatus(Page)
				# Парсинг ответа.
				PageContent = Response.json["content"]
				# Для каждой записи получить алиас.
				for Note in PageContent: Slugs.append(Note["dir"])

				# Если контента нет или достигнута последняя страница.
				if not PageContent or pages_count and Page == pages_count:
					# Завершение сбора.
					IsLastPage = True
					# Запись в лог информации: количество собранных тайтлов.
					self.__SystemObjects.logger.titles_collected(len(Slugs))

				# Выжидание интервала.
				sleep(self.__Settings.common.delay)
				# Инкремент номера страницы.
				Page += 1

			else:
				# Завершение сбора
				self.__SystemObjects.logger.request_error(Response, "Unable to collect titles.")
				# Выброс исключения.
				raise Exception("Unable to collect titles.")

		return Slugs

	def get_updates(self, hours: int) -> list[str]:
		"""
		Возвращает список алиасов тайтлов, обновлённых на сервере за указанный период времени.
			hours – количество часов, составляющих период для получения обновлений.
		"""

		# Список алиасов.
		Updates = list()
		# Промежуток времени для проверки обновлений (в миллисекундах).
		UpdatesPeriod = hours * 3600000
		# Состояние: достигнут ли конец проверяемого диапазона.
		IsUpdatePeriodOut = False
		# Счётчик страницы.
		Page = 1
		# Количество обновлённых тайтлов.
		UpdatesCount = 0

		# Проверка обновлений за указанный промежуток времени.
		while not IsUpdatePeriodOut:
			# Выполнение запроса.
			Response = self.__Requestor.get(f"https://api.remanga.org/api/titles/last-chapters/?page={Page}&count=20")
			
			# Если запрос успешен.
			if Response.status_code == 200:
				# Парсинг ответа.
				UpdatesPage = Response.json["content"]
				
				# Для каждой записи об обновлении.
				for UpdateNote in UpdatesPage:
					
					# Если запись не выходит за пределы интервала.
					if UpdateNote["upload_date"] < UpdatesPeriod:
						# Сохранение алиаса обновлённого тайтла.
						Updates.append(UpdateNote["dir"])
						# Инкремент обновлённых тайтлов.
						UpdatesCount += 1

					else:
						# Завершение цикла обновления.
						IsUpdatePeriodOut = True

			else:
				# Завершение цикла обновления.
				IsUpdatePeriodOut = True
				# Запись в лог ошибки.
				self.__SystemObjects.logger.request_error(Response, f"Unable to request updates page {Page}.")

			# Если цикл завершён.
			if not IsUpdatePeriodOut:
				# Инкремент страницы.
				Page += 1
				# Выжидание указанного интервала.
				sleep(self.__Settings.common.delay)

		# Запись в лог информации: количество собранных обновлений.
		self.__SystemObjects.logger.updates_collected(len(Updates))

		return Updates

	def parse(self, slug: str, message: str | None = None):
		"""
		Получает основные данные тайтла.
			slug – алиас тайтла, использующийся для идентификации оного в адресе;\n
			message – сообщение для портов CLI.
		"""

		# Преобразование сообщения в строку.
		message = message or ""
		# Заполнение базовых данных.
		self.__Title = BaseStructs().manga
		self.__Slug = slug
		# Вывод в консоль: статус парсинга.
		PrintParsingStatus(message)
		# Получение описания.
		Data = self.__GetTitleData()
		# Занесение данных.
		self.__Title["site"] = SITE
		self.__Title["id"] = Data["id"]
		self.__Title["slug"] = slug
		self.__Title["content_language"] = "rus"
		self.__Title["localized_name"] = Data["main_name"]
		self.__Title["en_name"] = Data["secondary_name"]
		self.__Title["another_names"] = Data["another_name"].split(" / ")
		self.__Title["covers"] = self.__GetCovers(Data)
		self.__Title["authors"] = []
		self.__Title["publication_year"] = Data["issue_year"]
		self.__Title["description"] = self.__GetDescription(Data)
		self.__Title["age_limit"] = self.__GetAgeLimit(Data)
		self.__Title["type"] = self.__GetType(Data)
		self.__Title["status"] = self.__GetStatus(Data)
		self.__Title["is_licensed"] = Data["is_licensed"]
		self.__Title["genres"] = self.__GetGenres(Data)
		self.__Title["tags"] = self.__GetTags(Data)
		self.__Title["franchises"] = []
		self.__Title["content"] = self.__GetContent(Data)

	def repair(self, content: dict, chapter_id: int) -> dict:
		"""
		Заново получает данные слайдов главы главы.
			content – содержимое тайтла;\n
			chapter_id – идентификатор главы.
		"""

		# Для каждой ветви.
		for BranchID in content.keys():
			
			# Для каждый главы.
			for ChapterIndex in range(len(content[BranchID])):
				
				# Если ID совпадает с искомым.
				if content[BranchID][ChapterIndex]["id"] == chapter_id:
					# Получение списка слайдов главы.
					Slides = self.__GetSlides(content[BranchID][ChapterIndex]["id"])
					# Запись в лог информации: глава восстановлена.
					self.__SystemObjects.logger.chapter_repaired(self.__Slug, self.__Title["id"], chapter_id, content[BranchID][ChapterIndex]["is_paid"])
					# Запись восстановленной главы.
					content[BranchID][ChapterIndex]["slides"] = Slides

		return content