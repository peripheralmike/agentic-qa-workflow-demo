from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class PaymentInput(Strict):
    reference: str = Field(max_length=80)
    amount: str = Field(max_length=40)
    currency: str = Field(max_length=10)


class Scenario(Strict):
    id: str = Field(pattern=r"^[a-z0-9_-]{1,50}$")
    requirement: Literal["R1", "R2", "R3", "R4", "R5"]
    purpose: str = Field(min_length=8, max_length=300)
    payments: list[PaymentInput] = Field(max_length=101)
    expected_status: Literal[201, 422]
    expected_imported: int = Field(ge=0, le=100)


class Plan(Strict):
    questions: list[str] = Field(min_length=1, max_length=10)
    scenarios: list[Scenario] = Field(min_length=1, max_length=30)


class Review(Strict):
    concerns: list[str] = Field(max_length=20)
    summary: str = Field(min_length=1, max_length=2000)
