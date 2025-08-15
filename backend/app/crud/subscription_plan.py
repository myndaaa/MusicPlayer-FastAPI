# TODO: SUBSCRIPTION PLAN CRUD IMPLEMENTATION

# CREATE
# [ ] create_subscription_plan(plan_data: SubscriptionPlanCreate) -> SubscriptionPlan
#     - Validate uniqueness of name
#     - Set is_active=True, offer_created_at=datetime.now(timezone.utc)

# GET
# [ ] get_subscription_plan_by_id(plan_id: int) -> Optional[SubscriptionPlan]
# [ ] get_subscription_plan_by_name(name: str) -> Optional[SubscriptionPlan]
# [ ] get_all_subscription_plans(skip: int = 0, limit: int = 20) -> List[SubscriptionPlan]
#     - Supports pagination for admin UI
# [ ] get_all_active_subscription_plans() -> List[SubscriptionPlan]
#     - For public consumption (dropdowns, display)

# FILTER N SEARCH
# [ ] filter_subscription_plans(
#         min_price: float = 0,
#         max_price: float = 9999,
#         duration: Optional[int] = None,
#         is_active: Optional[bool] = True
#     ) -> List[SubscriptionPlan]
#     - Query filter for admin dashboard

# [ ] search_subscription_plans_by_keyword(keyword: str) -> List[SubscriptionPlan]
#     - Search name or description (ILIKE for PostgreSQL)

# UPDATE
# [ ] update_subscription_plan(plan_id: int, data: SubscriptionPlanUpdate) -> Optional[SubscriptionPlan]
#     - Updates any subset of fields (name, price, duration, description, etc.)
#     - Enforce name uniqueness if changed

# ACTIVATION / DEACTIVATION
# [ ] toggle_subscription_plan_active_status(plan_id: int, active: bool) -> SubscriptionPlan
#     - Enables or disables a plan (soft toggle)

# DELETE
# [ ] delete_subscription_plan(plan_id: int) -> bool
#     - Permanent deletion

# ANALYTICS / AGGREGATES
# [ ] count_total_subscription_plans() -> int
# [ ] count_active_subscription_plans() -> int
# [ ] get_most_popular_subscription_plans(limit: int = 5) -> List[SubscriptionPlan]
#     - Requires tracking usage via `UserSubscription` table later, to be put on another script.

# HELPERS
# [ ] subscription_plan_exists(plan_id: int) -> bool
# [ ] is_subscription_plan_name_taken(name: str, exclude_id: Optional[int] = None) -> bool
