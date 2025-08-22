# TODO: SONG CRUD IMPLEMENTATION

# CREATE
# [ ] create_song(song_data: SongCreate, uploaded_by_user_id: int) -> Song
#     - Validate genre, artist/band IDs/User ID (admin) exist 
#     - Check user permissions (e.g., only verified users can upload?)
#     - Enforce required logic:
#         - Either artist_id or band_id or admins user ID should be set 
#         - artist_name and band_name should be fetched from related tables. if admin is uploading either artist_name or band_name should be set
#     - Auto-fill `uploaded_at` as current UTC time 


# READ
# [ ] get_song_by_id(song_id: int) -> Optional[Song]
#     - Include relationships (genre, artist, band)
#
# [ ] get_all_songs_paginated(skip: int = 0, limit: int = 20) -> List[Song]
#
# [ ] search_songs_by_title(title: str, skip: int = 0, limit: int = 20) -> List[Song]
#     - `ilike` for case-insensitive partial search
#
# [ ] get_songs_by_artist(artist_id: int, skip: int = 0, limit: int = 20) -> List[Song]
# [ ] get_songs_by_band(band_id: int, skip: int = 0, limit: int = 20) -> List[Song]
# [ ] get_songs_by_genre(genre_id: int, skip: int = 0, limit: int = 20) -> List[Song]


# UPDATE
# song update not allowed, only admin can update song file_path
# [ ] update_song_file_path(song_id: int, new_file_path: str, by_user_id: int) -> Song
#     - Only admin can update file_path
#     - Check if song exists
#     - Update `file_path` and `updated_at` timestamp


# HARD DELETE 
# [ ] delete_song_permanently(song_id: int) -> bool

