"""
Streaming API endpoints for serving audio files and images.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pathlib import Path
import os
import mimetypes
from typing import Optional

from app.core.deps import get_db
from app.db.models.song import Song
from app.services.file_service import file_service

router = APIRouter()

@router.get("/song/{song_id}")
async def stream_song(
    song_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Stream audio file with range request support for seeking.
    """
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    if not song.file_path or not os.path.exists(song.file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    file_path = Path(song.file_path)
    
    file_size = os.path.getsize(file_path)
    
    range_header = request.headers.get("range")
    if range_header:
        try:
            range_str = range_header.replace("bytes=", "")
            start, end = range_str.split("-")
            start = int(start)
            end = int(end) if end else file_size - 1
            
            if start >= file_size or end >= file_size or start > end:
                raise HTTPException(status_code=416, detail="Range not satisfiable")
            
            content_length = end - start + 1
            
            with open(file_path, "rb") as f:
                f.seek(start)
                chunk = f.read(content_length)
            
            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(content_length),
                "Content-Type": "audio/mpeg",
                "Cache-Control": "public, max-age=31536000"
            }
            
            return Response(content=chunk, headers=headers, status_code=206)
            
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="Invalid range header")
    
    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=31536000"
        }
    )

@router.get("/cover/{filename}")
async def stream_cover_image(filename: str):
    """
    Serve song/album cover images.
    """
    file_path = Path("uploads/covers") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Cover image not found")
    
    content_type, _ = mimetypes.guess_type(str(file_path))
    if not content_type:
        content_type = "image/jpeg"
    
    return FileResponse(
        path=file_path,
        media_type=content_type,
        headers={
            "Cache-Control": "public, max-age=31536000"
        }
    )

@router.get("/album/{filename}")
async def stream_album_image(filename: str):
    """
    Serve album cover images.
    """
    file_path = Path("uploads/albums") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Album image not found")
    
    content_type, _ = mimetypes.guess_type(str(file_path))
    if not content_type:
        content_type = "image/jpeg"
    
    return FileResponse(
        path=file_path,
        media_type=content_type,
        headers={
            "Cache-Control": "public, max-age=31536000"
        }
    )

@router.get("/profile/{filename}")
async def stream_profile_image(filename: str):
    """
    Serve user/artist/band profile images.
    """
    file_path = Path("uploads/profiles") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Profile image not found")
    
    content_type, _ = mimetypes.guess_type(str(file_path))
    if not content_type:
        content_type = "image/jpeg"
    
    return FileResponse(
        path=file_path,
        media_type=content_type,
        headers={
            "Cache-Control": "public, max-age=31536000"
        }
    )

@router.get("/song/{song_id}/info")
async def get_song_file_info(song_id: int, db: Session = Depends(get_db)):
    """
    Get information about a song's audio file.
    """
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    if not song.file_path or not os.path.exists(song.file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    file_path = Path(song.file_path)
    
    file_size = os.path.getsize(file_path)
    file_stat = os.stat(file_path)
    
    content_type, _ = mimetypes.guess_type(str(file_path))
    if not content_type:
        content_type = "audio/mpeg"
    
    return {
        "song_id": song_id,
        "title": song.title,
        "file_path": str(file_path),
        "file_size": file_size,
        "file_size_mb": round(file_size / (1024 * 1024), 2),
        "content_type": content_type,
        "created_at": file_stat.st_ctime,
        "modified_at": file_stat.st_mtime,
        "duration": song.song_duration,
        "stream_url": f"/stream/song/{song_id}"
    }
