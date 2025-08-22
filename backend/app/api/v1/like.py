from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_active_user, get_current_admin
from app.db.models.user import User
from app.schemas.like import (
    LikeOut, LikeList, LikeToggle, LikeStats, UserLikesSummary, 
    LikeWithSong, LikeListWithSongs, SongMinimal
)
from app.crud.like import (
    get_like_by_id, get_user_likes, get_user_likes_with_songs, is_song_liked_by_user, toggle_like, 
    count_song_likes, count_user_likes, get_top_liked_songs, 
    get_like_statistics, get_user_likes_summary
)
from app.crud.song import get_song_by_id


router = APIRouter()



@router.get("/song/{song_id}/count", tags=["likes"])
async def get_song_like_count(
    song_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the total number of likes for a song (Public).
    Returns only the count, not individual user data.
    """
    song = get_song_by_id(db, song_id)
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    count = count_song_likes(db, song_id)
    return {"song_id": song_id, "like_count": count}


@router.get("/top-songs", tags=["likes"])
async def get_top_liked_songs_endpoint(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get top liked songs (Public).
    Returns the most liked songs in the system (aggregated data only).
    """
    top_songs = get_top_liked_songs(db, limit=limit)
    return [
        {
            "song": {
                "id": song.id,
                "title": song.title,
                "artist_name": song.artist_name,
                "band_name": song.band_name,
                "cover_image": song.cover_image
            },
            "like_count": count
        }
        for song, count in top_songs
    ]



@router.post("/toggle", response_model=dict, tags=["likes"])
async def toggle_like_endpoint(
    like_data: LikeToggle,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Toggle like status for a song (Authenticated users).
    Likes the song if not liked, unlikes if already liked.
    """
    song = get_song_by_id(db, like_data.song_id)
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    like, was_created = toggle_like(db, current_user.id, like_data.song_id)
    
    return {
        "message": "Song liked" if was_created else "Song unliked",
        "song_id": like_data.song_id,
        "user_id": current_user.id,
        "was_created": was_created,
        "like_count": count_song_likes(db, like_data.song_id)
    }


@router.get("/song/{song_id}/is-liked", tags=["likes"])
async def check_song_liked_status(
    song_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check if current user has liked a specific song (Authenticated users).
    Returns whether the current user has liked the specified song.
    """
    song = get_song_by_id(db, song_id)
    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Song not found"
        )
    
    is_liked = is_song_liked_by_user(db, current_user.id, song_id)
    return {
        "song_id": song_id,
        "user_id": current_user.id,
        "is_liked": is_liked
    }


@router.get("/user/me", response_model=LikeListWithSongs, tags=["likes"])
async def get_my_likes(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    search: Optional[str] = Query(default=None, description="Search songs by title"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's likes with full song details (Authenticated users).
    Returns a paginated list of songs liked by the current user with song title, image, etc.
    Perfect for Flutter widgets displaying liked songs.
    """
    likes_with_songs = get_user_likes_with_songs(
        db, current_user.id, skip=skip, limit=limit, search=search
    )
    
    likes = []
    for like, song in likes_with_songs:
        like_with_song = LikeWithSong(
            id=like.id,
            user_id=like.user_id,
            song_id=like.song_id,
            liked_at=like.liked_at,
            song=SongMinimal(
                id=song.id,
                title=song.title,
                song_duration=song.song_duration,
                cover_image=song.cover_image,
                artist_name=song.artist_name,
                band_name=song.band_name
            )
        )
        likes.append(like_with_song)
    
    if search:
        total = len(likes_with_songs)
    else:
        total = count_user_likes(db, current_user.id)
    
    return LikeListWithSongs(
        likes=likes,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        total_pages=(total + limit - 1) // limit
    )


@router.get("/user/me/summary", response_model=UserLikesSummary, tags=["likes"])
async def get_my_likes_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's likes summary (Authenticated users).
    Returns a summary of the current user's likes including favorite artists and genres.
    """
    summary = get_user_likes_summary(db, current_user.id)
    return UserLikesSummary(**summary)




@router.get("/admin/statistics", response_model=LikeStats, tags=["likes"])
async def get_like_statistics_admin(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get overall like statistics (Admin only).
    Returns comprehensive statistics about likes in the system.
    """
    stats = get_like_statistics(db)
    return LikeStats(**stats)




