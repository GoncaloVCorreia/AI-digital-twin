import pytest
from sqlalchemy.orm import Session

from app.services.persona_service import PersonaService
from app.models.persona_model import Persona as PersonaModel
from .factories import make_persona_create, make_persona_update


def test_create_and_get_persona(db_session: Session):
    created = PersonaService.create_persona(
        db_session,
        make_persona_create(name="John Persona", age=35),
        creator_id=1, 
    )
    assert created.id is not None

    got = PersonaService.get_persona(db_session, created.id)
    assert got is not None
    assert got.name == "John Persona"
    assert got.age == 35


def test_list_personas_and_search(db_session: Session):
    PersonaService.create_persona(db_session, make_persona_create(name="Ana Dev", location="Lisbon"), creator_id=1)
    PersonaService.create_persona(db_session, make_persona_create(name="Bruno QA", location="Porto"), creator_id=1)
    PersonaService.create_persona(db_session, make_persona_create(name="Carla PM", location="Faro"), creator_id=1)

    # list all
    rows, total = PersonaService.list_personas(db_session, skip=0, limit=10)
    assert total == 3
    assert len(rows) == 3

    # search by name fragment (ilike)
    rows2, total2 = PersonaService.list_personas(db_session, search="dev")
    assert total2 == 1
    assert rows2[0].name == "Ana Dev"

    # pagination
    rows3, total3 = PersonaService.list_personas(db_session, skip=1, limit=1)
    assert total3 == 3
    assert len(rows3) == 1


def test_update_persona_patch(db_session: Session):
    p = PersonaService.create_persona(db_session, make_persona_create(name="X Person", location="Aveiro"), creator_id=1)
    patched = PersonaService.update_persona(
        db_session,
        p.id,
        make_persona_update(location="Coimbra", description="Now updated"),
    )
    assert patched is not None
    assert patched.location == "Coimbra"
    assert patched.description == "Now updated"


def test_update_persona_not_found_returns_none(db_session: Session):
    res = PersonaService.update_persona(db_session, persona_id=9999, patch=make_persona_update())
    assert res is None


def test_delete_persona_ok_and_not_found(db_session: Session):
    p = PersonaService.create_persona(db_session, make_persona_create(name="To Delete"), creator_id=1)
    ok = PersonaService.delete_persona(db_session, p.id)
    assert ok is True

    # delete again -> False
    ok2 = PersonaService.delete_persona(db_session, p.id)
    assert ok2 is False
