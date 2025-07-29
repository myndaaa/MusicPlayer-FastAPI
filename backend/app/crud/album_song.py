# TODO: ALBUMSONG CRUD IMPLEMENTATION

# CREATE
# [ ] create_album_song(album_song_data: AlbumSongCreate) -> AlbumSong
#     - Ensure unique track_number per album (check uniqueness before insert)
#     - Validate album_id and song_id exist

# GET
# [ ] get_album_song_by_id(album_song_id: int) -> Optional[AlbumSong]
# [ ] get_album_songs_by_album(album_id: int) -> List[AlbumSong]
# [ ] get_all_album_songs(skip: int = 0, limit: int = 20) -> List[AlbumSong]  # paginated for admins

# UPDATE
# [ ] update_album_song(album_song_id: int, data: AlbumSongUpdate) -> Optional[AlbumSong]
#     - Allow updating track_number
#     - On track_number update, check uniqueness within album

# DELETE
# [ ] delete_album_song(album_song_id: int) -> bool
#     - Delete by ID, return success/failure

# HELPERS
# [ ] album_song_exists(album_song_id: int) -> bool
# [ ] is_track_number_taken(album_id: int, track_number: int, exclude_id: Optional[int] = None) -> bool
#     - Check if a track number already exists for the album, excluding the current record

