from bamboo.database import db, models

from .utils import query_count


def test_city_staff():
    site = models.Site(name="Test site", config={})
    city = models.City(name="Test city", site=site)
    profile = models.Media(path="test.png", content_type="image/png")
    user = models.User(name="staff", profile_image=profile)
    city.staffs.add(models.Staff(staff=user, category="supporter"))
    db.session.add_all([city])
    db.session.commit()
    staffs = db.session.scalars(db.select(models.Staff).filter_by(city=city)).all()
    assert len(staffs) == 1
    assert staffs[0].staff == user
    assert staffs[0].city == city

    db.session.delete(city)
    db.session.commit()
    assert query_count(models.Staff) == 0
    assert query_count(models.User) == 1


def test_city_staff_delete_user():
    site = models.Site(name="Test site", config={})
    city = models.City(name="Test city", site=site)
    profile = models.Media(path="test.png", content_type="image/png")
    user = models.User(name="staff", profile_image=profile)
    user.supporting.add(models.Staff(city=city, category="supporter"))
    db.session.add(user)
    db.session.commit()
    staffs = db.session.scalars(db.select(models.Staff).filter_by(city=city)).all()
    assert len(staffs) == 1
    assert staffs[0].staff == user
    assert staffs[0].city == city

    db.session.delete(user)
    db.session.commit()
    assert query_count(models.Staff) == 0
    assert query_count(models.City) == 1
    db.session.delete(site)
    db.session.commit()
    db.session.flush()
    assert query_count(models.City) == 0
