# TODO: PLAYLIST CRUD IMPLEMENTATION

# CREATE
# [ ] create_playlist(data: PlaylistCreate, owner_id: int) -> Playlist
#     - Enforce (owner_id, name) uniqueness
#     - Set created_at

# GET
# [ ] get_playlist_by_id(playlist_id: int) -> Optional[Playlist]
# [ ] get_user_playlists(owner_id: int, skip: int = 0, limit: int = 20) -> List[Playlist]
# [ ] search_user_playlists(owner_id: int, keyword: str, skip: int = 0, limit: int = 20) -> List[Playlist]
#     - Search by playlist name or description

# UPDATE
# [ ] update_playlist_info(playlist_id: int, name: Optional[str], description: Optional[str]) -> Optional[Playlist]
#     - Validate new name uniqueness

# DELETE
# [ ] delete_playlist(playlist_id: int, requesting_user_id: int) -> bool


# HELPERS
# [ ] user_can_edit_playlist(user_id: int, playlist_id: int) -> bool
#     - Returns true if user is owner or collaborator


