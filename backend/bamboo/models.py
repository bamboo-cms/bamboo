from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, \
    Boolean, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from bamboo.core.extensions import db


class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    username = Column(String)
    password_hash = Column(String)
    biology = Column(String)
    introduction = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean)
    profile_image_id = Column(Integer, ForeignKey('media.id'))
    role_id = Column(String, ForeignKey('role.id'))

    profile_image = relationship('Media', foreign_keys=[profile_image_id])
    role = relationship('Role', back_populates='users')
    blog_authors = relationship('BlogAuthor', back_populates='author', cascade='all, delete-orphan')

    @property
    def password(self):
        raise AttributeError('Write-only property!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Role(db.Model):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    permissions = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship('User', back_populates='role')


class Media(db.Model):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True)
    path = Column(String)
    content_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Site(db.Model):
    __tablename__ = 'site'
    id = Column(Integer, primary_key=True)
    config = Column(JSON)
    template_url = Column(String)
    deploy_target = Column(String)
    deploy_method = Column(String)
    deploy_secret = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pages = relationship('Page', back_populates='site')
    notifications = relationship('Notification', back_populates='site')
    volunteer_forms = relationship('VolunteerForm', back_populates='site')
    sponsor_forms = relationship('SponsorForm', back_populates='site')
    speaker_forms = relationship('SpeakerForm', back_populates='site')
    talks = relationship('Talk', back_populates='site')
    blogs = relationship('Blog', back_populates='site')


class Page(db.Model):
    __tablename__ = 'page'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    path = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    site_id = Column(Integer, ForeignKey('site.id'))

    site = relationship('Site', back_populates='pages')


class Notification(db.Model):
    __tablename__ = 'notification'
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    site_id = Column(Integer, ForeignKey('site.id'))

    site = relationship('Site', back_populates='notifications')


class VolunteerForm(db.Model):
    __tablename__ = 'volunteer_form'
    id = Column(Integer, primary_key=True)
    # ...
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    site_id = Column(Integer, ForeignKey('site.id'))

    site = relationship('Site', back_populates='volunteer_forms')


class SponsorForm(db.Model):
    __tablename__ = 'sponsor_form'
    id = Column(Integer, primary_key=True)
    # ...
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    site_id = Column(Integer, ForeignKey('site.id'))

    site = relationship('Site', back_populates='sponsor_forms')


class SpeakerForm(db.Model):
    __tablename__ = 'speaker_form'
    id = Column(Integer, primary_key=True)
    # ...
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    site_id = Column(Integer, ForeignKey('site.id'))

    site = relationship('Site', back_populates='speaker_forms')


class Talk(db.Model):
    __tablename__ = 'talk'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    video_url = Column(String)
    slides_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    slides_id = Column(Integer, ForeignKey('media.id'))
    site_id = Column(Integer, ForeignKey('site.id'))

    slides = relationship('Media', foreign_keys=[slides_id])
    site = relationship('Site', back_populates='talks')
    schedule_items = relationship('ScheduleItem', back_populates='talk', cascade='all, delete-orphan')
    talk_categories = relationship('TalkCategory', back_populates='talk', cascade='all, delete-orphan')


class Category(db.Model):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    talk_categories = relationship('TalkCategory', back_populates='category', cascade='all, delete-orphan')


class TalkCategory(db.Model):
    __tablename__ = 'talk_category'
    talk_id = Column(Integer, ForeignKey('talk.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'), primary_key=True)

    talk = relationship('Talk', back_populates='talk_categories')
    category = relationship('Category', back_populates='talk_categories')


class Staff(db.Model):
    __tablename__ = 'staff'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    city_id = Column(Integer, ForeignKey('city.id'))
    staff_id = Column(Integer, ForeignKey('user.id'))

    city = relationship('City', back_populates='staffs')
    staff = relationship('User', foreign_keys=[staff_id])


class City(db.Model):
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    start = Column(DateTime)
    end = Column(DateTime)
    registration_url = Column(String)
    live_urls = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    site_id = Column(Integer, ForeignKey('site.id'))

    staffs = relationship('Staff', back_populates='city')
    venues = relationship('Venue', back_populates='city')
    partnerships = relationship('Partership', back_populates='city', cascade='all, delete-orphan')


class Partership(db.Model):
    __tablename__ = 'partnership'
    city_id = Column(Integer, ForeignKey('city.id'), primary_key=True)
    organization_id = Column(Integer, ForeignKey('organization.id'), primary_key=True)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    city = relationship('City', back_populates='partnerships')
    organization = relationship('Organization', back_populates='partnerships')


class Organization(db.Model):
    __tablename__ = 'organization'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    profile_image_id = Column(Integer, ForeignKey('media.id'))

    profile_image = relationship('Media', foreign_keys=[profile_image_id])
    partnerships = relationship('Partership', back_populates='organization', cascade='all, delete-orphan')


class Blog(db.Model):
    __tablename__ = 'blog'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    path = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    site_id = Column(Integer, db.ForeignKey('site.id'))

    site = relationship('Site', back_populates='blogs')
    blog_authors = relationship('BlogAuthor', back_populates='blog', cascade='all, delete-orphan')


class BlogAuthor(db.Model):
    __tablename__ = 'blog_author'
    blog_id = Column(Integer, ForeignKey('blog.id'), primary_key=True)
    author_id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    blog = relationship('Blog', back_populates='blog_authors')
    author = relationship('User', back_populates='blog_authors')


class ScheduleItem(db.Model):
    __tablename__ = 'schedule_item'
    venue_id = Column(Integer, ForeignKey('venue.id'), primary_key=True)
    talk_id = Column(Integer, ForeignKey('talk.id'), primary_key=True)
    content = Column(Text)
    start = Column(DateTime)
    end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    venue = relationship('Venue', back_populates='schedule_items')
    talk = relationship('Talk', back_populates='schedule_items')


class Venue(db.Model):
    __tablename__ = 'venue'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    address = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    city_id = Column(Integer, ForeignKey('city.id'))

    city = relationship('City', back_populates='venues')
    schedule_items = relationship('ScheduleItem', back_populates='venue', cascade='all, delete-orphan')
