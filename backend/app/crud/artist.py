# TODO: ARTIST CRUD IMPLEMENTATION

# CREATE
# [ ] create_artist(artist_data: ArtistCreate, user_id: int) -> Artist
#     - Ensure the user ID exists and isn’t already linked to another artist
#     - Set created_at automatically

# GET
# [ ] get_artist_by_id(artist_id: int) -> Optional[Artist]
# [ ] get_artist_by_user_id(user_id: int) -> Optional[Artist]
# [ ] get_artist_by_stage_name(name: str) -> Optional[Artist]
# [ ] get_all_artists(skip: int = 0, limit: int = 10) -> List[Artist]
# [ ] get_all_active_artists(skip: int = 0, limit: int = 10) -> List[Artist]
# [ ] get_all_artists_unpaginated() -> List[Artist]
# [ ] search_artists_by_name(keyword: str, skip: int = 0, limit: int = 10) -> List[Artist]
#     - Case insensitive

# UPDATE
# [ ] update_artist(artist_id: int, data: ArtistUpdate) -> Optional[Artist]
#     - Allow updating: stage name, bio, profile image, social links
#     - Prevents changing linked user

# DEACTIVATION / ACTIVATION
# [ ] disable_artist(artist_id: int) -> bool
#     - Set is_disabled = True, disabled_at = datetime.now()
# [ ] enable_artist(artist_id: int) -> bool
#     - Set is_disabled = False, disabled_at = None

# DELETE 
# [ ] delete_artist(artist_id: int) -> bool
#     - Only allow if cascade-safe

# HELPERS
# [ ] artist_exists(artist_id: int) -> bool
# [ ] is_user_already_an_artist(user_id: int) -> bool
# [ ] stage_name_taken(name: str, exclude_artist_id: Optional[int] = None) -> bool

# ADVANCED QUERIES
# [ ] get_artist_with_related_entities(artist_id: int) -> Optional[Artist]
#     - Eager load: songs, albums, followers, band memberships
# [ ] get_artists_followed_by_user(user_id: int, skip: int = 0, limit: int = 10) -> List[Artist]
#     - Joins through `Following` model (to be implemented on following model, putting here for reference for now)
