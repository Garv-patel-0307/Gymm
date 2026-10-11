import base64
import os
import sqlite3
import tempfile
from pathlib import Path

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Back up SQLite to the GitHub repository root"

    def handle(self, *args, **options):
        token = os.environ.get("GITHUB_TOKEN")
        repo = os.environ.get(
            "GITHUB_REPO",
            "Garv-patel-0307/Gym-Management-System",
        )
        branch = os.environ.get("GITHUB_BRANCH", "main")

        if not token:
            raise CommandError("GITHUB_TOKEN is not configured")

        if connection.vendor != "sqlite":
            raise CommandError("This command requires SQLite")

        db_path = Path(settings.DATABASES["default"]["NAME"])

        if not db_path.is_file():
            raise CommandError(f"Database not found: {db_path}")

        api_url = (
            f"https://api.github.com/repos/{repo}/contents/db.sqlite3"
        )
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        # Create a consistent snapshot using SQLite's backup API.
        with tempfile.TemporaryDirectory() as temp_dir:
            snapshot = Path(temp_dir) / "db.sqlite3"

            source = sqlite3.connect(
                f"file:{db_path.resolve()}?mode=ro",
                uri=True,
                timeout=30,
            )
            destination = sqlite3.connect(str(snapshot))

            try:
                source.backup(destination)
            finally:
                destination.close()
                source.close()

            content = base64.b64encode(
                snapshot.read_bytes()
            ).decode("ascii")

        # Get the current file SHA required by GitHub for updates.
        response = requests.get(
            api_url,
            headers=headers,
            params={"ref": branch},
            timeout=30,
        )

        if response.status_code == 200:
            sha = response.json()["sha"]
        elif response.status_code == 404:
            sha = None
        else:
            raise CommandError(
                f"GitHub read failed: {response.status_code} "
                f"{response.text[:500]}"
            )

        payload = {
            "message": "Automated SQLite backup",
            "content": content,
            "branch": branch,
        }

        if sha:
            payload["sha"] = sha

        response = requests.put(
            api_url,
            headers=headers,
            json=payload,
            timeout=60,
        )

        if response.status_code not in (200, 201):
            raise CommandError(
                f"GitHub upload failed: {response.status_code} "
                f"{response.text[:500]}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                "SQLite snapshot uploaded to GitHub successfully."
            )
        )