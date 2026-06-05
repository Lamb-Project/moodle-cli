"""Auth commands: login, logout, status, profiles."""

from __future__ import annotations

import click

from moodle_cli.cli.main import MoodleContext, handle_errors, pass_context
from moodle_cli.client.http import MoodleHTTPClient
from moodle_cli.client.qrlogin import (
    decode_qr_image,
    exchange_qr_login,
    parse_moodlemobile_uri,
)
from moodle_cli.config.manager import Profile
from moodle_cli.output import console, render_json, render_table


@click.group()
def auth() -> None:
    """Authenticate with a Moodle instance."""


@auth.command()
@click.option("--url", required=True, prompt=True, help="Moodle site URL (e.g. https://moodle.example.com)")
@click.option("--username", required=True, prompt=True, help="Moodle username")
@click.option("--password", default=None, help="Moodle password")
@click.option("--token", default=None, help="Pre-existing token (for SSO/CAS sites)")
@click.option("--profile-name", "--name", default="default", help="Profile name to save as")
@click.option("--service", default="moodle_mobile_app", help="Web service name")
@pass_context
@handle_errors
def login(
    ctx: MoodleContext,
    url: str,
    username: str,
    password: str | None,
    token: str | None,
    profile_name: str,
    service: str,
) -> None:
    """Login to a Moodle instance and save credentials.

    For SSO/CAS sites, use --token to provide a pre-existing token
    instead of username/password authentication.
    """
    url = url.rstrip("/")

    if token:
        console.print(f"Storing token for [bold]{url}[/bold]...")
    else:
        if not password:
            password = click.prompt("Password", hide_input=True)
        console.print(f"Authenticating to [bold]{url}[/bold]...")
        token = MoodleHTTPClient.authenticate(url, username, password, service)

    profile = Profile(url=url, username=username, service=service)
    ctx.config.set_profile(profile_name, profile)
    ctx.tokens.store(profile_name, token)

    console.print(f"[green]Logged in as {username} (profile: {profile_name})[/green]")


@auth.command("qr-login")
@click.argument("uri", required=False)
@click.option("--image", "image_path", default=None, help="Path to a QR-code image file to decode")
@click.option("--url", default=None, help="Site URL (when not using URI/--image)")
@click.option("--key", default=None, help="qrlogin key (when not using URI/--image)")
@click.option("--userid", default=None, help="userid (when not using URI/--image)")
@click.option("--username", default=None, help="Override the username (auto-detected by default)")
@click.option("--profile-name", "--name", default="default", help="Profile name to save as")
@click.option("--service", default="moodle_mobile_app", help="Web service name")
@pass_context
@handle_errors
def qr_login(
    ctx: MoodleContext,
    uri: str | None,
    image_path: str | None,
    url: str | None,
    key: str | None,
    userid: str | None,
    username: str | None,
    profile_name: str,
    service: str,
) -> None:
    """Authenticate from a Moodle "QR login" code and save credentials.

    Newer Moodle sites show a QR code instead of a token string. That QR encodes
    a one-time autologin passport, which this command exchanges for the real
    web-service token. This is the SSO/CAS-friendly path — no password, no admin.

    The passport is single-use with a ~3-minute TTL, so refresh the QR page right
    before running this.

    \b
    Three ways to supply the QR:
      moodle auth qr-login --image ~/Downloads/qr.png --name mysite
      moodle auth qr-login "moodlemobile://https://site?qrlogin=KEY&userid=42" --name mysite
      moodle auth qr-login --url https://site --key KEY --userid 42 --name mysite
    """
    if image_path:
        decoded = decode_qr_image(image_path)
        site_url, qr_key, qr_userid = parse_moodlemobile_uri(decoded)
    elif uri:
        site_url, qr_key, qr_userid = parse_moodlemobile_uri(uri)
    elif url and key and userid:
        site_url = url.rstrip("/")
        if not site_url.startswith("http"):
            site_url = "https://" + site_url
        qr_key, qr_userid = key, userid
    else:
        raise click.UsageError(
            "Provide the QR via one of: a moodlemobile:// URI argument, --image PATH, "
            "or --url/--key/--userid."
        )

    console.print(f"Exchanging QR passport with [bold]{site_url}[/bold]...")
    result = exchange_qr_login(site_url, qr_key, qr_userid)
    token = result["token"]

    # Confirm the token and auto-detect the username (core_webservice_get_site_info
    # is a read-only call available to any valid token).
    if not username:
        try:
            info = MoodleHTTPClient(site_url, token, service=service).call(
                "core_webservice_get_site_info"
            )
            username = info.get("username")
            if info.get("sitename"):
                console.print(f"Site: [bold]{info['sitename']}[/bold] ({info.get('release', '')})")
        except Exception as exc:  # noqa: BLE001 — non-fatal; fall back to --username
            console.print(f"[yellow]Could not auto-detect username: {exc}[/yellow]")
    if not username:
        raise click.UsageError(
            "Could not determine the username; rerun with --username."
        )

    profile = Profile(url=site_url, username=username, service=service)
    ctx.config.set_profile(profile_name, profile)
    ctx.tokens.store(profile_name, token)

    console.print(f"[green]Logged in as {username} (profile: {profile_name})[/green]")


@auth.command()
@click.option("--profile-name", "--name", default=None, help="Profile to logout from")
@pass_context
@handle_errors
def logout(ctx: MoodleContext, profile_name: str | None) -> None:
    """Remove stored token for a profile."""
    name, _ = ctx.config.get_profile(profile_name)
    ctx.tokens.delete(name)
    console.print(f"[green]Logged out from profile '{name}'.[/green]")


@auth.command()
@click.option("--profile-name", "--name", default=None, help="Profile to check")
@pass_context
@handle_errors
def status(ctx: MoodleContext, profile_name: str | None) -> None:
    """Show authentication status for a profile."""
    name, profile = ctx.config.get_profile(profile_name)
    token = ctx.tokens.get(name)
    if ctx.json_output:
        render_json({
            "profile": name,
            "url": profile.url,
            "username": profile.username,
            "authenticated": token is not None,
        })
    else:
        status_text = "[green]authenticated[/green]" if token else "[red]not authenticated[/red]"
        console.print(f"Profile: [bold]{name}[/bold]")
        console.print(f"URL:     {profile.url}")
        console.print(f"User:    {profile.username}")
        console.print(f"Status:  {status_text}")


@auth.command()
@pass_context
@handle_errors
def profiles(ctx: MoodleContext) -> None:
    """List all saved profiles."""
    profile_list = ctx.config.list_profiles()
    if ctx.json_output:
        render_json([
            {"name": name, "url": p.url, "username": p.username, "default": is_default}
            for name, p, is_default in profile_list
        ])
    else:
        if not profile_list:
            console.print("[dim]No profiles configured. Run: moodle auth login[/dim]")
            return
        rows = []
        for name, p, is_default in profile_list:
            rows.append({
                "Name": f"{'* ' if is_default else ''}{name}",
                "URL": p.url,
                "Username": p.username,
            })
        render_table(rows, title="Profiles")
