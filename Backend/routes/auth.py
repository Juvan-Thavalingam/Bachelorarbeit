from fastapi import APIRouter, HTTPException
import os

router = APIRouter()

PASSWORD_FILE = "keys/password.txt"

@router.get("/api/admin-password")
def get_admin_password():
    try:
        with open(PASSWORD_FILE, "r", encoding="utf-8") as f:
            return {"password": f.read().strip()}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Passwortdatei nicht gefunden.")
