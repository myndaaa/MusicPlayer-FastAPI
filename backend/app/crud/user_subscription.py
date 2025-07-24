# TODO: USER SUBSCRIPTION CRUD IMLPEMENTATION

# CREATE
# [ ] create_user_subscription(user_id: int, plan_id: int, start_date: datetime, duration_days: int) -> UserSubscription
#     - Calculate `end_date = start_date + timedelta(days=duration_days)`
#     - Set `is_auto_renew=True` by default
#     - prevent overlap with existing subscriptions 

# READ
# [ ] get_active_subscription(user_id: int, now: datetime = utcnow()) -> Optional[UserSubscription]
#     - where: start_date <= now <= end_date and is_cancelled = False

# [ ] get_all_subscriptions(user_id: int) -> List[UserSubscription]
#     - Return history (past, present, future)

# UPDATE
# [ ] cancel_subscription(user_id: int, subscription_id: int) -> UserSubscription
#     - Set `is_cancelled=True`, `cancelled_at=now`, `is_auto_renew=False`
#     - Only allowed if current or upcoming.

# [ ] update_auto_renewal(user_id: int, subscription_id: int, auto_renew: bool) -> UserSubscription
#     - Toggle `is_auto_renew`


# RENEW (manually or automatically)
# [ ] renew_subscription(user_id: int) -> UserSubscription
#     - Fetch active subscription / last subscription
#     - If `is_auto_renew=True` and not cancelled, create new subscription starting from end_date
