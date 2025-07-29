# TODO: LIKE CRUD IMPLEMENTATION

# CREATE
# [ ] like_song(user_id: int, song_id: int) -> Like
#     - Check if already liked; if so, raise 409 Conflict
#     - Auto-fills `liked_at` as current UTC time

# GET
# [ ] get_like_by_id(like_id: int) -> Optional[Like]
# [ ] get_user_likes(user_id: int, skip: int = 0, limit: int = 50) -> List[Like]
#     - Recent likes first (order by `liked_at` DESC)
# [ ] get_users_who_liked_song(song_id: int) -> List[User] //is it needed?
# [ ] is_song_liked_by_user(user_id: int, song_id: int) -> bool //helper?

# DELETE
# [ ] unlike_song(user_id: int, song_id: int) -> bool
#     - Deletes if exists, else returns False

# COUNTING
# [ ] count_song_likes(song_id: int) -> int
# [ ] count_user_likes(user_id: int) -> int

# STATS
# [ ] get_top_liked_songs(limit: int = 10) -> List[Tuple[Song, int]]

