# Consilium V2: genuine session evidence, not simulated minutes

This folder contains a **fail-closed** session gate. Every one of the 54 FBS codes must have its **own** independently auditable runtime discussion lasting **>=3600 wall-clock seconds and >=3600 active seconds**. Sessions may run in parallel only if there are actual independent running agent processes and trusted source telemetry.

## Setup / live operation (not performed yet)
1. Deploy an actual multi-agent orchestrator; configure runtime identities/roles, durable event logging, heartbeat, pause/resume, substantive message source URLs and SHA-256 for each message.
2. Give the orchestrator an Ed25519 signing key held outside the repository. Store its **public** PEM key at `consilium/trusted_orchestrator_ed25519.pub` through protected main-branch review. **Do not put private signing key in GitHub.** It is intentionally absent now, and verification intentionally fails.
3. For each FBS, create an independent runtime `session_id`, capture true orchestrator UTC START, per-agent explicit signed `active_intervals` (UTC start/end, trusted telemetry provenance, evidence URL, endpoint runtime event IDs) covering every unpaused second for >=60 minutes each, plus server-signed END; record >=2 distinct agent processes and substantive messages from each in every 15-minute window.
4. Sign the complete JSON record (all fields except `signature_b64`) using canonical `json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',', ':')).encode('utf-8')`, base64-encode signature and place into that code's registry record. Runtime attestation must be backed by independent provider logs. Do not backdate timestamps.
5. Mark only `REVIEW_PENDING` once all quality gates are honestly satisfied; `COMPLETED_EDITORIAL` and `BANK_APPROVED` are **separate approvals**.
6. Run `python -m unittest discover -s tests -p 'test_consilium_gate.py' -v` and `python -m consilium.verify_sessions --source FBS_FULL_54/FBS_ALL_54_SOURCE_AND_DECISION.csv --sessions consilium/session_registry.json --trusted-pubkey consilium/trusted_orchestrator_ed25519.pub`.

**Verifier semantics (V17 hardening):** A 60-minute wall-clock interval minus pauses is only an upper bound, **not verified active time**. Every agent must supply explicit runtime-attested active intervals with independent endpoint event witnesses; the script requires >=3600 seconds per agent and rejects uncovered unpaused seconds. Substantive reviews are required in every active 15-minute window across the full session duration, not merely the first hour. These are **structural checks of signed claims**, not proof of actual reasoning. A separate independent human content review and bank approvals remain mandatory.

**Important security limitations:** A cryptographic signature proves that the holder of the trusted private key attested these logs, not that genuine discussion took place. External runtime/platform verification, review of substantive messages and trusted signing-key custody are mandatory. PR authors must **not** be able to replace trusted public keys or modify verifier code without independent protected review. Set branch protection / required checks in GitHub settings (not established by this PR). The CI gate is not technically mandatory until repository rules enforce it. Never equate one GitHub issue created_at with 54 completed sessions.


## Дополнительные условия V18 / защита от ложного консенсуса

- **Все 54 сессии разные.** У каждой уникальный `session_id`, подписанный `source_sha` должен совпадать с SHA256 зафиксированного CSV исходных 54 ФБС. Объект агента не заменяет это условие.
- **Идёт именно дискуссия.** Каждая реально активная 15-минутная зона по всей продолжительности сессии, а не только первые 60 минут, должна содержать содержательные сообщения от обеих сторон и перекрёстные `reply_to_event_id` к другому агенту.
- **Heartbeat не равен содержательной активности.** Время, отработанное реально, подтверждается отдельными аттестованными `active_intervals`, которые привязаны к подписанным runtime events; паузы вычитаются. Просто оставить приложение открытым на час недостаточно.
- **Подпись не является независимым экспертным одобрением.** Ed25519 удостоверяет заявление держателя ключа, но внешний эксперт должен отдельно проверить provider logs, фактическое содержание переписки, непроизводность двух «агентов» от одного процесса и отсутствие подмены свидетельств. Две роли одного текстового диалога не дают `independent_agents=VERIFIED`.
- **Бизнес-одобрение отдельно.** [54 редакционных вердикта](../DISCUSSIONS/CONSILIUM_V17_ALL_54_EDITORIAL_APPROVAL_REGISTER_20261030.csv) не подтверждают ни банк, ни production. [36 независимых E2E спецификаций](../DISCUSSIONS/CONSILIUM_V18_36_E2E_EXPECTATIONS_20261030.csv) всё ещё `NOT_EXECUTED`; [CI](../.github/workflows/consilium-gate.yml) проверяет только непротиворечивость спецификаций и защиту от ложного статуса.

**Текущее положение:** `editorial-integrity=PASS`; `consilium-time-gate=FAIL CLOSED` до появления подлинных журналов, защищённой доверенной подписи и независимой семантической экспертизы. Не отключать второй gate ради зелёного CI.

## Current status
All 54 are `NOT_STARTED` in the registry. No signed authentic telemetry has been provided, so `SESSION_NOT_VERIFIED` and any attempt to merge as `COMPLETED` must be rejected. The research/editorial document is useful before this process, but does not claim to satisfy it.
