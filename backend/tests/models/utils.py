import sqlalchemy as sa

from bamboo.database import db


def query_count(model):
    return db.session.scalar(db.select(sa.func.count()).select_from(model))
