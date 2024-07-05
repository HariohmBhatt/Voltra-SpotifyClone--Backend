import uuid
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from database import get_db
from middleware.auth_middleware import auth_middleware
import cloudinary
import cloudinary.uploader
from sqlalchemy.orm import joinedload

from models.favorite import Favorite
from models.songs import Song
from pydantic_schemas.favorite_song import FavouriteSong

router = APIRouter()

cloudinary.config( 
    cloud_name = "dlbz15bzl", 
    api_key = "888342413836319", 
    api_secret = "tDupC0h_PadXOshc-GJmrz7GyWE", # Click 'View Credentials' below to copy your API secret
    secure=True
)


@router.post('/upload', status_code= 201)
def upload_song (
    song: UploadFile = File(...), 
    thumbnail: UploadFile = File(...), 
    artist: str = Form(...), 
    songname: str = Form(...), 
    hex_code: str = Form(...),
    db: Session = Depends(get_db),
    auth_dict = Depends(auth_middleware)
) :
    song_id = str(uuid.uuid4())
    song_res = cloudinary.uploader.upload(song.file, resource_type = 'auto', folder = f'songs/{song_id}')
    thumbnail_res = cloudinary.uploader.upload(thumbnail.file, resource_type = 'image', folder = f'songs/{song_id}')
    
    new_song = Song(
        id = song_id,
        song_name = songname,
        artist = artist,
        hex_code = hex_code,
        song_url = song_res['url'],
        thumbnail_url = thumbnail_res['url']
    )
    
    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    
    return new_song

@router.get('/list')
def list_songs(db: Session = Depends(get_db), auth_dict = Depends(auth_middleware)):
    songs = db.query(Song).all()
    
    return songs

@router.post('/favourite')
def favourite_song(song: FavouriteSong, 
                    db: Session = Depends(get_db), 
                    auth_dict = Depends(auth_middleware)):
    user_id = auth_dict['uid']
    
    try:
        fav_song = db.query(Favorite).filter(
            Favorite.song_id == song.song_id,
            Favorite.user_id == user_id
        ).first()
        
        if fav_song:
            db.delete(fav_song)
            db.commit()
            return {'message': False}
        else: 
            new_fav_song = Favorite(id=str(uuid.uuid4()), song_id=song.song_id, user_id=user_id)
            db.add(new_fav_song)
            db.commit()
            return {'message': True}
    except Exception as e:
        db.rollback()
        # Log the error here
        return {'error': 'An error occurred while processing your request'}, 500
    
@router.get('/list/favourites')
def list_fav_songs(db: Session = Depends(get_db), auth_dict = Depends(auth_middleware)):
    user_id = auth_dict['uid']
    fav_songs = db.query(Favorite).options(
            joinedload(Favorite.song)
        ).filter(
            Favorite.user_id == user_id
        ).all()
    return fav_songs