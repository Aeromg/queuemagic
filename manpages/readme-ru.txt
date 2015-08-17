== Конфигурационный словарь ==
Представляет из себя обычный питоновый dict. Соответственно, можно использовать все возможности языка.

# userconfig.py
config = {
}

== Объединение конфигураций ==
Словарь используется для инициализации ConfigProvider.
Декларируемый ConfigProvider метод insert позволяет вставлять словарь с указанным приоритетом.
Получение значения конфигурации происходит с учетом приоритетов: значение из словаря, имевшего больший приоритет
перекрывает значение из словаря, имевшего меньший приоритет.

== Модули ==
Модули двух видов: сервисные и прикладные. Прикладные делятся на обработчики и условия.
Сервисные - низкоуровневые вещи. Редко нуждаются в изменениях. Используются модулями, через RPC, из командной строки
или в виде подключаемого модуля в стороннем приложении.
Прикладные - высокоуровневые вещи. Используются непосредственно в конвейерах.

== Конфигурирование модулей ==
В двух сущностях ServiceResolver и ModulesResolver реализован шаблон ServiceLocator. Их настройка выполняется
в секциях services и modules, расположенных в корне конфигурационного дерева.

{
	'services': {
		ИмяИнтерфейсаСервиса: {
	            'fabric': модуль.фабрики.включая.КлассФабрики,
	            'config': конфигурационный_словарь
		}, 
		...
	}
	'modules': {
		'stages': {
			имя_обработчика: модуль.обработчика.включая.КлассОбработчика,
			...
		},
		'filters' {
			имя_фильтра: модуль.фильтра.включая.КлассФильтра,
			...
		}
	}
}

== Ссылки в конфигурации ==
В значениях можно ссылаться на другие значения и использовать шаблоны.

{
	'app': {
		'name': 'QueueMagic',
		'description': 'Extended routing policies for postfix mta'
	},
	'appinfo': '{{app.name}}: {{app.description}}',	# шаблон 'QueueMagic: Extended routing policies for postfix mta'
	'sections': {
		'subsection': {
			'value': 1
		}
	},
	'value': '{{sections.subsection.value}}',			# копия значения внутри другой секции
	'subsection': '{{sections.subsection}}',			# ссылка на секцию
	'value_over_subsection': {{subsection_copy.value}},	# копия значения внутри другой секции
	'subsection_copy': {{sections}}				# ссылка на секцию
}

Реальный пример:
{
	'services': {
		'PipelineService': {
	            'fabric': 'modules.services.pipeline.fabric.PipelineServiceFabric',
	            'config': '{{pipelines}}'
		}, 
		...
	},
	'pipelines': {
		'empty': { 'modules': [] }
		'test': {...}
	}
}


== Формат справки ==
имя_модуля: Описание
	аргумент - тип_значения[+busvariable][, d. значение_по_умолчанию[, a. допустимые_значения]] описание

busvariable - использовать значение как шаблон и данные шины в виде "{ключ}"

== Конвейеры ==
Формат секции:

{
	'имя_конвейера': {
		'stages': {
			'имя_обработчика_1': секция_обработчика_1,
			...
			'имя_обработчика_n': секция_обработчика_n
		},
		'queue': [
			'имя_обработчика_1',
			...
			'имя_обработчика_n'
		],
		параметры
	}
}

stages - [section] секции этапов
queue - [str] очередность этапов

Параметры конвейера:
	[error] - str, d. continue, a. ['continue', 'rollback', 'drop', 'raise'] политика обработки ошибок в модулях
	[filter] - section секция условия ("aggregation" filter module)


== Обработчики ==
	Справка по реализованным
	chain: modules.pipeline.stages.chain.Chain
	disclaimer: modules.pipeline.stages.disclaimer.Disclaimer
	dkim: modules.pipeline.stages.dkim.DKIM
	remove_hashtag: modules.pipeline.stages.remove_hashtag.RemoveHashTag
	logo_inject: modules.pipeline.stages.logo_inject.LogoInject
	vcard_inject: modules.pipeline.stages.vcard_inject.VcardInject
	isolator: modules.pipeline.stages.isolator.Isolator
	beautifulizer: modules.pipeline.stages.beautifulizer.Beautifulizer
	copy: modules.pipeline.stages.copy.Copy
	switch: modules.pipeline.stages.switch.Switch
	break: modules.pipeline.stages.break.Break
	header: modules.pipeline.stages.header_inject.HeaderInject
	bus_interact: modules.pipeline.stages.bus_interact.BusInteract
	subprocess: modules.pipeline.stages.subprocess.SubProcess

---: Все модули
	[module] - str, d. <имя_обработчика> имя модуля обработчика
	[filter] - section секция условия ("aggregation" filter module)
	[async] - bool, d. False разрешить асинхронный запуск, если это может увеличить производительность

subprocess: Скармливает SMTP-message процессу
	exec - str вызываемый процесс
	[args] - [str], d. [] аргументы
	[ignore_output] - bool, d. False не искать в stdout процесса SMTP сообщение
	[async_id] - str, d. None идентификатор процесса при асинхронном вызове. Включает собой ignore_output

chain: Переводит выполнение в другой конвейер
	jump - str имя конвейера, куда нужно прыгнуть
	[resume] - bool, d. True продолжить ли выполнение текущего конвейера

	пример секции:
	'chain': {
		'module': 'chain',
		'jump': 'first_time',
		'resume': False
		'filter': {
			'statistics': {
				'first_time': True
			}
		}
	}

switch: Выполняет один из двух обработчиков, в зависимости от определяющего условия
	if - section секция условия
	then - section секция обработчика, если условие пройдено
	else - section секция обработчика, если условие провалено

	пример секции:
	'delivery_preroute': {
		'module': 'switch',
		'if': {
			'identity': {
				''
			}
		}
	}

break: Прерывает выполнение текущего конвейера
	---

bus_interact: Взаимодействует данными на шине конвейера
	[arg_1] - object|lambda устанавливаемое на шине значение с произвольным индексом arg_1
	...
	[arg_N] - object|lambda устанавливаемое на шине значение с произвольным индексом arg_N

header: Добавляет или изменяет mime-заголовок
	name - str имя заголовка
	value - str значение заголовка
	[allow_replace] - bool, d. True разрешено ли заменять имеющийся заголовок

disclaimer: Добавляет подпись в тело письма
	html - str имя шаблона для html-версии тела письма
	plain - str имя шаблона для текстовой версии тела письма
	[view_bag] - dict, d. {} начальное состояние вьюбага

dkim: Добавляет/обновляет подпись domain keys
	[remove] - bool, d. False удалить подпись

remove_hashtag: Удаляет хэштеги
	[locations] - [str], d. ['subject'], a. ['subject', 'body'] где искать теги
	[tags] - [unicode], d. [] какие искать теги. Пусто - любые теги

logo_inject: Добавляет лого
	[optional] - bool, d. False не ломаться если не смогли ничего вставить
	[default] - str, d. None имя, путь или URL до файла по-умолчанию
	[user_def] - str, d. None имя поля в записи аутентификации, где искать пользовательскую картинку
	[display] - str, d. None как назвать файл в аттачменте
	id - str идентификатор вложения

vcard_inject: Добавляет vcard
	---

isolator: Убирает лишних получателей письма
	[headers] - [str], d. ['To', 'Cc', 'Bcc'] модифицируемые списки получателей
	[undisclosed] - bool, d. False заменять получателя на "undisclosed-recipients:;"

beautifulizer: Наводит порядок в письме
	[locations] - [str], d. ['subject', 'body'], a. ['subject', 'body'] где модифицировать текст
	[remove_long_spaces] - bool, d. False убирать лишние пробелы
	[remove_long_newline] - bool, d. False убирать лишние переносы строк
	[remove_html] - bool, d. False убирать html-форматирование
	[allowed_html_tags] - [str], d. [] разрешенные html теги, включает собой remove_html
	[restore_punctuation] - bool, d. False трогать пунктуацию
	[sender_name_rewrite] - lambda, d. None выражение, определяющее новое имя отправителя
	[sender_address_rewrite] - lambda, d. None выражение, определяющее новый адрес отправителя

copy: Копирует письмо
	[destination] - str, d. None имя файла или адрес электронной почты, куда следует записать или отправить копию
	[lambda] - lambda, d. None выражение, динамически определяющее destination

	---

== Условия ==
	Справка по реализованным
	attrib: modules.pipeline.filters.attributes.Attributes
	identity: modules.pipeline.filters.identity.identity
	pass: modules.pipeline.filters.bypass.Bypass
	expr: modules.pipeline.filters.expression.Expression
	filter: modules.pipeline.filters.aggregation.Aggregation
	hashtag: modules.pipeline.filters.hashtag.HashTag
	statistics: modules.pipeline.filters.statistics.Statistics
	header: modules.pipeline.filters.header.Header
	stage: modules.pipeline.filters.stage.Stage
	subprocess: modules.pipeline.filters.subprocess.SubProcessFilter
	bus_data: modules.pipeline.filters.bus_data.BusData

---: Все модули
	[negation] - bool, d. False отрицание результата
	[async] - bool, d. False разрешить асинхронный запуск, если это может увеличить производительность

bus_data: Проверка данных на шине
	lambda - lambda выражение, передается аргумент-коллекция bus.data

stage: Результат выполнения этапа
	stage - имя этапа
	result_in - [str], a. ['pass', 'skip', 'fail'] допустимый результат

attrib: Аттрибуты письма
	[with_referenced] - bool, d. True включить ответы и пересылаемые письма
	[max_size] - int, d. sys.maxint ограничить максимальный размер письма
	[min_size] - int, d. 0 ограничить минимальный размер письма

identity: Аутентификация
	[include_users] - [str], d. [] аккаунт отправителя должен быть в списке
	[exclude_users] - [str], d. [] аккаунт отправителя НЕ должен быть в списке
	[include_member_of] - [str], d. [] группа аккаунта отправителя должна быть в списке
	[exclude_member_of] - [str], d. [] группа аккаунта отправителя НЕ должна быть в списке
	[sender_location] - str, d. 'any', a. ['any', 'internal', 'external'] локальный или внешний отправитель

subprocess: Результат выполнения внешнего процесса
	exec - str вызываемый процесс
	[args] - [str], d. [] аргументы
	[output_pattern] - str, d. None регулярное выражение на stdout субпроцесса
	[exit_code_in] - [int], d. [] допустимые коды возврата

subprocess_async: Результат выполнения асинхронного процесса
	async_id - str идентификатор процесса выполняемого асинхронно
	[output_pattern] - str, d. None регулярное выражение на stdout субпроцесса
	[exit_code_in] - [int], d. [] допустимые коды возврата

pass: Заглушка
	[value] - bool, d. True постоянный результат фильтра

expr: Выражение
	lambda - lambda выполняемое выражение
	[error] - str, d. 'fail', a. ['fail', 'pass', 'raise'] результат фильтра в случае сбоя

filter: Вложенный фильтр
	[aggregate] - str, d. 'all', a. ['all', 'any'] успешно прохождение одного или всех фильтров

hashtag: Хэштеги
	[tags] - [unicode, str], d. [] теги к поиску
	[take] - str, d. 'any', a. ['all', 'any', 'one'] успешно нахождение всех, любого или строго одного тега
	[locations] - [str], d. ['subject'], a. ['subject', 'body'] где искать теги

statistics: Статистика
	[first_time] - bool, d. False отправитель пишет письмо получателю впервые
	[antiquity] - int, d. sys.maxint отправитель писал предыдущее письмо получателю не ранее n секунд назад
	[aggregate] - str, d. 'any', a. ['all', 'any'] успех, когда одно или все условия выполнены

header: Заголовок
	name - str имя заголовка
	pattern - str регулярное выражение, которому должно соответствовать содержимое заголовка
	[miss_ok] - bool, d. False выполняемость условия при не существующем заголовке


== Сервисы ==
	Справка по конкретным
	IdentificationSource: modules.services.identification.fabric.ActiveDirectoryFabric
	Attachments: modules.services.attachments.fabric.AttachmentsFabric
	DomainKeysSigner: modules.services.domain_keys.fabric.DomainKeysSignerFabric
	PipelineService: modules.services.pipeline.fabric.PipelineServiceFabric
	Speller: modules.services.speller.yandex_speller_fabric.YandexSpellerFabric
	PersistentDictionary: modules.services.db.shelve_dict_fabric.ShelveDictFabric
	Statistics: modules.services.statistics.fabric.StatisticsFabric

Attachments: Добавляет, удаляет и изменяет вложения.
	path - str путь к хранилищу

IdentificationSource: Находит сведения о человеке
	dc - str контроллер домена
	user - str имя пользователя
	password - str пароль
	catalog - str начальный OU для поиска
	wildcard_mail_field - str поле схемы ***???
	extra_fields - [str] "демультиплексируемые" поля
	local_domains - [str] локальные домены
	extra_fields_source - str "замультиплексированное" поле в схеме лдап
	[cache] - <section>, d. None секция кэш-сервиса

Cache: Key->serialized object с быстрым поиском по ключу
	prefix - str префикс файлов
	path - str директория
	ttl - int время жизни в секундах

PersistentDictionary: Key->serialized object с быстрым доступом к данным, column-ориентированная база
	file - str файл базы

DomainKeysSigner: Создает и проверяет ключи DKIM
	headers - [str] заголовки письма для подписи
	selector - str селектор
	default_domain - dict шаблон для всех доменов
		[enabled] - bool, d. False разрешить применение шаблона к неизвестным доменам
		private_key - str+busvariable путь к закрытому ключу
		[selector] - str, d. None селектор, по умолчанию равен основному селектору
	domains - [dict] домены
		name - str домен
		private_key - str+busvariable путь к закрытому ключу, гду {domain} - имя домена
	ToDo:...

Logs: Логи

TextFactory: Шаблоны

PipelineService: Конвейеры

ModulesResolver: Сервис-локатор прикладных модулей


Speller: Спеллчекер

PersistentDictionary: Key-Value база данных

Statistics: Статистика

SendMail: Отправка почты


== Разработка ==

== Добавление нового модуля условия ==

modules.pipelines.filters._skel.SkeletonFilter - скелетон
1. Скопировать.
2. Сменить имя класса.
3. Описать логику.
4. Прописать путь до класса в конфиге по адресу modules.filters.<имя_модуля>.


== Добавление нового модуля обработчика ==

modules.pipelines.stages._skel.SkeletonStage - скелетон
1. Скопировать.
2. Сменить имя класса.
3. Описать логику.
4. Прописать путь до класса в конфиге по адресу modules.stages.<имя_модуля>.


== Добавление нового сервиса ==

services.base._skel.SkeletonService - скелетон
1. Скопировать.
2. Сменить имя класса.
3. Объявить методы. В теле методов оставить raise Exception('Method must be overridden'). Здесь так принято.
4. Реализовать сервис


== Добавление новой реализации сервиса ==

services.base.* - интерфейсы сервисов
services.service_fabric.ServiceFabric - абстрактная фабрика
1. Реализовать выбранный интерфейс.
2. Реализовать фабрику.
3.1 Прописать/переписать в конфиге services.<имя_интерфейса_сервиса>.fabric путь до класса фабрики.
3.2 Прописать/переписать в конфиге services.<имя_интерфейса_сервиса>.config секцию конфигурации сервиса.