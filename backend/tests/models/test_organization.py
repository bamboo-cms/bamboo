from bamboo.database import db, models


def test_organization(client):
    profile = models.Media(path="test.png", content_type="image/png")
    organization = models.Organization(
        name="code-kitchen", url="https://codekitchen.community", profile_image=profile
    )
    db.session.add_all([profile, organization])
    db.session.commit()

    organ = db.session.scalars(db.select(models.Organization)).all()
    assert len(organ) == 1
    assert organ[0].name == "code-kitchen"
    assert organ[0].url == "https://codekitchen.community"
    assert organ[0].profile_image.path == "test.png"
    assert organ[0].profile_image.content_type == "image/png"

    organization.name = "test"
    db.session.commit()
    organ = db.session.scalars(db.select(models.Organization)).all()
    assert len(organ) == 1
    assert organ[0].name == "test"

    db.session.delete(organization)
    db.session.commit()
    organ = db.session.scalars(db.select(models.Organization)).all()
    assert len(organ) == 0
