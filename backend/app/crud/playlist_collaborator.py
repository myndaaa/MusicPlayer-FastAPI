# TODO: PLAYLIST COLLABORATOR CRUD IMPLEMENTATION

# CREATE
# [ ] add_collaborator_to_playlist(playlist_id: int, collaborator_id: int, added_by_user_id: int,can_edit: bool = False) -> PlaylistCollaborator
#     - Check if already exists → raise 409 Conflict
#     - Check that added_by_user_id is owner of playlist
#     - Save with added_at timestamp

# READ
# [ ] get_collaborator_entry(playlist_id: int, user_id: int) -> Optional[PlaylistCollaborator]
# [ ] get_playlist_collaborators(playlist_id: int) -> List[PlaylistCollaborator]

# UPDATE
# [ ] update_collaborator_permissions(playlist_id: int, collaborator_id: int, can_edit: bool) -> PlaylistCollaborator
#     - Only allowed if current user is playlist owner

# DELETE
# [ ] remove_collaborator_from_playlist(playlist_id: int,collaborator_id: int) -> bool
#     - only owner can remove others

# PERMISSION
# [ ] is_user_playlist_editor(user_id: int, playlist_id: int) -> bool
# [ ] is_user_playlist_owner_or_editor(user_id: int, playlist_id: int) -> bool
