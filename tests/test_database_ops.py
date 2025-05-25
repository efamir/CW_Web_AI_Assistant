import pytest
from db import Role, User, Note


def test_create_new_role(db_s):
    my_role = Role(name="tester_role")
    db_s.add(my_role)
    db_s.commit()

    role_from_db = db_s.query(Role).filter_by(name="tester_role").first()
    assert role_from_db is not None
    assert role_from_db.name == "tester_role"

def test_create_user_and_check_pass(db_s):
    user_r = Role(name="simple_user_role")
    db_s.add(user_r)
    db_s.commit()

    test_u = User(username="test_user1", password_string="pass123", role=user_r)
    db_s.add(test_u)
    db_s.commit()

    user_from_db = db_s.query(User).filter_by(username="test_user1").first()
    assert user_from_db is not None
    assert user_from_db.username == "test_user1"
    assert user_from_db.role.name == "simple_user_role"
    assert user_from_db.check_password("pass123") is True
    assert user_from_db.check_password("wrong_pass") is False

def test_create_note_for_specific_user(db_s):
    note_role = Role(name="note_role_db")
    db_s.add(note_role)
    db_s.commit()
    db_s.refresh(note_role)
    note_user = User(username="writer_user", password_string="secret", role=note_role)
    db_s.add(note_user)
    db_s.commit()

    my_note = Note(text="Це моя тестова нотатка.", user_id=note_user.id)
    db_s.add(my_note)
    db_s.commit()

    note_from_db = db_s.query(Note).filter_by(text="Це моя тестова нотатка.").first()
    assert note_from_db is not None
    assert note_from_db.user_id == note_user.id
    assert note_from_db.user.username == "writer_user"
    assert len(note_user.notes) == 1
    assert note_user.notes[0].text == "Це моя тестова нотатка."
