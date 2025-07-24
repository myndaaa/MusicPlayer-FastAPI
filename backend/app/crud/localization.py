# TODO: LOCALIZATION CRUD IMPLEMENTATION

# CREATE
# [ ] create_localization(data: LocalizationCreate, updated_by_user_id: int) -> Localization
#     - Enforce uniqueness of (translation_key, language_code) pair
#     - Set updated_by_user_id and updated_at

# GET
# [ ] get_localization_by_id(id: int) -> Optional[Localization]
# [ ] get_localization(translation_key: str, language_code: str) -> Optional[Localization]
# [ ] get_all_localizations(skip: int = 0, limit: int = 20) -> List[Localization]
# [ ] get_all_by_language(language_code: str, skip: int = 0, limit: int = 20) -> List[Localization]
# [ ] search_localizations(keyword: str, skip: int = 0, limit: int = 20) -> List[Localization]
#     - Search in `translation_key` or `translation_value` 
# [ ] get_localization_with_user(id: int) -> Optional[Localization]
#     - Eager load `updated_by_user` to show editor name/email in frontend (for admin dashboard)

# UPDATE
# [ ] update_localization(id: int, new_value: str, updated_by_user_id: int) -> Optional[Localization]
#     - Update `translation_value`, `updated_by_user_id`, and `updated_at`


# HELPERS
# [ ] localization_exists(translation_key: str, language_code: str) -> bool
# [ ] is_translation_key_unique_in_language(translation_key: str, language_code: str) -> bool


