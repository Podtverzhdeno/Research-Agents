# Round 08 — критическая сверка пяти конкурирующих портфелей 2031–2041

**28.10.2026 · RESEARCH_QA_DONE / NOT_BANK_APPROVED.** Это **контраргументы**, а не шестой список будущих продуктов. Сохранён единый [основной навигатор V01–V13](FUTURES_2031_2041_CANONICAL_RESOLUTION.md) и [подробная финансово-юридическая рецензия](FUTURES_DECISION_2031_2041_CANONICAL.md). Внешняя приёмка остаётся [#47](https://github.com/Podtverzhdeno/Research-Agents/issues/47).

**Сравнены** пять параллельных первоначальных версий (12,13,17,18,22 идеи) и дополнительный N01–N14. Эти редакции подготовлены аналитическими проходами GPT-6, не независимыми банковскими комитетами. В таблице explicit verdict на 15 самых конфликтных идей.

| Round 08 | Контргипотеза | R2 | Точные ФБС / отсутствующие владельцы | Сильный существующий baseline | Что решает судьбу идеи | Редакторское решение |
|---|---|---|---|---|---|---|
| R01 | Финансирование по доказанному товарному событию | V01+V03 | Кредитование вне 54; 6.1.5/6.1.6 | ADB PO/deep tier SCF существует | Нужен законный debtor/claim, независимый evidence, ΔRAC>0 | RETAIN AS V01/V03 |
| R02 | Trade DvP между правом на eBL и деньгами | V13 | 4.1.10.2,6.1.11,7.11.1 | DCSA cross-platform eBL существует | MLETR/UK ETDA corridor, controlling party, финальность и failure handling | CONDITIONAL LONG |
| R03 | Страховая защита неоплаты в агентной сделке | WATCH_INSURANCE | 4.1.22.2 только если именно банковская гарантия; страхование outside 54 | Allianz Trade pay API | Страховой андеррайтинг, claim fraud, корреляции | PARTNER / NO P1 |
| R04 | Переносимый профиль SME между банковскими юрисдикциями | V05+V11 / WATCH_APERTA | 3.1.1,3.1.10,6.1.10,6.1.11 | BIS Aperta PoC в пяти экономиках | Receiving bank всё равно исполняет KYC/AML и local law | SUPPORT / NO V14 |
| R05 | Мобильное обеспечение после этапа поставки | V04 | 4.1.11,4.1.14.4,7.11.1 | DTCC DTS уже LIVE с 28.10.2026 | Legal lien/priority/segregation/default и новые банковские доходы | CONDITIONAL LONG |
| R06 | Контингентный финансовый маршрут после срыва | V02 | 2.1.3,3.3.3,4.1.22.2; кредит outside 54 | Стандартные standby credit и trade insurance | Новый buyer approval/контракт, новый риск и обоснованный avoided loss | SEGMENT TEST |
| R07 | Микроплатежи машинных сервисов | V10 | 4.1.5,4.1.9.3,4.1.10.1 | Mastercard AP4M June 2026 | Net margin per batch после AML/dispute и нулевое нарушение мандата | NICHE / DEMOTE |
| R08 | Коррелированное движение массовых агентных платежей | V06 | 5.2.6 лишь ИТ; risk outside 54 | BIS Agenti исследовательский симулятор | Доказать предотвращённый real loss vs false stop | CORE RISK CONTROL |
| R09 | Агентный аукцион юридически исполнимых банковских условий | V11 | 2.1.3,3.3.3,3.2.6 | UCP/AP2 и обычные ERP marketplace | Маржа падает от price compression; выигранный прибыльный договор | CORE CHANNEL |
| R10 | 24/7 международный PvP между доступными токенизированными депозитами | V07 | 4.1.10.2,6.1.11; FX/liquidity outside 54 | Agorá July RVT, MAS BLOOM initiative | Нет права/доступа к каждой валюте, token assets отличаются | LONG HORIZON |
| R11 | Гарантия на доказанный результат | V01 | 4.1.22.2 и отдельно 4.1.11 | ГК РФ 368(4) допускает event-contingent сумму | False release либо нет цены/капитальной выгоды над обычной гарантией | SUPPORT / NO STANDALONE |
| R12 | Граф доверия и смена агента без бизнес-остановки | V12 | 3.1.9,3.1.15,7.7.2.1.3.2 | AP2 mandates и HKMA ART proposals | Atomic revocation и новый runtime spoof до исполнения | CORE TRUST |
| R13 | Автоматическое корпоративное treasury под 4.1.13.1 | REJECT FBS MAPPING | 4.1.13.1=физическая наличность | Treasury/tokenised money есть, но иные владельцы ФБС | Нет права переносить цифровые FX в cash inventory | REJECT MISMAPPING |
| R14 | Финансирование оборудования во втором жизненном цикле | V08 | 6.1.5,6.1.6,4.1.11; кредит outside 54 | Обычный equipment finance/lease, BIS Insight — только цепочки | Верная стоимость б/у техники, ликвидность залога, проверяемость истории | SEGMENT / WATCH |
| R15 | Ценные бумаги с исполнением условий эмитента агентами | V09 | 4.1.14.2,4.1.14.4,7.11.1 | DTCC DTS, BIS Promissa для MDB notes | Законный выпуск и custody, нельзя превратить B2B договор в облигацию | CONDITIONAL LONG |

## Три обязательных сценария, где стратегия проигрывает

1. **Рынок остаётся human-approved.** [BoE/FCA 26.10.2026](https://www.bankofengland.co.uk/report/2026/artificial-intelligence-in-uk-financial-services-2026) зафиксировал широкую автономию только у 2% ответивших организаций. Если банк окупается **только** при автономных агентах без подтверждения человека, expensive frontier перестаёт быть P1; V01/V03/V05/V11/V12 должны работать при human-in-loop.
2. **Платформы и страховщики забрали торговый intent.** Visa/BILL уже исполняют approved invoices; Allianz Trade pay already offers embedded insurance. Слабость банка: замена юридической ответственности красивым «API of bank offers» не создаёт новой маржи, V02/V11 нужны целевой сегмент и положительная ΔRAC.
3. **Международные рельсы фрагментированы.** Agorá ограниченно проверена на реальных суммах в июле 2026, DTCC DTS в США LIVE 28.10.2026, но нет автоматического общего legal corridor для V04/V07/V13. Это LONG, не обещанная доступная услуга.

## Иностранные первоисточники (названия проекта ≠ обещание нашего продукта)

- BIS Project Agorá real-value testing July 2026: https://www.bis.org/project/agora
- MAS BLOOM initiative: https://www.mas.gov.sg/schemes-and-initiatives/BLOOM
- BIS Aperta PoC: https://www.bis.org/project/aperta
- BIS Agenti research simulation: https://www.bis.org/node/87745
- DTCC DTS launched 28.10.2026: https://www.dtcc.com/press-releases/2026/dtcc-tokenization-service-goes-live
- DCSA eBL Standard Annex: https://dcsa.org/newsroom/five-ebl-platforms-adopt-dcsa-interoperability-annex
- Mastercard AP4M: https://www.mastercard.com/global/en/news-and-trends/press/2026/june/mastercard-launches-agent-pay-for-machines.html
- HKMA ART: https://www.hkma.gov.hk/eng/news-and-media/press-releases/2026/10/20261015-3/
- Bank of England/FCA survey: https://www.bankofengland.co.uk/report/2026/artificial-intelligence-in-uk-financial-services-2026

**Disposition:** по всем R01–R15 есть KEEP/CONDITIONAL/DEMOTE/WATCH/REJECT, и они связаны с V-кодами или честным `OUTSIDE_54`. Ни одна из этих строк не является банком одобренной прибыльностью, легальным новым договором или фактом выполненного E2E.
