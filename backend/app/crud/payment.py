# TODO: PAYMENT CRUD IMPLEMENTATION

# CREATE
# [ ] create_payment(payment_data: PaymentCreate) -> Payment
#     - Ensure unique transaction_reference before insert
#     - Set created_at automatically

# GET
# [ ] get_payment_by_id(payment_id: int) -> Optional[Payment]
# [ ] get_payments_by_user(user_id: int, skip: int = 0, limit: int = 20) -> List[Payment]
# [ ] get_payments_by_status(status: str, skip: int = 0, limit: int = 20) -> List[Payment]
# [ ] get_payments_by_method(method: str, skip: int = 0, limit: int = 20) -> List[Payment]
# [ ] get_payments_in_date_range(start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 20) -> List[Payment]
# [ ] get_all_payments(skip: int = 0, limit: int = 50) -> List[Payment]  # admin use

# UPDATE
# [ ] update_payment_status(payment_id: int, new_status: str, completed_at: Optional[datetime] = None) -> bool

# DELETE
# Not needed as payments should not be deleted

# HELPERS 
# [ ] payment_exists(payment_id: int) -> bool
# [ ] transaction_reference_taken(reference: str) -> bool
# [ ] validate_payment_status(status: str) -> bool
# [ ] validate_payment_method(method: str) -> bool


# [ ] get_total_revenue_by_date_range(start_date: datetime, end_date: datetime) -> float
# [ ] get_user_total_payments(user_id: int) -> float
# [ ] get_payment_summary_grouped_by_status() -> Dict[str, int]
