from typing import Optional, List, Annotated
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, StringConstraints, Field, model_validator
import enum


# Payment status enum
class PaymentStatus(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"
    refunded = "refunded"
    cancelled = "cancelled"


# Payment method enum
class PaymentMethod(str, enum.Enum):
    paypal = "paypal"
    credit_card = "credit_card"
    debit_card = "debit_card"
    bank_transfer = "bank_transfer"
    crypto = "crypto"


# Base schema for payment
class PaymentBase(BaseModel):
    user_id: int
    amount: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
    status: PaymentStatus
    method: PaymentMethod
    transaction_reference: Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]

    class Config:
        from_attributes = True
        use_enum_values = True


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class PaymentOut(PaymentBase):
    id: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True


# Schemas for relationships
class UserMinimal(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str

    class Config:
        from_attributes = True


# Payment output with relationships
class PaymentWithRelations(PaymentOut):
    user: UserMinimal


# Payment with additional details
class PaymentWithDetails(PaymentWithRelations):
    payment_method_details: Optional[dict] = None  # Additional payment method specific data
    refund_amount: Optional[Decimal] = None
    refund_reason: Optional[str] = None
    refunded_at: Optional[datetime] = None


# List schemas for pagination
class PaymentList(BaseModel):
    payments: List[PaymentOut]
    total: int
    page: int
    per_page: int
    total_pages: int


class PaymentListWithRelations(BaseModel):
    payments: List[PaymentWithRelations]
    total: int
    page: int
    per_page: int
    total_pages: int


# Search and filter schemas
class PaymentFilter(BaseModel):
    user_id: Optional[int] = None
    status: Optional[PaymentStatus] = None
    method: Optional[PaymentMethod] = None
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None
    created_at_from: Optional[datetime] = None
    created_at_to: Optional[datetime] = None
    completed_at_from: Optional[datetime] = None
    completed_at_to: Optional[datetime] = None


class PaymentSearch(BaseModel):
    query: str  # Search in transaction_reference
    user_id: Optional[int] = None
    status: Optional[PaymentStatus] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# Payment processing schemas
class PaymentProcess(BaseModel):
    user_id: int
    amount: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
    method: PaymentMethod
    payment_method_details: Optional[dict] = None  # Payment method specific data


class PaymentRefund(BaseModel):
    payment_id: int
    refund_amount: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
    refund_reason: Optional[str] = None
    partial_refund: bool = False

    @model_validator(mode="after")
    def validate_refund_amount(self) -> "PaymentRefund":
        """Ensure refund amount is not greater than original payment amount"""
        # TODO: Implement in service layer after fetching original payment amount
        return self


# Payment statistics
class PaymentStats(BaseModel):
    total_payments: int
    successful_payments: int
    failed_payments: int
    pending_payments: int
    refunded_payments: int
    total_amount: Decimal
    total_refunded: Decimal
    net_amount: Decimal


# Payment method specific schemas
class CreditCardPayment(BaseModel):
    card_number: Annotated[str, StringConstraints(min_length=13, max_length=19)]
    expiry_month: Annotated[int, Field(ge=1, le=12)]
    expiry_year: Annotated[int, Field(ge=2024)]
    cvv: Annotated[str, StringConstraints(min_length=3, max_length=4)]
    cardholder_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class PayPalPayment(BaseModel):
    paypal_email: Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]


class BankTransferPayment(BaseModel):
    account_number: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
    routing_number: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
    account_holder_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


# For future PayPal integration via sandbox environment
class PaymentWebhook(BaseModel):
    payment_id: int
    status: PaymentStatus
    transaction_reference: str
    webhook_data: dict  # Raw webhook data from PayPal
    signature: Optional[str] = None  # webhook verification 
