# TODO: BAND CRUD IMPLEMENTATION

# CREATE
# [ ] create_band(band_data: BandCreate) -> Band
#     - Ensures unique band name before insert
#     - Sets created_at and is_disabled=False by default

# GET
# [ ] get_band_by_id(band_id: int) -> Optional[Band]
# [ ] get_band_by_name(name: str) -> Optional[Band]
# [ ] get_all_bands(skip: int = 0, limit: int = 10) -> List[Band]  # paginated
# [ ] get_all_bands_unpaginated() -> List[Band]  # full list
# [ ] get_active_bands(skip: int = 0, limit: int = 10) -> List[Band]  # paginated, only active bands

# UPDATE
# [ ] update_band(band_id: int, band_data: BandUpdate) -> Optional[Band]
#     - Allows updating name, bio, profile_picture, social_link
#     - Checks for name uniqueness on update

# DEACTIVATION 
# [ ] disable_band(band_id: int) -> bool
#     - Set is_disabled=True, disabled_at=datetime.utcnow()
# [ ] enable_band(band_id: int) -> bool
#     - Set is_disabled=False, disabled_at=None

# DELETE (HARD)
# [ ] delete_band_permanently(band_id: int) -> bool
#     - Fully deletes the Band 

# HELPERS
# [ ] band_exists(band_id: int) -> bool
# [ ] band_name_taken(name: str, exclude_band_id: Optional[int] = None) -> bool
# [ ] get_band_followers_count(band_id: int) -> int
#     - Returns number of followers for a given band, not to be put on this script. 
# [ ] get_band_with_related_entities(band_id: int) -> Optional[Band]
#     - Returns band with related songs, albums, members (eager load to be used)
