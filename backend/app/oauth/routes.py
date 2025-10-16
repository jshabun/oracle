from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User, OAuthToken
from .yahoo_oauth import YahooOAuth
from datetime import datetime, timedelta
import secrets

router = APIRouter(prefix="/auth/yahoo", tags=["auth"])

oauth = YahooOAuth()

@router.get("/login")
async def login():
    state = secrets.token_urlsafe(24)
    return {"auth_url": oauth.auth_url(state), "state": state}

@router.get("/callback")
async def callback(code: str, state: str, db: Session = Depends(get_db)):
    try:
        token = await oauth.exchange_code(code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # upsert user with sub if available in id_token (skipped: verify jwt)
    # simplified: store token only
    user = User(yahoo_sub=state)  # placeholder until id_token parsing is added
    db.add(user)
    db.flush()

    expires_at = datetime.utcnow() + timedelta(seconds=int(token.get("expires_in", 3600)))
    db.add(OAuthToken(
        user_id=user.id,
        access_token=token.get("access_token"),
        refresh_token=token.get("refresh_token"),
        expires_at=expires_at,
        extra=token,
    ))
    db.commit()
    return {"ok": True}