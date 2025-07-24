# TODO: HISTORY CRUD IMPLEMENTATION

# CREATE
# [ ] create_history_entry(user_id: int, song_id: int) -> History
#     - Automatically sets `played_at` to current UTC time
#     - prevent spamming by checking if same user played same song within short time (120 seconds)

# GET
# [ ] get_history_by_id(history_id: int) -> Optional[History]
# [ ] get_user_history(user_id: int, skip: int = 0, limit: int = 50) -> List[History]
#     - Ordered by `played_at` DESC (most recent first)
# [ ] get_recent_plays_of_song(song_id: int, limit: int = 10) -> List[History]
# [ ] get_song_play_history_by_user(user_id: int, song_id: int) -> List[History]

# DELETE - thoughts on archiving instead of deleting - so song play history is preserved
# [ ] delete_history_by_id(history_id: int) -> bool
# [ ] delete_user_history(user_id: int) -> int
#     - Returns number of deleted records

# FILTERING 
# [ ] get_user_history_in_date_range(user_id: int, start: datetime, end: datetime) -> List[History]

# ANALYTICS
# [ ] count_song_plays(song_id: int) -> int
# [ ] count_user_total_plays(user_id: int) -> int
# [ ] count_song_plays_by_user(user_id: int, song_id: int) -> int

# STATS
# [ ] get_most_played_songs_by_user(user_id: int, limit: int = 10) -> List[Tuple[Song, int]]
# [ ] get_most_active_users(limit: int = 10) -> List[Tuple[User, int]]
# [ ] get_global_top_songs(limit: int = 10) -> List[Tuple[Song, int]]
