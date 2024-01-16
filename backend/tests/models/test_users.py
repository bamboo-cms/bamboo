import pytest
from bamboo.database import db, models


def test_user():
    profile = models.Media.from_file("test.png")
    user1 = models.User(name="test", profile_image=profile)
    user2 = models.User(name="test2", profile_image=profile)
    user1.password = "123456"
    db.session.add_all([user1, user2, profile])
    db.session.commit()
    with pytest.raises(AttributeError):
        user1.password
    assert user1.validate_password("123456")
    assert user1.role is None
    assert user2.role is None
    assert not user1.active and not user1.is_superuser
    assert user1.profile_image == user1.profile_image == profile


def test_role():
    role = models.Role(name="test", permissions=1)
    profile = models.Media.from_file("test.png")
    user1 = models.User(name="test", profile_image=profile, role=role)
    user2 = models.User(name="test2", profile_image=profile, role=role)
    db.session.add_all([user1, user2, profile, role])
    db.session.commit()
    assert user1.role == user2.role == role
    assert models.User.query.filter_by(role=role).all() == [user1, user2]
    assert db.session.scalars(db.select(models.User).filter_by(role=role)).all() == [user1, user2]


def test_staff():
    site = models.Site(name="Test site", config={})
    profile = models.Media.from_file("test.png")
    user1 = models.User(name="test1", profile_image=profile)
    user2 = models.User(name="test2", profile_image=profile)
    city = models.City(name="New York", site=site)
    staff1 = models.Staff(staff=user1, city=city, category="supporter")
    staff2 = models.Staff(staff=user2, city=city, category="sponsor")
    db.session.add_all([user1, user2, profile, city, staff1, staff2, site])
    db.session.commit()
