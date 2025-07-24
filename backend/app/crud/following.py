# TODO: FOLLOWING CRUD IMPLEMENTATION

# CREATE
# [ ] create_following_for_artist(user_id: int, artist_id: int) -> Following
#     - Ensure user is not already following the artist (enforced by unique constraint)
# [ ] create_following_for_band(user_id: int, band_id: int) -> Following
#     - Ensure user is not already following the band (enforced by unique constraint)

# GET
# [ ] get_following_by_id(following_id: int) -> Optional[Following]
# [ ] get_all_followings_of_user(user_id: int, skip: int = 0, limit: int = 50) -> List[Following]
# [ ] get_followings_of_user_artists(user_id: int, skip: int = 0, limit: int = 50) -> List[Following]
# [ ] get_followings_of_user_bands(user_id: int, skip: int = 0, limit: int = 50) -> List[Following]
# [ ] get_all_followers_of_artist(artist_id: int, skip: int = 0, limit: int = 50) -> List[Following]
# [ ] get_all_followers_of_band(band_id: int, skip: int = 0, limit: int = 50) -> List[Following]

# DELETE
# [ ] delete_following_artist(user_id: int, artist_id: int) -> bool
#     - Allow a user to unfollow an artist
# [ ] delete_following_band(user_id: int, band_id: int) -> bool
#     - Allow a user to unfollow a band
# [ ] delete_following_by_id(following_id: int) -> bool

# CHECK
# [ ] is_user_following_artist(user_id: int, artist_id: int) -> bool
# [ ] is_user_following_band(user_id: int, band_id: int) -> bool

# HELPERS 
# [ ] count_followers_of_artist(artist_id: int) -> int
# [ ] count_followers_of_band(band_id: int) -> int
# [ ] count_followings_of_user(user_id: int) -> int

# REPORTS
# [ ] get_recent_followings_of_user(user_id: int, limit: int = 10) -> List[Following]
# [ ] get_recent_followers_of_artist_or_band(entity_type: str, entity_id: int, limit: int = 10) -> List[Following]
#     - entity_type can be "artist" or "band" to handle both cases
