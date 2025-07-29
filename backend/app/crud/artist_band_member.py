# TODO: ARTIST BAND MEMBER CRUD IMPLEMENTATION

# CREATE
# [ ] create_artist_band_member(data: ArtistBandMemberCreate) -> ArtistBandMember
#     - Ensure artist_id and band_id exist
#     - Validate no overlapping membership periods for same artist & band
#     - joined_on to now by default, is_current_member=True

# GET
# [ ] get_artist_band_member_by_id(band_member_id: int) -> Optional[ArtistBandMember]
# [ ] get_memberships_by_artist(artist_id: int, skip: int = 0, limit: int = 20) -> List[ArtistBandMember]
# [ ] get_memberships_by_band(band_id: int, skip: int = 0, limit: int = 20) -> List[ArtistBandMember]
# [ ] get_current_members_by_band(band_id: int) -> List[ArtistBandMember]
# [ ] get_current_bands_for_artist(artist_id: int) -> List[ArtistBandMember]

# UPDATE
# [ ] update_artist_band_member(band_member_id: int, data: ArtistBandMemberUpdate) -> Optional[ArtistBandMember]
#     - Allow updating left_at, is_current_member
#     - Automatically set is_current_member=False if left_at is set


# HELPERS 
# [ ] membership_exists(band_member_id: int) -> bool
# [ ] validate_artist_exists(artist_id: int) -> bool
# [ ] validate_band_exists(band_id: int) -> bool
# [ ] check_no_overlap_membership(artist_id: int, band_id: int, joined_on: datetime, left_at: Optional[datetime]) -> bool
