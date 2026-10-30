"""Toy, deterministic bank reference controls for FBS research *only*.

Executable negative-control invariants, NOT banking software, compliance,
production flows or proof of real banking E2E. No real customer data or funds.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from threading import Lock


class Refusal(Exception):
    """A mock policy refuses an unsafe instruction."""


def money(amount: str | int | Decimal) -> Decimal:
    number = Decimal(str(amount))
    if not number.is_finite() or number <= 0:
        raise Refusal("amount must be positive and finite")
    return number


@dataclass
class SharedMandate:
    """3.1.9: one shared principal cap across concurrent delegated agents."""
    principal: str
    agents: set[str]
    cap: Decimal
    consumed: Decimal = field(default_factory=lambda: Decimal("0"))
    revoked: set[str] = field(default_factory=set)
    _seen: dict[str, tuple[str, Decimal]] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)

    def spend(self, principal: str, agent: str, operation_id: str, amount: Decimal) -> bool:
        value = money(amount)
        with self._lock:
            if principal != self.principal or agent not in self.agents or agent in self.revoked:
                raise Refusal("principal/delegation is invalid or revoked")
            key = (agent, value)
            if operation_id in self._seen:
                if self._seen[operation_id] != key:
                    raise Refusal("operation replay changed its signed parameters")
                return False
            if self.consumed + value > self.cap:
                raise Refusal("shared principal cap exceeded")
            self.consumed += value
            self._seen[operation_id] = key
            return True

    def revoke(self, agent: str) -> None:
        with self._lock:
            self.revoked.add(agent)


@dataclass(frozen=True)
class PaymentOrder:
    """4.1.1: immutable approved instruction, separate from settlement truth."""
    principal: str
    beneficiary: str
    amount: Decimal
    signed: bool
    human_approved: bool
    high_risk: bool = False


@dataclass
class PaymentBook:
    _submitted: dict[str, PaymentOrder] = field(default_factory=dict)
    _status: dict[str, str] = field(default_factory=dict)

    def submit(self, key: str, order: PaymentOrder) -> str:
        money(order.amount)
        if not order.signed or (order.high_risk and not order.human_approved):
            raise Refusal("missing required authorization/step-up")
        if key in self._submitted:
            if order != self._submitted[key]:
                raise Refusal("idempotency-key collision with changed instruction")
            return self._status[key]
        self._submitted[key] = order
        self._status[key] = "PENDING"
        return "PENDING"

    def provider_update(self, key: str, provider_status: str) -> None:
        if key not in self._submitted or provider_status not in {"PAID", "FAILED"}:
            raise Refusal("untrusted settlement update")
        if self._status[key] in {"PAID", "FAILED"} and self._status[key] != provider_status:
            raise Refusal("final settlement is immutable")
        self._status[key] = provider_status

    def agent_claims_paid(self, key: str) -> str:
        return self._status[key]

    @property
    def unique_debits(self) -> int:
        return len(self._submitted)


@dataclass
class Guarantee:
    """4.1.22.2: independent legal obligations, not mutable by B2B events."""
    principal: str
    beneficiary: str
    face_value: Decimal
    exposure: Decimal = field(init=False)

    def __post_init__(self) -> None:
        self.exposure = money(self.face_value)

    def network_supplier_changed(self, new_supplier: str) -> None:
        _ = new_supplier  # Cannot rewrite existing beneficiary.

    def release(self, legal_amendment_confirmed: bool, amount: Decimal) -> None:
        value = money(amount)
        if not legal_amendment_confirmed or value > self.exposure:
            raise Refusal("a valid legal release instrument is required")
        self.exposure -= value


def aggregate_exposure(guarantees: list[Guarantee]) -> Decimal:
    return sum((g.exposure for g in guarantees), Decimal("0"))


@dataclass
class Escrow:
    """4.1.24: only verified, contract-authorized tranches can be released."""
    principal: str
    escrow_balance: Decimal
    version: int = 1
    released: Decimal = field(default_factory=lambda: Decimal("0"))

    def release(self, tranche: Decimal, *, shipped: bool, accepted: bool,
                buyer_acceptor_independent: bool, valid_contract_version: int,
                contract_permits: bool) -> None:
        value = money(tranche)
        if (not shipped or not accepted or not buyer_acceptor_independent
                or not contract_permits or valid_contract_version != self.version):
            raise Refusal("escrow disbursement evidence/contract is insufficient")
        if value > self.escrow_balance:
            raise Refusal("tranche exceeds escrow balance")
        self.escrow_balance -= value
        self.released += value

    def agent_asks_to_rollback(self) -> None:
        raise Refusal("final payment cannot be reversed by agent text")


@dataclass(frozen=True)
class TradeEvent:
    """6.1.11: valid JSON is not legal status equivalence."""
    status: str
    signed_by: str
    buyer: str
    seller: str
    ebl_active: bool


def legally_accepted(event: TradeEvent) -> bool:
    return (event.status == "ACCEPTED" and event.signed_by == event.buyer
            and event.buyer != event.seller and event.ebl_active)


@dataclass(frozen=True)
class Alert:
    review: bool
    reason: str


def mock_aml_review(
    transfers: list[tuple[str, Decimal]], *,
    consented_legal_data: bool, known_account_owner: str,
    model_prompt: str = "",
) -> Alert:
    """7.5.1: arbitrary sample threshold, NOT AML policy."""
    _ = model_prompt  # Language-model prompt cannot override policy.
    if not consented_legal_data:
        return Alert(True, "MISSING_LEGAL_DATA_BASIS")
    total = sum((money(amount) for principal, amount in transfers
                 if principal == known_account_owner), Decimal("0"))
    if total >= Decimal("100"):
        return Alert(True, "AGGREGATE_OWNER_THRESHOLD")
    return Alert(False, "NO_THRESHOLD_ALERT")
