from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from db import fake_users_db
from models import User, UserInDB

authenticate = FastAPI()


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2 = OAuth2PasswordBearer(tokenUrl="token")


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user


def get_current_user(token: str = Depends(oauth2)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@authenticate.post("/token/")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    print(user_dict, "USER DICT")
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    print(user, "USER")
    hashed_password = fake_hash_password(form_data.password)
    print(hashed_password, "FAKE")
    if not hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}


@authenticate.get("/users/me/")
async def read_items(current_user: User = Depends(get_current_active_user)):
    print(current_user, "\n\n\n\n\n\n\n\n")
    return current_user
