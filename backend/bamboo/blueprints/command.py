import click
from flask import Blueprint

from bamboo.database import db

command = Blueprint("command", __name__, cli_group=None)


@command.cli.command(name="create-tables")
def create_tables() -> None:
    """Create all tables."""
    db.create_all()
    click.echo("Tables created.")


@command.cli.command(name="drop-tables")
def drop_tables() -> None:
    """Drop all tables."""
    db.drop_all()
    click.echo("Tables dropped.")


@command.cli.command(name="create-admin")
@click.option("--username", prompt=True, help="Admin username.")
@click.option(
    "--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Admin password."
)
@click.option("--name", "fullname", prompt=True, help="Admin full name.")
@click.option("--email", prompt=True, help="Admin email.")
def create_admin(username: str, password: str, name: str, email: str) -> None:
    """Create admin user."""
    from bamboo.database import models

    if (
        profile := db.session.scalars(db.select(models.Media).filter_by(path="user.png")).first()
    ) is None:
        profile = models.Media.from_file("user.png")
        db.session.add(profile)

    user = models.User(
        name=name,
        profile_image=profile,
        is_superuser=True,
        active=True,
        username=username,
        email=email,
    )
    user.password = password
    db.session.add(user)
    db.session.commit()
    click.echo(f"Admin user {username} has been created.")
