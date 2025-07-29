# TODO: ALBUM CRUD IMPLEMENTATION

# CREATE
# [ ] create_album(album_data: AlbumCreate) -> Album
#     - Nullable artist or band references allowed
#     - Validate artist_id and band_id exist 

# GET
# [ ] get_album_by_id(album_id: int) -> Optional[Album]
# [ ] get_albums_by_artist(artist_id: int, skip: int = 0, limit: int = 20) -> List[Album]
# [ ] get_albums_by_band(band_id: int, skip: int = 0, limit: int = 20) -> List[Album]
# [ ] get_albums_by_title(title: str, skip: int = 0, limit: int = 20) -> List[Album]
# [ ] get_all_albums(skip: int = 0, limit: int = 50) -> List[Album]

# UPDATE
# [ ] update_album(album_id: int, data: AlbumUpdate) -> Optional[Album]
#     - Allow updating title, description, cover_image


# [ ] get_album_with_songs(album_id: int) -> Optional[Album]  # eager load songs, artist, band
# [ ] get_albums_released_between(start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 20) -> List[Album]
# [ ] get_albums_by_artist_name(artist_name: str, skip: int = 0, limit: int = 20) -> List[Album]
# [ ] get_albums_by_band_name(band_name: str, skip: int = 0, limit: int = 20) -> List[Album]

# HELPERS
# [ ] album_exists(album_id: int) -> bool
# [ ] validate_artist_exists(artist_id: int) -> bool
# [ ] validate_band_exists(band_id: int) -> bool
