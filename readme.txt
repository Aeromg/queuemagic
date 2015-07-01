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
	аргумент - тип_значения[, d. значение_по_умолчанию[, a. допустимые_значения]] описание

=== Обработчики ===
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
			'auth': {
				'lambda': lambda x: x.account == 'some'
			}
		},
		'then': {
		    'module': 'dkim'
		},
		'else': {
		    'module': 'chain',
		    'jump': 'others'
		}
	}

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
    template - str имя шаблона визитки
    display - str отображаемое имя файла во вложении
    [encoding] - str, d. 'cp1251' кодировка вложенного файла
    [view_bag] - dict, d. {} начальное состояние вьюбага
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
	[from_name_template] - str, d. None имя шаблона, в соответствии с которым нужно приводить имя отправителя

copy: Копирует письмо
	[destination] - str, d. None имя файла или адрес электронной почты, куда следует записать или отправить копию
	[lambda] - lambda, d. None выражение, динамически определяющее destination

	---

=== Условия ===
	Справка по реализованным
	attrib: modules.pipeline.filters.attributes.Attributes
	auth: modules.pipeline.filters.auth.Auth
	pass: modules.pipeline.filters.bypass.Bypass
	expr: modules.pipeline.filters.expression.Expression
	filter: modules.pipeline.filters.aggregation.Aggregation
	hashtag: modules.pipeline.filters.hashtag.HashTag
	statistics: modules.pipeline.filters.statistics.Statistics

---: Все модули
	[negation] - bool, d. False отрицание результата

attrib: Аттрибуты письма
	[with_referenced] - bool, d. True включить ответы и пересылаемые письма
	[max_size] - int, d. sys.maxint ограничить максимальный размер письма
	[min_size] - int, d. 0 ограничить минимальный размер письма

auth: Аутентификация
	[include_users] - [str], d. [] аккаунт отправителя должен быть в списке
	[exclude_users] - [str], d. [] аккаунт отправителя НЕ должен быть в списке
	[include_member_of] - [str], d. [] группа аккаунта отправителя должна быть в списке
	[exclude_member_of] - [str], d. [] группа аккаунта отправителя НЕ должна быть в списке
	[sender_location] - str, d. 'any', a. ['any', 'internal', 'external'] локальный или внешний отправитель

pass: Заглушка
	[value] - bool, d. True постоянный результат фильтра

expr: Лямбда
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


=== Сервисы ===
	Справка по конкретным
	AuthoritySource: modules.services.authority.fabric.ActiveDirectoryFabric
	Attachments: modules.services.attachments.fabric.AttachmentsFabric
	DomainKeysSigner: modules.services.domain_keys.fabric.DomainKeysSignerFabric
	PipelineService: modules.services.pipeline.fabric.PipelineServiceFabric
	Speller: modules.services.speller.yandex_speller_fabric.YandexSpellerFabric
	PersistentDictionary: modules.services.db.shelve_dict_fabric.ShelveDictFabric
	Statistics: modules.services.statistics.fabric.StatisticsFabric

Attachments: Добавляет, удаляет и изменяет вложения.
	path - str путь к хранилищу

AuthoritySource: Находит сведения о человеке
	dc - str контроллер домена
	user - str имя пользователя
	password - str пароль
	catalog - str начальный OU для поиска
	wildcard_mail_field - str поле схемы ***???
	extra_fields - [str] "демультиплексируемые" поля
	local_domains - [str] локальные домены
	extra_fields_source - str "замультиплексированное" поле в схеме лдап
	[cache] - <section>, d. None секция кэш-сервиса

Cache: Key-serialized object с быстрым поиском по ключу
	prefix - str префикс файлов
	path - str директория
	ttl - int время жизни в секундах

PersistentDictionary: Key-serialized object с быстрым доступом к данным, column-ориентированная база
	file - str файл berkley-db

DomainKeysSigner: Создает и проверяет ключи DKIM
	domains
	...?

Logs: Логи

TextFactory: Шаблоны

PipelineService: Конвейеры

ModulesResolver: Сервис-локатор прикладных модулей

Speller: Спеллчекер

PersistentDictionary: Key-Value база данных

Statistics: Статистика

SendMail: Отправка почты


=== Разработка ===

=== Добавление нового модуля условия ===

modules.pipelines.filters._skel.SkeletonFilter - скелетон
1. Скопировать.
2. Сменить имя класса.
3. Описать логику.
4. Прописать путь до класса в конфиге по адресу modules.filters.<имя_модуля>.


=== Добавление нового модуля обработчика ===

modules.pipelines.stages._skel.SkeletonStage - скелетон
1. Скопировать.
2. Сменить имя класса.
3. Описать логику.
4. Прописать путь до класса в конфиге по адресу modules.stages.<имя_модуля>.


=== Добавление нового сервиса ===

services.base._skel.SkeletonService - скелетон
1. Скопировать.
2. Сменить имя класса.
3. Объявить методы. В теле методов оставить raise Exception('Method must be overridden'). Здесь так принято.
4. Реализовать сервис


=== Добавление новой реализации сервиса ===

services.base.* - интерфейсы сервисов
services.service_fabric.ServiceFabric - абстрактная фабрика
1. Реализовать выбранный интерфейс.
2. Реализовать фабрику.
3.1 Прописать/переписать в конфиге services.<имя_интерфейса_сервиса>.fabric путь до класса фабрики.
3.2 Прописать/переписать в конфиге services.<имя_интерфейса_сервиса>.config секцию конфигурации сервиса.