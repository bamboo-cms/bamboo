from bamboo.database import db, models


def test_partnership(client):
    profile = models.Media(path="test.png", content_type="image/png")
    organization = models.Organization(
        name="code-kitchen", url="https://codekitchen.community", profile_image=profile
    )
    site = models.Site(name="Test site", config={})
    city = models.City(name="Test city", site=site)
    profile = models.Media(path="test.png", content_type="image/png")
    user = models.User(name="staff", profile_image=profile)
    city.staffs.add(models.Staff(staff=user, category="supporter"))
    db.session.add_all([profile, organization, city])
    partnership = models.Partnership(city=city, organization=organization, category="supporter")
    db.session.add_all([partnership])
    db.session.commit()

    partner = db.session.scalars(db.select(models.Partnership)).all()
    assert len(partner) == 1
    assert partner[0].city.name == "Test city"
    assert partner[0].organization.name == "code-kitchen"
    assert partner[0].category == "supporter"

    db.session.delete(partnership)
    db.session.commit()
    organ = db.session.scalars(db.select(models.Partnership)).all()
    assert len(organ) == 0
