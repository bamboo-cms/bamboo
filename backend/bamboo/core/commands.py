import click

from bamboo.core.extensions import db
from bamboo.models import *


def register_commands(app):
    @app.cli.command(name='create-tables')
    def create_tables():
        db.create_all()
        click.echo('Tables created')

    @app.cli.command(name='drop-tables')
    def drop_tables():
        db.drop_all()
        click.echo('Tables dropped')
