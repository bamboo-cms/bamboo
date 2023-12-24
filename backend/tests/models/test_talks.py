from datetime import datetime

from bamboo.database import db, models


def test_talk_category():
    site = models.Site(name="Test site", config={})
    keynote = models.Category(name="keynote")
    act = models.Category(name="act")
    talk = models.Talk(title="Sample Talk", site=site)
    talk.categories.add_all([keynote, act])
    db.session.add_all([site, keynote, act, talk])
    db.session.commit()
    assert set(models.Category.query.filter(models.Category.talks.contains(talk)).all()) == {
        keynote,
        act,
    }


def test_talk_schedule():
    site = models.Site(name="Test site", config={})
    talk = models.Talk(title="Sample Talk", site=site)
    city = models.City(name="Test city", site=site)
    venue = models.Venue(name="Test venue", address="somewhere", city=city)
    schedule_item = models.ScheduleItem(
        talk=talk, venue=venue, start=datetime(2021, 1, 1, 12, 0), end=datetime(2021, 1, 1, 13, 0)
    )
    db.session.add_all([site, talk, schedule_item, city, venue])
    db.session.commit()
    assert talk.schedule_item == schedule_item
