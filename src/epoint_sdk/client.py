from __future__ import annotations

from typing import Any, Mapping, Optional, Union

from ._core import AsyncEngine, Op, SyncEngine
from .callbacks import verify_callback
from .models import Transaction
from .resources import Cards, Installments, Invoices, Payments, Split, Transfers, Wallets, Widgets


def _alive(body: Any) -> bool:
    return isinstance(body, Mapping) and str(body.get("status", "")).lower() == "ok"


class _Namespaces:
    _private_key: str

    def _mount(self) -> None:
        self.payments = Payments(self)
        self.cards = Cards(self)
        self.split = Split(self)
        self.installments = Installments(self)
        self.wallets = Wallets(self)
        self.widgets = Widgets(self)
        self.invoices = Invoices(self)
        self.transfers = Transfers(self)

    def verify_callback(self, data: Union[str, Mapping[str, Any]], signature: str = "") -> Transaction:
        return verify_callback(self._private_key, data, signature)


class Epoint(SyncEngine, _Namespaces):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._mount()

    def heartbeat(self) -> bool:
        result: bool = self._run(Op("heartbeat", None, _alive, safe=True, method="GET", signed=False))
        return result

    def request(self, endpoint: str, payload: Optional[Mapping[str, Any]] = None, *, safe: bool = False) -> Any:
        return self._run(Op(endpoint, dict(payload or {}), safe=safe))


class AsyncEpoint(AsyncEngine, _Namespaces):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._mount()

    async def heartbeat(self) -> bool:
        result: bool = await self._run(Op("heartbeat", None, _alive, safe=True, method="GET", signed=False))
        return result

    async def request(self, endpoint: str, payload: Optional[Mapping[str, Any]] = None, *, safe: bool = False) -> Any:
        return await self._run(Op(endpoint, dict(payload or {}), safe=safe))
