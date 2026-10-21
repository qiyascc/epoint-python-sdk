from __future__ import annotations

from typing import Any, Optional
from urllib.parse import quote, urlsplit

from goodconf import Field, GoodConf, GoodConfConfigDict
from pydantic import BaseModel, SecretStr, field_validator

from ._version import __version__
from .enums import Currency, Language
from .errors import ConfigurationError
from .messages import text

LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})


class Endpoints(BaseModel):
    payment: str = "/api/1/request"
    checkout: str = "/api/1/checkout"
    status: str = "/api/1/get-status"
    reverse: str = "/api/1/reverse"
    hold: str = "/api/1/pre-auth-request"
    capture: str = "/api/1/pre-auth-complete"
    card_register: str = "/api/1/card-registration"
    card_register_pay: str = "/api/1/card-registration-with-pay"
    card_charge: str = "/api/1/execute-pay"
    card_status: str = "/api/1/get-status-card"
    payout: str = "/api/1/refund-request"
    split_payment: str = "/api/1/split-request"
    split_charge: str = "/api/1/split-execute-pay"
    split_register_pay: str = "/api/1/split-card-registration-with-pay"
    installment_plans: str = "/api/1/get-installment-request"
    installment_payment: str = "/api/1/installment-request"
    wallets: str = "/api/1/wallet/status"
    wallet_payment: str = "/api/1/wallet/payment"
    widget: str = "/api/1/token/widget"
    widget_split: str = "/api/1/token/split-payment"
    invoice_create: str = "/api/1/invoices/create"
    invoice_update: str = "/api/1/invoices/update"
    invoice_view: str = "/api/1/invoices/view"
    invoice_list: str = "/api/1/invoices/list"
    invoice_sms: str = "/api/1/invoices/send-sms"
    invoice_email: str = "/api/1/invoices/send-email"
    b2b_transfer: str = "/api/1/b2b/payment"
    b2b_status: str = "/api/1/b2b/payment/{order_id}"
    heartbeat: str = "/api/heartbeat"


class Settings(GoodConf):
    model_config = GoodConfConfigDict(
        env_prefix="EPOINT_",
        file_env_var="EPOINT_CONFIG",
        default_files=["epoint.toml", "epoint.yaml", "epoint.yml", "epoint.json"],
        extra="ignore",
        env_nested_delimiter="__",
    )

    public_key: str = Field(default="", description=text("settings.public_key"))
    private_key: SecretStr = Field(default=SecretStr(""), description=text("settings.private_key"))
    base_url: str = Field(default="https://epoint.az", description=text("settings.base_url"))
    endpoints: Endpoints = Field(default_factory=Endpoints, description=text("settings.endpoints"))
    language: Language = Field(default=Language.AZ, description=text("settings.language"))
    currency: Currency = Field(default=Currency.AZN, description=text("settings.currency"))
    success_url: Optional[str] = Field(default=None, description=text("settings.success_url"))
    error_url: Optional[str] = Field(default=None, description=text("settings.error_url"))
    timeout: float = Field(default=30.0, gt=0, description=text("settings.timeout"))
    connect_timeout: float = Field(default=10.0, gt=0, description=text("settings.connect_timeout"))
    max_retries: int = Field(default=2, ge=0, le=10, description=text("settings.max_retries"))
    backoff_base: float = Field(default=0.5, ge=0, description=text("settings.backoff_base"))
    backoff_cap: float = Field(default=8.0, ge=0, description=text("settings.backoff_cap"))
    user_agent: str = Field(default="epoint-python-sdk/{version}", description=text("settings.user_agent"))
    allow_insecure_http: bool = Field(default=False, description=text("settings.allow_insecure_http"))

    @field_validator("base_url")
    @classmethod
    def _base_url(cls, value: str) -> str:
        parts = urlsplit(value.strip())
        if parts.scheme not in ("http", "https") or not parts.hostname:
            raise ValueError(text("error.base_url", url=value))
        return value.strip()

    def check_transport(self) -> None:
        parts = urlsplit(self.base_url)
        if parts.scheme == "https" or self.allow_insecure_http or parts.hostname in LOCAL_HOSTS:
            return
        raise ConfigurationError(text("error.insecure", url=self.base_url))

    def url(self, endpoint: str, **params: Any) -> str:
        template = endpoint if endpoint.startswith("/") else getattr(self.endpoints, endpoint)
        path = template.format(**{k: quote(str(v), safe="") for k, v in params.items()})
        return self.base_url.rstrip("/") + path

    def resolved_user_agent(self) -> str:
        return self.user_agent.replace("{version}", __version__)

    def keys(self) -> tuple[str, str]:
        public, private = self.public_key.strip(), self.private_key.get_secret_value().strip()
        if not public or not private:
            raise ConfigurationError(text("error.missing_keys"))
        return public, private


Settings.__doc__ = text("settings.description")


def load_settings(config_file: Optional[str] = None, **overrides: Any) -> Settings:
    given = {key: value for key, value in overrides.items() if value is not None}
    return Settings(load=True, config_file=config_file, **given)
