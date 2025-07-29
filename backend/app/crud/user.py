# TODO: USER CRUD IMPLEMENTATION


# [ ] create_user(user_data: UserCreate) -> User
# - Hash password before storing
# - Ensure unique username and email (checks before insert)
# - Set created_at, is_active=True


# READ / GET USERS

# [ ] get_user_by_id(user_id: int) -> Optional[User]
# [ ] get_user_by_username(username: str) -> Optional[User]
# [ ] get_user_by_email(email: str) -> Optional[User]
# [ ] get_user_by_first_name(fname: str) -> List[User]
# [ ] get_user_by_last_name(lname: str) -> List[User]
# [ ] get_users(skip: int = 0, limit: int = 20) -> List[User]  # paginated
# [ ] get_all_users() -> List[User]  # non-paginated
# [ ] get_users_by_role(role: str, skip: int = 0, limit: int = 20) -> List[User]
# [ ] get_all_users_active_only(skip: int = 0, limit: int = 20) -> List[User]
# [ ] get_all_disabled_users(skip: int = 0, limit: int = 20) -> List[User]


# UPDATE USER PROFILE
# [ ] update_user_info(user_id: int, data: UserUpdate) -> Optional[User]
#     - Allows updating: username, first_name, last_name, email
#     - Check if new username/email already exists for another user


# PASSWORDS

# [ ] change_user_password(user_id: int, new_password_hash: str) -> bool
#     - Hash is already pre-processed
# [ ] verify_user_password(user_id: int, plain_password: str) -> bool
#     - Compare against stored hash using security.verify_password


#  ACTIVATION / DEACTIVATION

# [ ] disable_user(user_id: int) -> bool
#     - Set is_active = False, disabled_at = datetime.utcnow()
# [ ] enable_user(user_id: int) -> bool
#     - Set is_active = True, disabled_at = None


# AUDIT 
# [ ] get_user_created_date(user_id: int) -> Optional[datetime]
# [ ] get_user_last_login(user_id: int) -> Optional[datetime]
# [ ] is_user_disabled(user_id: int) -> bool


# HELPERS

# [ ] user_exists(user_id: int) -> bool
# [ ] username_taken(username: str, exclude_user_id: Optional[int] = None) -> bool
# [ ] email_taken(email: str, exclude_user_id: Optional[int] = None) -> bool
