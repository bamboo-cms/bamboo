from datetime import UTC, datetime
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import check_password_hash, generate_password_hash

from bamboo.core.extensions import db


def now():
    return datetime.now(UTC)


class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str]
    username: so.Mapped[Optional[str]]
    password_hash: so.Mapped[Optional[str]]
    bio: so.Mapped[Optional[str]]
    introduction: so.Mapped[Optional[str]]
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    active: so.Mapped[bool] = so.mapped_column(default=False)
    profile_image_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("media.id"), index=True)
    role_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("role.id"), index=True)
    profile_image: so.Mapped["Media"] = so.relationship(foreign_keys=[profile_image_id])
    role: so.Mapped["Role"] = so.relationship(back_populates="users")
    blog_authors: so.WriteOnlyMapped["BlogAuthor"] = so.relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    @property
    def password(self):
        raise AttributeError("Write-only property!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Role(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str]
    permissions: so.Mapped[int]
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    users: so.WriteOnlyMapped["User"] = so.relationship(back_populates="role")


class Media(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    path: so.Mapped[str]
    content_type: so.Mapped[str]
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)


class Site(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    config: so.Mapped[dict] = so.mapped_column(type_=sa.JSON)
    template_url: so.Mapped[Optional[str]]
    deploy_target: so.Mapped[Optional[str]]
    deploy_method: so.Mapped[Optional[str]]
    deploy_secret: so.Mapped[Optional[str]] = so.mapped_column(sa.Text)
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    pages: so.WriteOnlyMapped["Page"] = so.relationship(back_populates="site")
    notifications: so.WriteOnlyMapped["Notification"] = so.relationship(back_populates="site")
    volunteer_forms: so.WriteOnlyMapped["VolunteerForm"] = so.relationship(back_populates="site")
    sponsor_forms: so.WriteOnlyMapped["SponsorForm"] = so.relationship(back_populates="site")
    speaker_forms: so.WriteOnlyMapped["SpeakerForm"] = so.relationship(back_populates="site")
    talks: so.WriteOnlyMapped["Talk"] = so.relationship(back_populates="site")
    blogs: so.WriteOnlyMapped["Blog"] = so.relationship(back_populates="site")


class Page(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str]
    path: so.Mapped[str]
    content: so.Mapped[str] = so.mapped_column(sa.Text)
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    site_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("site.id"), index=True)
    site: so.Mapped["Site"] = so.relationship(back_populates="pages")


class Notification(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    content: so.Mapped[str] = so.mapped_column(sa.Text)
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    site_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("site.id"), index=True)
    site: so.Mapped["Site"] = so.relationship(back_populates="notifications")


class VolunteerForm(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    # ...
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    site_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("site.id"), index=True)
    site: so.Mapped["Site"] = so.relationship(back_populates="volunteer_forms")


class SponsorForm(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    # ...
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    site_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("site.id"), index=True)
    site: so.Mapped["Site"] = so.relationship(back_populates="sponsor_forms")


class SpeakerForm(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    # ...
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    site_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("site.id"), index=True)
    site: so.Mapped["Site"] = so.relationship(back_populates="speaker_forms")


class Talk(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str]
    content: so.Mapped[str]
    video_url: so.Mapped[Optional[str]]
    slides_url: so.Mapped[Optional[str]]
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    slides_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey("media.id"), index=True)
    slides: so.Mapped["Media"] = so.relationship(foreign_keys=[slides_id])
    site_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("site.id"), index=True)
    site: so.Mapped["Site"] = so.relationship(back_populates="talks")
    schedule_items: so.WriteOnlyMapped["ScheduleItem"] = so.relationship(
        back_populates="talk", uselist=False, cascade="all, delete-orphan"
    )
    talk_categories: so.WriteOnlyMapped["TalkCategory"] = so.relationship(
        back_populates="talk", cascade="all, delete-orphan"
    )


class Category(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str]
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    talk_categories: so.WriteOnlyMapped["TalkCategory"] = so.relationship(
        back_populates="category", cascade="all, delete-orphan"
    )


class TalkCategory(db.Model):
    talk_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("talk.id"), primary_key=True)
    category_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("category.id"), primary_key=True)
    talk: so.Mapped["Talk"] = so.relationship(back_populates="talk_categories")
    category: so.Mapped["Category"] = so.relationship(back_populates="talk_categories")


class Staff(db.Model):
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    city_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("city.id"), primary_key=True)
    staff_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), primary_key=True)
    city: so.Mapped["City"] = so.relationship(back_populates="staffs")
    staff: so.Mapped["User"] = so.relationship(foreign_keys=[staff_id])
    category: so.Mapped[str]


class City(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str]
    address: so.Mapped[str]
    latitude: so.Mapped[float]
    longitude: so.Mapped[float]
    start: so.Mapped[datetime]
    end: so.Mapped[datetime]
    registration_url: so.Mapped[str]
    live_urls: so.Mapped[str]
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    site_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("site.id"), index=True)
    staffs: so.WriteOnlyMapped["Staff"] = so.relationship(back_populates="city")
    venues: so.WriteOnlyMapped["Venue"] = so.relationship(back_populates="city")
    partnerships: so.WriteOnlyMapped["Partership"] = so.relationship(
        back_populates="city", cascade="all, delete-orphan"
    )


class Partership(db.Model):
    city_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("city.id"), primary_key=True)
    organization_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("organization.id"), primary_key=True
    )
    category: so.Mapped[str]
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    city: so.Mapped["City"] = so.relationship(back_populates="partnerships")
    organization: so.Mapped["Organization"] = so.relationship(back_populates="partnerships")


class Organization(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str]
    url: so.Mapped[str]
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    profile_image_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("media.id"), index=True)
    profile_image: so.Mapped["Media"] = so.relationship(foreign_keys=[profile_image_id])
    partnerships: so.WriteOnlyMapped["Partership"] = so.relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )


class Blog(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str]
    path: so.Mapped[str]
    content: so.Mapped[str] = so.mapped_column(sa.Text)
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    site_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("site.id"), index=True)
    site: so.Mapped["Site"] = so.relationship(back_populates="blogs")
    blog_authors: so.WriteOnlyMapped["BlogAuthor"] = so.relationship(
        back_populates="blog", cascade="all, delete-orphan"
    )


class BlogAuthor(db.Model):
    blog_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("blog.id"), primary_key=True)
    author_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), primary_key=True)
    blog: so.Mapped["Blog"] = so.relationship(back_populates="blog_authors")
    author: so.Mapped["User"] = so.relationship(back_populates="blog_authors")


class ScheduleItem(db.Model):
    venue_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("venue.id"), primary_key=True)
    talk_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey("talk.id"), primary_key=True)
    content: so.Mapped[str] = so.mapped_column(sa.Text)
    start: so.Mapped[datetime]
    end: so.Mapped[datetime]
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    venue: so.Mapped["Venue"] = so.relationship(back_populates="schedule_items")
    talk: so.Mapped["Talk"] = so.relationship(back_populates="schedule_items")


class Venue(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str]
    address: so.Mapped[str]
    created_at: so.Mapped[datetime] = so.mapped_column(default=now)
    updated_at: so.Mapped[datetime] = so.mapped_column(default=now, onupdate=now)
    city_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("city.id"), index=True)
    city: so.Mapped["City"] = so.relationship(back_populates="venues")
    schedule_items: so.WriteOnlyMapped["ScheduleItem"] = so.relationship(
        back_populates="venue", cascade="all, delete-orphan"
    )
