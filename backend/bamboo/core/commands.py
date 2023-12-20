import click

from bamboo import models  # noqa: F401
from bamboo.core.extensions import db


def register_commands(app):
    @app.cli.command(name="create-tables")
    def create_tables():
        db.create_all()
        click.echo("Tables created")

    @app.cli.command(name="drop-tables")
    def drop_tables():
        db.drop_all()
        click.echo("Tables dropped")
