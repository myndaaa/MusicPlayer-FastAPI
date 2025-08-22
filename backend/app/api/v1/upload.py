"""
Upload API endpoints for file uploads and combined creation/upload operations.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import tempfile
import os
from pathlib import Path

from app.core.deps import get_db, get_current_user, get_current_admin, get_current_musician
from app.db.models.user import User
from app.db.models.artist import Artist
from app.db.models.band import Band
from app.db.models.album import Album
from app.db.models.song import Song
from app.crud.song import create_song_by_artist, create_song_by_band, create_song_by_admin
from app.crud.album import create_album, update_album
from app.crud.band import create_band, update_band
from app.crud.artist import update_artist
from app.services.file_service import file_service
from app.schemas.song_upload import (
    SongCreateWithUpload, SongCreateWithUploadByArtist, 
    SongCreateWithUploadByBand, SongCreateWithUploadByAdmin,
    SongUploadResponse
)
from app.schemas.album import AlbumCreate, AlbumUpdate
from app.schemas.band import BandCreate, BandUpdate
from app.schemas.artist import ArtistUpdate
from app.schemas.upload import FileUploadResponse, AudioUploadResponse, ImageUploadResponse

router = APIRouter()


@router.post("/song/artist", response_model=SongUploadResponse)
async def create_song_with_upload_by_artist(
    audio_file: UploadFile = File(...),
    title: str = Form(...),
    genre_id: int = Form(...),
    artist_id: int = Form(...),
    release_date: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_musician)
):
    """
    Create song and upload audio file as artist.
    Combines song creation and file upload in one operation.
    """
    try:
        if not audio_file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.filename).suffix) as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_path = Path(temp_file.name)
        
        is_valid, error_msg = file_service.validate_audio_file(temp_path, audio_file.content_type)
        if not is_valid:
            os.unlink(temp_path)
            raise HTTPException(status_code=400, detail=error_msg)
        
        metadata = file_service.get_audio_metadata(temp_path)
        
        song_data = SongCreateWithUploadByArtist(
            title=title,
            genre_id=genre_id,
            artist_id=artist_id,
            release_date=release_date,
            song_duration=metadata.get("duration", 0),
            file_path="",  # Will be set after file save
            cover_image=None
        )
        
        song = create_song_by_artist(db, song_data, current_user.id)
        
        filename = file_service.generate_unique_filename(audio_file.filename, song.id, "song")
        destination_path = Path("uploads/songs") / filename
        
        success = await file_service.save_uploaded_file(temp_path, destination_path)
        if not success:
            db.delete(song)
            db.commit()
            raise HTTPException(status_code=500, detail="Failed to save file")
        
        song.file_path = str(destination_path)
        db.commit()
        db.refresh(song)
        
        return SongUploadResponse(
            song_id=song.id,
            title=song.title,
            filename=filename,
            stream_url=f"/stream/song/{song.id}",
            duration=metadata.get("duration", 0),
            file_size=temp_path.stat().st_size,
            message="Song created and uploaded successfully"
        )
        
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass  # File might already be deleted
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/song/band", response_model=SongUploadResponse)
async def create_song_with_upload_by_band(
    audio_file: UploadFile = File(...),
    title: str = Form(...),
    genre_id: int = Form(...),
    band_id: int = Form(...),
    release_date: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_musician)
):
    """
    Create song and upload audio file as band member.
    Combines song creation and file upload in one operation.
    """
    try:
        if not audio_file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.filename).suffix) as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_path = Path(temp_file.name)
        
        is_valid, error_msg = file_service.validate_audio_file(temp_path, audio_file.content_type)
        if not is_valid:
            os.unlink(temp_path)
            raise HTTPException(status_code=400, detail=error_msg)
        
        metadata = file_service.get_audio_metadata(temp_path)
        
        song_data = SongCreateWithUploadByBand(
            title=title,
            genre_id=genre_id,
            band_id=band_id,
            release_date=release_date,
            song_duration=metadata.get("duration", 0),
            file_path="",  # Will be set after file save
            cover_image=None
        )
        
        song = create_song_by_band(db, song_data, current_user.id)
        
        filename = file_service.generate_unique_filename(audio_file.filename, song.id, "song")
        destination_path = Path("uploads/songs") / filename
        
        success = await file_service.save_uploaded_file(temp_path, destination_path)
        if not success:
            db.delete(song)
            db.commit()
            raise HTTPException(status_code=500, detail="Failed to save file")
        
        song.file_path = str(destination_path)
        db.commit()
        db.refresh(song)
        
        return SongUploadResponse(
            song_id=song.id,
            title=song.title,
            filename=filename,
            stream_url=f"/stream/song/{song.id}",
            duration=metadata.get("duration", 0),
            file_size=temp_path.stat().st_size,
            message="Song created and uploaded successfully"
        )
        
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass  # File might already be deleted
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/song/admin", response_model=SongUploadResponse)
async def create_song_with_upload_by_admin(
    audio_file: UploadFile = File(...),
    title: str = Form(...),
    genre_id: int = Form(...),
    artist_id: Optional[int] = Form(None),
    band_id: Optional[int] = Form(None),
    artist_name: Optional[str] = Form(None),
    band_name: Optional[str] = Form(None),
    release_date: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Create song and upload audio file as admin.
    Combines song creation and file upload in one operation.
    """
    try:
        if not audio_file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.filename).suffix) as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_path = Path(temp_file.name)
        
        is_valid, error_msg = file_service.validate_audio_file(temp_path, audio_file.content_type)
        if not is_valid:
            os.unlink(temp_path)
            raise HTTPException(status_code=400, detail=error_msg)
        
        metadata = file_service.get_audio_metadata(temp_path)
        
        song_data = SongCreateWithUploadByAdmin(
            title=title,
            genre_id=genre_id,
            artist_id=artist_id,
            band_id=band_id,
            artist_name=artist_name,
            band_name=band_name,
            release_date=release_date,
            song_duration=metadata.get("duration", 0),
            file_path="",  # Will be set after file save
            cover_image=None
        )
        
        song = create_song_by_admin(db, song_data, current_user.id)
        
        filename = file_service.generate_unique_filename(audio_file.filename, song.id, "song")
        destination_path = Path("uploads/songs") / filename
        
        success = await file_service.save_uploaded_file(temp_path, destination_path)
        if not success:
            db.delete(song)
            db.commit()
            raise HTTPException(status_code=500, detail="Failed to save file")
        
        song.file_path = str(destination_path)
        db.commit()
        db.refresh(song)
        
        return SongUploadResponse(
            song_id=song.id,
            title=song.title,
            filename=filename,
            stream_url=f"/stream/song/{song.id}",
            duration=metadata.get("duration", 0),
            file_size=temp_path.stat().st_size,
            message="Song created and uploaded successfully"
        )
        
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass  # File might already be deleted
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/album", response_model=dict)
async def create_album_with_cover(
    cover_file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    album_artist_id: Optional[int] = Form(None),
    album_band_id: Optional[int] = Form(None),
    artist_name: Optional[str] = Form(None),
    band_name: Optional[str] = Form(None),
    release_date: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_musician)
):
    """
    Create album and upload cover image.
    Combines album creation and cover upload in one operation.
    """
    try:
        if not cover_file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(cover_file.filename).suffix) as temp_file:
            content = await cover_file.read()
            temp_file.write(content)
            temp_path = Path(temp_file.name)
        
        is_valid, error_msg = file_service.validate_image_file(temp_path, cover_file.content_type)
        if not is_valid:
            os.unlink(temp_path)
            raise HTTPException(status_code=400, detail=error_msg)
        
        album_data = AlbumCreate(
            title=title,
            description=description,
            cover_image="",  # Will be set after file save
            release_date=release_date,
            album_artist_id=album_artist_id,
            album_band_id=album_band_id,
            artist_name=artist_name,
            band_name=band_name
        )
        
        album = create_album(db, album_data, current_user.id)
        
        filename = file_service.generate_unique_filename(cover_file.filename, album.id, "album")
        destination_path = Path("uploads/albums") / filename
        
        success = await file_service.save_uploaded_file(temp_path, destination_path)
        if not success:
            db.delete(album)
            db.commit()
            raise HTTPException(status_code=500, detail="Failed to save file")
        
        album.cover_image = str(destination_path)
        db.commit()
        db.refresh(album)
        
        return {
            "album_id": album.id,
            "title": album.title,
            "cover_filename": filename,
            "cover_url": f"/stream/album/{filename}",
            "message": "Album created and cover uploaded successfully"
        }
        
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass  # File might already be deleted
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/band", response_model=dict)
async def create_band_with_profile(
    profile_file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    formed_date: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_musician)
):
    """
    Create band and upload profile image.
    Combines band creation and profile upload in one operation.
    """
    try:
        if not profile_file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(profile_file.filename).suffix) as temp_file:
            content = await profile_file.read()
            temp_file.write(content)
            temp_path = Path(temp_file.name)
        
        is_valid, error_msg = file_service.validate_image_file(temp_path, profile_file.content_type)
        if not is_valid:
            os.unlink(temp_path)
            raise HTTPException(status_code=400, detail=error_msg)
        
        band_data = BandCreate(
            name=name,
            description=description,
            profile_picture="",  # Will be set after file save
            formed_date=formed_date
        )
        
        band = create_band(db, band_data, current_user.id)
        
        filename = file_service.generate_unique_filename(profile_file.filename, band.id, "band")
        destination_path = Path("uploads/profiles") / filename
        
        success = await file_service.save_uploaded_file(temp_path, destination_path)
        if not success:
            db.delete(band)
            db.commit()
            raise HTTPException(status_code=500, detail="Failed to save file")
        
        band.profile_picture = str(destination_path)
        db.commit()
        db.refresh(band)
        
        return {
            "band_id": band.id,
            "name": band.name,
            "profile_filename": filename,
            "profile_url": f"/stream/profile/{filename}",
            "message": "Band created and profile uploaded successfully"
        }
        
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass  # File might already be deleted
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/artist/profile", response_model=dict)
async def upload_artist_profile(
    profile_file: UploadFile = File(...),
    artist_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload profile image for existing artist.
    """
    try:
        if not profile_file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(profile_file.filename).suffix) as temp_file:
            content = await profile_file.read()
            temp_file.write(content)
            temp_path = Path(temp_file.name)
        
        is_valid, error_msg = file_service.validate_image_file(temp_path, profile_file.content_type)
        if not is_valid:
            os.unlink(temp_path)
            raise HTTPException(status_code=400, detail=error_msg)
        
        artist = db.query(Artist).filter(Artist.id == artist_id).first()
        if not artist:
            os.unlink(temp_path)
            raise HTTPException(status_code=404, detail="Artist not found")
        
        if current_user.role != "admin" and artist.linked_user_account != current_user.id:
            os.unlink(temp_path)
            raise HTTPException(status_code=403, detail="Not authorized to update this artist")
        
        filename = file_service.generate_unique_filename(profile_file.filename, artist.id, "artist")
        destination_path = Path("uploads/profiles") / filename
        
        success = await file_service.save_uploaded_file(temp_path, destination_path)
        if not success:
            os.unlink(temp_path)
            raise HTTPException(status_code=500, detail="Failed to save file")
        
        artist.artist_profile_image = str(destination_path)
        db.commit()
        db.refresh(artist)
        
        return {
            "artist_id": artist.id,
            "artist_name": artist.artist_stage_name,
            "profile_filename": filename,
            "profile_url": f"/stream/profile/{filename}",
            "message": "Artist profile uploaded successfully"
        }
        
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                pass  # File might already be deleted
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/song/cover", response_model=dict)
async def upload_song_cover(
    cover_file: UploadFile = File(...),
    song_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload cover image for existing song.
    """
    try:
        if not cover_file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(cover_file.filename).suffix) as temp_file:
            content = await cover_file.read()
            temp_file.write(content)
            temp_path = Path(temp_file.name)
        
        is_valid, error_msg = file_service.validate_image_file(temp_path, cover_file.content_type)
        if not is_valid:
            os.unlink(temp_path)
            raise HTTPException(status_code=400, detail=error_msg)
        
        song = db.query(Song).filter(Song.id == song_id).first()
        if not song:
            os.unlink(temp_path)
            raise HTTPException(status_code=404, detail="Song not found")
        
        if current_user.role != "admin" and song.uploaded_by_user_id != current_user.id:
            os.unlink(temp_path)
            raise HTTPException(status_code=403, detail="Not authorized to update this song")
        
        filename = file_service.generate_unique_filename(cover_file.filename, song.id, "cover")
        destination_path = Path("uploads/covers") / filename
        
        success = await file_service.save_uploaded_file(temp_path, destination_path)
        if not success:
            os.unlink(temp_path)
            raise HTTPException(status_code=500, detail="Failed to save file")
        
        song.cover_image = str(destination_path)
        db.commit()
        db.refresh(song)
        
        return {
            "song_id": song.id,
            "title": song.title,
            "cover_filename": filename,
            "cover_url": f"/stream/cover/{filename}",
            "message": "Song cover uploaded successfully"
        }
        
    except Exception as e:
        if 'temp_path' in locals():
            os.unlink(temp_path)
        raise HTTPException(status_code=500, detail=str(e))
