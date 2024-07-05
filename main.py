from database import engine
from fastapi import FastAPI 
from models.base import Base
from routes import auth
from routes import song

app = FastAPI()

app.include_router(auth.router, prefix= '/auth')
app.include_router(song.router, prefix= '/song')


Base.metadata.create_all(engine)