from typing import Annotated
from fastapi import Depends
from db.session import get_session
from sqlmodel import Session


SessionDep = Annotated[Session, Depends(get_session)]
