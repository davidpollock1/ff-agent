from fastapi import APIRouter, Request, Form, status, Depends, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from app.models.models import User
from app.db.session import get_session
import bcrypt
import secrets


templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

SESSION_COOKIE = "session"
SESSION_SECRET = secrets.token_urlsafe(32)


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_session_cookie(user_id: int) -> str:
    # need to update for prod.
    return str(user_id)


def get_user_from_session(request: Request, session: Session) -> User | None:
    user_id = request.cookies.get(SESSION_COOKIE)
    if not user_id:
        return None
    return session.get(User, int(user_id))


@router.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/signup")
def signup(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
) -> Response:
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        return HTMLResponse("Email already registered", status_code=400)
    user = User(email=email, hashed_password=get_password_hash(password))
    session.add(user)
    session.commit()
    session.refresh(user)
    response = RedirectResponse("/signin", status_code=status.HTTP_302_FOUND)
    return response


@router.get("/signin", response_class=HTMLResponse)
def signin_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("signin.html", {"request": request})


@router.post("/signin")
def signin(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
) -> Response:
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.hashed_password):
        return HTMLResponse("Invalid credentials", status_code=400)
    resp = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    resp.set_cookie(
        SESSION_COOKIE, create_session_cookie(user.id), httponly=True, secure=True
    )
    return resp


@router.get("/signout")
def signout(response: Response) -> Response:
    resp = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    resp.delete_cookie(SESSION_COOKIE)
    return resp
