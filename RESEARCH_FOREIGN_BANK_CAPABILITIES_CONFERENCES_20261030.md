# Зарубежные модели ФБС и научные конференции — разведка для Agentic Economy 2031–2041

**Исследовательская редакция 30.10.2026.** Ключевой вопрос: существуют ли международные подходы, по которым можно отличить **новую банковскую бизнес-способность** от функции, процесса, IT-service, интеграции и агентного сценария? Вторая цель — извлечь строго ограниченный shortlist новых самостоятельных банковских ролей.

**Честная граница:** изучены общедоступные релизные записки, страницы стандартов, оглавления и аннотации научных работ; **не** получен полный закрытый каталог Business Architecture Guild или весь защищённый объектный репозиторий BIAN. Статусы proposed, не BANK_APPROVED. Не переносить зарубежные названия на 639-строчный банковский каталог без юридического / FBS Owner GAP.

## 1. Самый строгий первоисточник: BIAN 14.0, февраль 2026

**BIAN V14.0 Release Notes (официальный документ), стр. 6:** 586 Business Capabilities, 38 Business Domains, **322 Service Domains**, 362 end-to-end Business Scenarios, 242 Semantic APIs, 1 585 Business Objects. Service Domains и Business Capabilities — **разные уровни**; число 322 нельзя автоматически назвать количеством ФБС. **Осторожно:** сторонние GitHub/инструментальные выгрузки утверждают 341 Service Domains; официальные цифры v14.0 расходятся, для этой записки приоритет официальному PDF.

**Стр. 9:** реструктуризация Business Capability Model / Value Streams **ещё не была** завершена в BiZZdesign на момент выпуска v14. Значит, нельзя утверждать, что текущая открытая международная карта уже учитывает все будущие agentic business capabilities.

**Стр. 10: новые Service Domains:** Payee Management, Customer Consent, Payment Orchestration, Payment Confirmation, Payment Settlement; Corporate Card Service; Insurance Claim Assessment, Claim Administration, Funeral Policy; отдельные сервисы партнёрской, reward и incentives инфраструктуры. При этом Payment Instruction, Payment Execution, ACH Operations и Correspondent Bank Operations изменяют жизненный цикл в модели. **Вывод:** отдельный платёжный orchestration или подтверждение — не «уникальная новая ФБС агентной экономики», даже если реализованы AI.

**Стр. 21:** сценарии External Credit Transfer, Direct Debit, Request to Pay и карточного платежа; это **новые сценарии внутри уже описанного банковского мира**, не доказательство новых ФБС.

**Рабочая группа BIAN Business Capability Models:** Capability Model + Value Streams и связь с Service Domains. Формальная семантика в старом пояснении BIAN: **Capability** отвечает стратегии бизнеса; **Service Domain** — стратегии информационных систем; за IT-системами возможно многозначное соответствие с ФБС.

Источники:
- https://bian.org/wp-content/uploads/2026/02/BIAN-v14.0-Release-Notes-v1.0_-Final-Version.pdf (pp. 6, 9, 10, 21)
- https://bian.org/bian-membership/working-groups/
- https://bian.org/servicelandscape-10-0-0/views/view_51768.html
- https://bian.org/servicelandscape-14-0-0/object_16.html?object=48782 (Payment Orchestration)
- https://bian.org/news-room/bian-unveils-new-service-landscape-14-0-to-accelerate-ai-ready-banking-architecture/

## 2. Сравнение международных банковских capability frameworks

| Источник | Что является единицей | Структура и конкретные области | Как использовать в нашем исследовании |
|---|---|---|---|
| **BIAN 14.0** | Business Capability отдельно от Service Domain/Business Scenario/API | 38 business domains; payment, corporate cards, loans, deposits, custody, collateral, risk, compliance, insurance; новые payment orchestration/confirmation/settlement SD | Основной антидубль для банка; нельзя называть API и service domain новой ФБС |
| **Business Architecture Guild — Financial Services Industry Reference Model** | Levelled capability model + value streams + stakeholders/information | Strategic, supporting, core capabilities и end-to-end value streams | Независимая *бизнес-ориентированная* проверка ценности; полный каталог по регистрации/участию |
| **SAP Reference Business Architecture** | Business Domain → Business Area → Business Capability; отдельно Business Processes и Solution Capabilities | 4 enterprise domains: Product/Service, Supply, Customer, Corporate; capability независима от конкретной реализации, связана с процессами и продуктовой архитектурой | Обязательное разделение «новое бизнес-умение» / «как сделать» / «какое ПО реализует» |
| **APQC Banking PCF 7.2.2 (27.03.2025)** | **Процесс**, не Business Capability | Иерархия отраслевых банковских процессов для унификации, benchmarking; разработана совместно с IBM | Контр-проверка того, что новый ФБС — не переписанный процесс; нельзя считать PCF списком ФБС |
| **OTP Group (BIAN case study, 2025–2026)** | Отраслевой blueprint + mapping SD к банковским приложениям | 12 банков в 11 странах; >180 Service Domains сопоставлены в 6 филиальных банках; в 4 legacy core-модулях 77 SD, 23 дублировались | Практическая anti-duplication модель для картирования старых и новых функций |

Первичные ссылки:
- https://learning.businessarchitectureguild.org/products/financial-services-industry-reference-model
- https://www.businessarchitectureguild.org/resource/resmgr/Using_Business_Architecture_.pdf (сопоставление Guild и BIAN)
- https://learning.sap.com/courses/sap-enterprise-architecture-framework-foundation-introduction/discovering-the-reference-architecture-content
- https://www.apqc.org/resource-library/resource-listing/apqc-process-classification-framework-pcf-banking-pcf-pdf-1
- https://bian.org/success-stories/twelve-banks-one-blueprint/

**Не смешивать:** SAP Domain/Area/Capability не равно отраслевому BIAN Business Domain/Capability и не равно APQC Process. Между ними нужна **семантическая карта соответствия**, не механическое совпадение названий.

## 3. Научные конференции с подтверждённой capability-тематикой

| Площадка | Проверенная работа/тема | Почему пригодна |
|---|---|---|
| **FACETE при PoEM 2025** | Foundations and Applications of Capabilities in Enterprises, Transformations and ESG; онтологии, метамодели, эмпирические capability maps | **Самая профильная**: научно определяет критерии появления новой бизнес-способности |
| **FACETE при PoEM 2026** — 1 декабря, Греция (событие **ещё впереди** на 30.10.2026) | Продолжение capability-based management; workshop по методам и практике capability modeling | Проверять новые материалы после появления proceedings; ещё не утверждать итоги будущих докладов |
| **EDOC 2026** — 15–18 сентября, Нидерланды | *Semantic Symmetry in Business Architecture: Demarcating Capability Boundaries with Object Models*; COVO / enterprise ontology | Формально разграничивает способности через объект и право/взаимодействие; применимо к нашим трём кандидатам |
| **CBI 2026** — 15–18 сентября, Нидерланды | *Architectural Patterns and Enabling Capabilities for Agentic AI: A Systematic Literature Review* (Univ. Twente); *AI Compliance in Finance* (Osnabrück/DFKI) | Показывает, что agent registries, orchestration, control, audit — **enabling capabilities** / compliance design, не обязательно новый банковский продукт |
| **CAiSE 2026** — 8–12 июня, Италия | Ontology, conceptual modeling, service- and multi-agent IS, compliance, semantics, value/supply chain | Методика доказательства новых объектов и прав; не объявлять весь поток conference business capability research |
| **BIR 2026** — 7–9 октября, Швейцария | Hybrid Intelligence in Business; business informatics / enterprise models | Дополнительный источник исследовательских гипотез, **менее прямой** для определения границ ФБС |
| **BPM 2026** — Торонто, Канада | Business process management, process mining, choreography | Для negative CJM и разграничения процесса от capability; **не самостоятельное доказательство новой ФБС** |

Ссылки на первичные программы и публикации:
- https://poem2025.unige.ch/home/workshops
- https://poem2026.aegean.gr/workshops/
- https://www.facete.org/
- https://conf.researchr.org/details/cbi-2026/edoc-2026-papers/23/Semantic-Symmetry-in-Business-Architecture-Demarcating-Capability-Boundaries-with-Ob
- https://conf.researchr.org/details/cbi-2026/cbi-2026-papers/2/Architectural-Patterns-and-Enabling-Capabilities-for-Agentic-AI-A-Systematic-Literat
- https://conf.researchr.org/details/cbi-2026/cbi-2026-papers/6/A-Design-Science-Research-Approach-to-AI-Compliance-in-Finance-Building-and-Evaluati
- https://ceur-ws.org/Vol-4171/paper_41.pdf (PoEM 2025: *Semantically Coherent Business Architecture Models: Integrating Capabilities, Value Streams, and Business Objects*)
- https://caise26.polimi.it/?page_id=60
- https://link.springer.com/conference/bir
- https://bpm-conference.org/conferences/

### Наиболее важный научный метод

**COVO — Capability-Object-Value Ontology** связывает (а) способность, (б) бизнес-объект, которым она управляет, (в) stage создания ценности / value commitment. В статье EDOC 2026 *Semantic Symmetry* структурная зависимость объектов должна соответствовать поведенческой зависимости способностей.

**Наша адаптация / INFERENCE:** отдельная новая ФБС должна управлять собственным **устойчивым юридически или экономически значимым объектом**, выдавать отличающийся результат и иметь владельца и ответственность. Если меняется только agentic workflow/технология существующего объекта, это `ENHANCE_EXISTING`.

## 4. Результат применения к трём ранее предложенным новым ФБС

| Кандидат | Собственный бизнес-объект? | Возможный самостоятельный результат | Что уже существует / kill-test | Решение |
|---|---|---|---|---|
| **A. Оператор прав по требованиям независимых компаний** | Потенциально да: *юридически признаваемый статус внешнего денежного требования*, включая держателя, уступки и обременения | Самостоятельный признанный реестр/переход права; доход от участников сети | BIAN custody/collateral, обычный factoring, ABS Trade Finance Registry, MLETR и existing data integrity. Если нет внешнего признания/права — обычный реестр, `NO_NEW_FBS` | **HOLD_NEW_FBS** — только при подтверждённой правовой модели |
| **B. Оператор клиринговой сети агентных B2B-обязательств** | Да, если именно отдельная система: *допущенные требования, чистые обязательства и правила участия* | Правомерно установленные конечные позиции и последствия дефолта; отдельный операторский договор | BIAN Clearing/Settlement уже есть, 7-ФЗ уже регулирует клиринг, ING предоставляет corporate multilateral netting; если это routing/treasury netting — `NO_NEW_FBS` | **STRONGEST CONDITIONAL**, но не новая мировая технология |
| **C. Межплатформенная схема финансовой ответственности агентных сделок** | Потенциально да: *требование о компенсации, распределённая ответственность и согласованные резервы участников* | Правомерная компенсация по внешним межплатформенным правилам; комиссии участников | BIAN Claim Assessment/Administration, карточные chargebacks, страховщики, гарантии и 3.8/4.1.22.2. Если нет самостоятельного соглашения/оператора — `NO_NEW_FBS` | **HOLD_NEW_FBS** — нужен плательщик и правовой предмет |

**Важная корректировка:** официальная BIAN 14.0 уже добавила `Claim Assessment` и `Claim Administration` в страховом контуре, поэтому кандидат C **не должен рекламироваться как «банк впервые рассматривает убытки»**. Только новая нейтральная внешняя схема распределения расходов между сторонами.

## 5. План объективной проверки гипотез, без вымышленного APPROVED

Для каждого кандидата получить ровно пять объектов:

1. **FBS ID / object contract:** предмет способности, владелец, кто получает услугу и один обязательный результат.
2. **BIAN / Guild / российский каталог 639:** явные текущие владельцы и reason «почему нельзя расширить».
3. **Business transaction:** образец реального законного обязательства и отрицательный контрпример (двойная уступка, дефолт в клиринге, отозванный мандат и спорная компенсация).
4. **External right / regulatory authority:** какой статус/лицензия/договор необходимы именно в РФ и на международном рынке.
5. **Business model / evidence:** комиссии, buyer, cost of capital/guarantee reserve, claims, P&L и явная сравнительная выгода относительно действующих банковских продуктов.

До проверки: `EDITORIAL_CANDIDATE_ONLY`; банк-гейты Issue #47 и независимый консилиум Issue #53 открыты. **Новую ФБС не утверждать даже если технология или международный service domain имеют слово `new`.**

## Короткий вывод для руководства

Зарубежные методики **не поддерживают подход «новый агент = новая ФБС»**. Они требуют отделить Capability от Service Domain/Process/Software и показать предмет ответственности и ценность. Научная основа — COVO / Semantic Symmetry (PoEM/EDOC). Для горизонта 2031–2041 доказательно стоит рассматривать **три условных операторских роли** — внешние права, мультисторонний клиринг, внешнюю схему ответственности. **Новых паспортов банка не доказано (0)**; названия — исследовательские гипотезы, а не официальный BIAN crosswalk.
