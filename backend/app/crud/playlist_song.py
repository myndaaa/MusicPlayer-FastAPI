# TODO: PLAYLIST SONG CRUD IMPLEMENTATION

# ADD (CREATE)
# [ ] add_song_to_playlist(playlist_id: int, song_id: int, order: Optional[int], added_by_user_id: int) -> PlaylistSong
#     - Prevent duplicates: playlist_id + song_id should be unique
#     - Auto-calculate order if not provided (append to end)

# READ
# [ ] get_songs_in_playlist(playlist_id: int, include_disabled: bool = False) -> List[Song]
#     - JOIN with `Song` and return ordered list (sorted by `song_order`)

# [ ] get_playlist_song_entry(playlist_id: int, song_id: int) -> Optional[PlaylistSong]
#     - To check if a song is already added


# DELETE (REMOVE SONG)
# [ ] remove_song_from_playlist(playlist_id: int, song_id: int) -> bool
# DELETE ALL (on playlist delete, cascades automatically, no manual cleanup needed)


# [ ] reorder_playlist(playlist_id: int, song_ids_in_order: List[int]) -> None
#     - Bulk update song_order to match given order
#
# [ ] clear_playlist(playlist_id: int) -> int
#     - Delete all PlaylistSong entries for a playlist
