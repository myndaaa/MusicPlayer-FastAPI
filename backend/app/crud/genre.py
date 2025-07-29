# TODO: GENRE CRUD IMPLEMENTATION

# CREATE
# [ ] create_genre(genre_data: GenreCreate) -> Genre
#     - Ensures unique genre name before insert
#     - Set created_at, is_active=True by default

# READ / GET
# [ ] get_genre_by_id(genre_id: int) -> Optional[Genre]
# [ ] get_genre_by_name(name: str) -> Optional[Genre]
# [ ] get_all_genres() -> List[Genre]  # no pagination needed, small list 
# [ ] get_all_active_genres() -> List[Genre]

# UPDATE
# [ ] update_genre(genre_id: int, data: GenreUpdate) -> Optional[Genre]
#     - Allows updating name and description
#     - Check uniqueness of name on update

# DEACTIVATION 
# [ ] disable_genre(genre_id: int) -> bool
#     - Set is_active=False, disabled_at=datetime.utcnow()
# [ ] enable_genre(genre_id: int) -> bool
#     - Set is_active=True, disabled_at=None

# HELPERS
# [ ] genre_exists(genre_id: int) -> bool
# [ ] genre_name_taken(name: str, exclude_genre_id: Optional[int] = None) -> bool
