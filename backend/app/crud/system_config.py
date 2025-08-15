# TODO: SYSTEM CONFIG CRUD IMPLEMENTATION

# CREATE
# [ ] create_config(config_data: SystemConfigCreate, admin_user_id: int) -> SystemConfig
#     - Ensure `config_key` is unique before insert
#     - Set config_updated_by_admin_id = admin_user_id
#     - Set config_updated_at = datetime.utcnow()

# GET
# [ ] get_config_by_key(key: str) -> Optional[SystemConfig]
# [ ] get_all_configs(skip: int = 0, limit: int = 20) -> List[SystemConfig]
# [ ] search_configs_by_keyword(keyword: str, skip: int = 0, limit: int = 10) -> List[SystemConfig]
#     - Search in `config_description`
# [ ] get_config_with_admin(key: str) -> Optional[SystemConfig]
#     - Eager load updated_by_admin for audit display

# UPDATE
# [ ] update_config_value(key: str, new_value: str, admin_user_id: int) -> Optional[SystemConfig]
#     - Update value, updated_by, and updated_at fields

# HELPERS
# [ ] config_key_exists(key: str) -> bool
# [ ] is_config_value_unique(key: str, value: str) -> bool  # only if you want to enforce value uniqueness


