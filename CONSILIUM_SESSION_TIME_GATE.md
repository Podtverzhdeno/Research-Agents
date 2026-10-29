# Проверяемое правило времени для многоагентного консилиума ФБС

**Версия:** 2026-10-29 · **Статус:** `GOVERNANCE_REQUIREMENT`, не отчёт о проведённой сессии.

## I. Временной порог

Для **КАЖДОЙ ФБС отдельно**: минимальный календарный срок обсуждения `>=60 минут` от реально зафиксированного старта и минимальное **активное время обсуждения** `>=60 минут`, **без учёта пауз**. Формулировка «45–60+ минут» намеренно ужесточена до 60 минут. Если одна сессия идёт 4 минуты, итог не может получить статус `COMPLETED`, даже если подготовлено 100 сообщений или красивый текст.

Начало фиксируется в **UTC** в точке фактического запуска реальной дискуссии (`START`) по первому поддающемуся проверке событию оркестратора / GitHub. **Не использовать создание этого документа, сбор источников или ранее написанные чатовые сообщения как `started_at`.**


## I.a. Непрерывное участие каждого агента (обязательное правило)

- При `START` зафиксировать `session_id`, `agent_id`, роль каждого участника и серверное UTC-время начала. Нельзя задним числом переносить старт.
- **Каждый заявленный активным агент обязан продолжать содержательный обмен аргументами, расчётами и критикой до выполнения временного шлюза**. Запрещены преждевременные `DONE`, `FINAL`, выход агента или прекращение обсуждения под предлогом, что его индивидуальная часть уже решена.
- Минимум 45 минут из пожелания заказчика — промежуточный рубеж, **не разрешение закрыть сессию**; действующий строгий порог консилиума — **не менее 60 минут реального подтверждённого активного обсуждения** для каждой ФБС. При открытых возражениях обсуждение длится 60+ минут до их разрешения или явной фиксации как нерешённых.
- Пауза, потеря агента/рантайма и пустые heartbeat-события не засчитываются в активное время. Если агент выпал, его участие помечается `PAUSED` и затем возобновляется; без подтверждения активности запрещено изображать непрерывный разговор.
- Координатор не может завершить сессию за других агентов; перед `REVIEW_PENDING` проверяется участие всех заявленных ролей в содержательных обсуждениях, журнал событий и качество результата. Невозможность поддерживать живую сессию означает `SESSION_NOT_VERIFIED`, а не фиктивное исполнение часового требования.

## II. Состояния

```text
NOT_STARTED
    |
  START (server-side UTC timestamp, session_id, FBS code)
    |
 ACTIVE (обсуждение, содержательные контрольные точки)
    | \
    |  -> PAUSED (таймер активного времени остановлен) -> RESUMED -> ACTIVE
    |
  60+ wall minutes AND 60+ verified active minutes AND all quality gates
    |
 REVIEW_PENDING (проверка URL/времени/контраргументов/версии ФБС)
    |
 COMPLETED_EDITORIAL (после проверки протокола; НЕ BANK_APPROVED)
```

До перехода в `REVIEW_PENDING` нельзя маркировать окончание `COMPLETED`, `DONE`, `FINAL`, `CLOSED`, `CONSENSUS_REACHED`. Если все идеи не проходят барьеры V2, результат может быть `NO_BET`, но только после настоящего полного консилиума.

## III. Доказательства

У каждой сессии своя **отдельная** запись:

```yaml
session_id: fbs-2.1.3-2036-iteration-001
fbs_code: 2.1.3
source_version: FBS_54_functional_latest
session_status: NOT_STARTED
started_at_utc: null            # момент START, от GitHub/оркестратора
last_active_at_utc: null
ended_at_utc: null
wall_clock_elapsed_seconds: 0    # рассчитывается, не вводится вручную
verified_active_seconds: 0       # сумма непрерывных подтверждённых интервалов
participants: []                # реальный agent_id, роль, версия/тип
events: []                      # серверный timestamp, agent_id, message id, URL
pause_intervals: []             # начало/конец, исключать из active
checkpoints:
  - slot_minutes: 15
    real_discussion_event_ids: []
  - slot_minutes: 30
    real_discussion_event_ids: []
  - slot_minutes: 45
    real_discussion_event_ids: []
  - slot_minutes: 60
    real_discussion_event_ids: []
quality_gates:
  alternatives_min_3_and_no_bet: false
  scope_pass: false
  agency_pass: false
  novelty_pass: false
  value_pass: false
  legal_risk_review: false
  meaningful_iterations_min_2: false
  negative_tests_proposed: false
  unresolved_objections_disclosed: false
bank_approval: PENDING_EXTERNAL_VALIDATION
```

**Контрольные точки каждые 15 минут** — не заменяют фактические сообщения между ними. Система должна иметь **heartbeat агентного рантайма и журнал коммуникаций**. Верификатор проверяет: серверные timestamps, идентификатор реально работающего процесса, отсутствие периодов паузы, наличие содержательных контраргументов и изменённых решений. Из одного лишь факта `started_at` + `ended_at` *нельзя* сделать вывод, что агенты всё время обсуждали задачу.

Если нет наблюдаемого оркестратора, корректная маркировка **`SESSION_NOT_VERIFIED`**. Чатовый текст, созданный единовременно моделью, или заранее отрендеренные 5 400 раундов **не** считается 60-минутной работой.

## IV. Машинный veto при закрытии

```python
assert session.fbs_code in active_fbs_registry
assert session.started_at_utc and session.ended_at_utc
assert server_verified(session.events)  # не строки, введённые автором
assert utc_seconds(session.ended_at_utc - session.started_at_utc) >= 3600
assert verified_active_seconds(session.events, session.pause_intervals) >= 3600
assert no_unverified_gaps(session.events)     # события рантайма/heartbeat
assert meaningful_content_in_all_15min_windows(session.events)
assert contains_competing_ideas(session) and has_no_bet_option(session)
assert all_required_v2_gates_checked(session)
# Затем REVIEW_PENDING -> только редакционное COMPLETED_EDITORIAL.
```

Это **спецификация** для будущего оркестратора, а не действующий исполняемый тест. Для реальной защиты от преждевременного закрытия необходим CI/status-check или иной валидатор на эти события, управляемый GitHub branch protection/review rules. Без такой интеграции это документальное правило, не техническая гарантия.

## V. Работа с GitHub

1. Для каждого конкретного заседания открыть issue/дискуссию, зарегистрировать START с серверным `created_at` и source SHA.
2. Агенты обсуждают проблему и альтернативы, фиксируя реальный обмен вопросами, возражениями, исправлениями и независимые timestamps; лог не дописывать задним числом.
3. Каждые 15 минут сделать содержательный checkpoint с ссылками на события, а не просто написать «живы».
4. Ни один участник и координатор **не вправе заявлять завершение до истечения 60+ минут фактической активности** и закрытия качественных барьеров. Прерывистая сессия остаётся `PAUSED` или `ACTIVE`, но не `COMPLETED`.
5. Итоговый PR/решение публикуется только после проверенного отчёта с `started_at`, `ended_at`, `active_seconds`, `quality_gates` и явными нерешёнными возражениями.
6. Состояние `COMPLETED_EDITORIAL` не заменяет реального банковского ACK: [#47](https://github.com/Podtverzhdeno/Research-Agents/issues/47).

## VI. Привязка

- [Консилиум V2 — методика и 54 ФБС](FBS_CONSILIUM_V2_METHODOLOGY_20261029.md).
- [Issue #52 — новая ФБС / без доработок / антидублирование](https://github.com/Podtverzhdeno/Research-Agents/issues/52).
- [Issue #47 — банковские внешние подтверждения](https://github.com/Podtverzhdeno/Research-Agents/issues/47).
