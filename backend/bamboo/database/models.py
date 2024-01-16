from datetime import datetime
from typing import TYPE_CHECKING, NoReturn, Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


# https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#sqlite-foreign-keys
@sa.event.listens_for(sa.engine.Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    import sqlite3

    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


if TYPE_CHECKING:

    class BaseModel(Model, so.DeclarativeBase):
        """A dummy BaseModel class for type checking"""

        pass
else:
    BaseModel = db.Model


class Base(BaseModel):
    __abstract__ = True

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    created_at: so.Mapped[datetime] = so.mapped_column(default=func.now())
    updated_at: so.Mapped[datetime] = so.mapped_column(default=func.now(), onupdate=func.now())

    def __repr__(self):
        attrs = {"id": self.id}
        if hasattr(self, "name"):
            attrs["name"] = self.name  # pyright: ignore[reportGeneralTypeIssues]
        if hasattr(self, "title"):
            attrs["title"] = self.title  # pyright: ignore[reportGeneralTypeIssues]
        return "<{} {}>".format(
            self.__class__.__name__, ",".join(f"{k}={v!r}" for k, v in attrs.items())
        )


blog_author = db.Table(
    "blog_author",
    sa.Column(
        "blog_id", sa.Integer, sa.ForeignKey("blog.id", ondelete="CASCADE"), primary_key=True
    ),
    sa.Column(
        "author_id", sa.Integer, sa.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    ),
)


class User(Base):
    name: so.Mapped[str]
    username: so.Mapped[Optional[str]] = so.mapped_column(unique=True, index=True)
    password_hash: so.Mapped[Optional[str]]
    bio: so.Mapped[Optional[str]]
    introduction: so.Mapped[Optional[str]]
    active: so.Mapped[bool] = so.mapped_column(default=False)
    is_superuser: so.Mapped[bool] = so.mapped_column(default=False)
    profile_image_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("media.id", ondelete="CASCADE"), index=True
    )
    role_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey("role.id", ondelete="CASCADE"), index=True
    )
    profile_image: so.Mapped["Media"] = so.relationship(foreign_keys=[profile_image_id])
    role: so.Mapped[Optional["Role"]] = so.relationship(back_populates="users")
    blogs: so.WriteOnlyMapped["Blog"] = so.relationship(
        back_populates="authors", secondary=blog_author, passive_deletes=True
    )
    supporting: so.WriteOnlyMapped["Staff"] = so.relationship(
        back_populates="staff", cascade="all, delete-orphan", passive_deletes=True
    )

    @property
    def password(self) -> NoReturn:
        raise AttributeError("Write-only property!")

    @password.setter
    def password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password: str) -> bool:
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)


class Role(Base):
    name: so.Mapped[str]
    permissions: so.Mapped[int]
    users: so.WriteOnlyMapped["User"] = so.relationship(back_populates="role")


class Media(Base):
    path: so.Mapped[str]
    content_type: so.Mapped[str]


class Site(Base):
    name: so.Mapped[str]
    config: so.Mapped[dict] = so.mapped_column(type_=sa.JSON)
    template_url: so.Mapped[Optional[str]]
    deploy_target: so.Mapped[Optional[str]]
    deploy_method: so.Mapped[Optional[str]]
    deploy_secret: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    pages: so.WriteOnlyMapped["Page"] = so.relationship(
        back_populates="site", cascade="all, delete-orphan", passive_deletes=True
    )
    notifications: so.WriteOnlyMapped["Notification"] = so.relationship(
        back_populates="site", cascade="all, delete-orphan", passive_deletes=True
    )
    volunteer_forms: so.WriteOnlyMapped["VolunteerForm"] = so.relationship(
        back_populates="site", cascade="all, delete-orphan", passive_deletes=True
    )
    sponsor_forms: so.WriteOnlyMapped["SponsorForm"] = so.relationship(
        back_populates="site", cascade="all, delete-orphan", passive_deletes=True
    )
    speaker_forms: so.WriteOnlyMapped["SpeakerForm"] = so.relationship(
        back_populates="site", cascade="all, delete-orphan", passive_deletes=True
    )
    talks: so.WriteOnlyMapped["Talk"] = so.relationship(
        back_populates="site", cascade="all, delete-orphan", passive_deletes=True
    )
    blogs: so.WriteOnlyMapped["Blog"] = so.relationship(
        back_populates="site", cascade="all, delete-orphan", passive_deletes=True
    )
    cities: so.WriteOnlyMapped["City"] = so.relationship(
        back_populates="site", cascade="all, delete-orphan", passive_deletes=True
    )


class Page(Base):
    title: so.Mapped[str]
    path: so.Mapped[str]
    content: so.Mapped[str] = so.mapped_column(sa.Text)
    site_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("site.id", ondelete="CASCADE"), index=True
    )
    site: so.Mapped["Site"] = so.relationship(back_populates="pages")


class Notification(Base):
    content: so.Mapped[str] = so.mapped_column(sa.Text)
    site_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("site.id", ondelete="CASCADE"), index=True
    )
    site: so.Mapped["Site"] = so.relationship(back_populates="notifications")


class VolunteerForm(Base):
    # ...
    site_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("site.id", ondelete="CASCADE"), index=True
    )
    site: so.Mapped["Site"] = so.relationship(back_populates="volunteer_forms")


class SponsorForm(Base):
    # ...
    site_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("site.id", ondelete="CASCADE"), index=True
    )
    site: so.Mapped["Site"] = so.relationship(back_populates="sponsor_forms")


class SpeakerForm(Base):
    # ...
    site_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("site.id", ondelete="CASCADE"), index=True
    )
    site: so.Mapped["Site"] = so.relationship(back_populates="speaker_forms")


talk_category = db.Table(
    "talk_category",
    sa.Column(
        "talk_id", sa.Integer, sa.ForeignKey("talk.id", ondelete="CASCADE"), primary_key=True
    ),
    sa.Column(
        "category_id",
        sa.Integer,
        sa.ForeignKey("category.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Talk(Base):
    title: so.Mapped[str]
    content: so.Mapped[str] = so.mapped_column(sa.Text, default="")
    video_url: so.Mapped[Optional[str]]
    slides_url: so.Mapped[Optional[str]]
    slides_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey("media.id", ondelete="CASCADE"), index=True
    )
    slides: so.Mapped["Media"] = so.relationship(foreign_keys=[slides_id])
    site_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("site.id", ondelete="CASCADE"), index=True
    )
    site: so.Mapped["Site"] = so.relationship(back_populates="talks")
    schedule_item: so.Mapped[Optional["ScheduleItem"]] = so.relationship(back_populates="talk")
    categories: so.WriteOnlyMapped["Category"] = so.relationship(
        secondary=talk_category, back_populates="talks"
    )


class Category(Base):
    name: so.Mapped[str]
    talks: so.WriteOnlyMapped["Talk"] = so.relationship(
        secondary=talk_category, passive_deletes=True
    )


class Staff(BaseModel):
    created_at: so.Mapped[datetime] = so.mapped_column(default=func.now())
    updated_at: so.Mapped[datetime] = so.mapped_column(default=func.now(), onupdate=func.now())
    city_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("city.id", ondelete="CASCADE"), primary_key=True
    )
    staff_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    city: so.Mapped["City"] = so.relationship(back_populates="staffs", foreign_keys=[city_id])
    staff: so.Mapped["User"] = so.relationship(back_populates="supporting", foreign_keys=[staff_id])
    category: so.Mapped[str]


class City(Base):
    name: so.Mapped[str] = so.mapped_column(index=True)
    address: so.Mapped[Optional[str]]
    latitude: so.Mapped[Optional[str]]
    longitude: so.Mapped[Optional[str]]
    start: so.Mapped[Optional[datetime]]
    end: so.Mapped[Optional[datetime]]
    registration_url: so.Mapped[Optional[str]]
    live_urls: so.Mapped[Optional[str]]
    site_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("site.id", ondelete="CASCADE"), index=True
    )
    site: so.Mapped["Site"] = so.relationship(back_populates="cities")
    staffs: so.WriteOnlyMapped["Staff"] = so.relationship(
        back_populates="city", cascade="all, delete-orphan", passive_deletes=True
    )
    venues: so.WriteOnlyMapped["Venue"] = so.relationship(
        back_populates="city", cascade="all, delete-orphan", passive_deletes=True
    )
    partnerships: so.WriteOnlyMapped["Partnership"] = so.relationship(
        back_populates="city", cascade="all, delete-orphan", passive_deletes=True
    )


class Partnership(BaseModel):
    city_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("city.id", ondelete="CASCADE"), primary_key=True
    )
    organization_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("organization.id", ondelete="CASCADE"), primary_key=True
    )
    category: so.Mapped[str]
    created_at: so.Mapped[datetime] = so.mapped_column(default=func.now())
    updated_at: so.Mapped[datetime] = so.mapped_column(default=func.now(), onupdate=func.now())
    city: so.Mapped["City"] = so.relationship(back_populates="partnerships")
    organization: so.Mapped["Organization"] = so.relationship(back_populates="partnerships")


class Organization(Base):
    name: so.Mapped[str]
    url: so.Mapped[str]
    profile_image_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("media.id", ondelete="CASCADE"), index=True
    )
    profile_image: so.Mapped["Media"] = so.relationship(foreign_keys=[profile_image_id])
    partnerships: so.WriteOnlyMapped["Partnership"] = so.relationship(
        back_populates="organization", cascade="all, delete-orphan", passive_deletes=True
    )


class Blog(Base):
    title: so.Mapped[str]
    path: so.Mapped[str]
    content: so.Mapped[str] = so.mapped_column(sa.Text)
    site_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("site.id", ondelete="CASCADE"), index=True
    )
    site: so.Mapped["Site"] = so.relationship(back_populates="blogs")
    authors: so.WriteOnlyMapped["User"] = so.relationship(
        back_populates="blogs", secondary=blog_author
    )


class ScheduleItem(Base):
    venue_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("venue.id", ondelete="CASCADE"), index=True
    )
    talk_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey("talk.id", ondelete="CASCADE"), index=True
    )
    content: so.Mapped[str] = so.mapped_column(sa.Text, default="")
    start: so.Mapped[datetime]
    end: so.Mapped[datetime]
    venue: so.Mapped["Venue"] = so.relationship(back_populates="schedule_items")
    talk: so.Mapped["Talk"] = so.relationship(back_populates="schedule_item")


class Venue(Base):
    name: so.Mapped[str]
    address: so.Mapped[str]
    city_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("city.id", ondelete="CASCADE"), index=True
    )
    city: so.Mapped["City"] = so.relationship(back_populates="venues")
    schedule_items: so.WriteOnlyMapped["ScheduleItem"] = so.relationship(
        back_populates="venue", cascade="all, delete-orphan", passive_deletes=True
    )
