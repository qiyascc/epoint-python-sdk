from __future__ import annotations

from enum import Enum


class _Str(str, Enum):
    def __str__(self) -> str:
        return str(self.value)


class Status(_Str):
    NEW = "new"
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"
    RETURNED = "returned"
    SERVER_ERROR = "server_error"
    UNKNOWN = "unknown"

    @classmethod
    def of(cls, value: object) -> Status:
        try:
            return cls(str(value or "").strip().lower())
        except ValueError:
            return cls.UNKNOWN


class CardStatus(_Str):
    NEW = "new"
    ACTIVE = "active"
    PENDING = "pending"
    REJECTED = "rejected"
    EXPIRED = "expired"
    SESSION_EXPIRED = "session_expired"
    UNKNOWN = "unknown"

    @classmethod
    def of(cls, value: object) -> CardStatus:
        try:
            return cls(str(value or "").strip().lower())
        except ValueError:
            return cls.UNKNOWN


class OperationCode(_Str):
    CARD_REGISTRATION = "001"
    PAYMENT = "100"
    REGISTRATION_WITH_PAYMENT = "200"


class Language(_Str):
    AZ = "az"
    EN = "en"
    RU = "ru"


class Currency(_Str):
    AZN = "AZN"
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"
