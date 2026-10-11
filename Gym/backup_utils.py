
import logging
import os
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def backup_database_to_github():
    project_root = Path(__file__).resolve().parent.parent

    try:
        result = subprocess.run(
            [
                sys.executable,
                "manage.py",
                "backup_sqlite_to_github",
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=90,
            check=True,
            env=os.environ.copy(),
        )

        logger.info("GitHub backup successful: %s", result.stdout)

    except subprocess.CalledProcessError as e:
        logger.error("GitHub backup command failed.")
        logger.error("STDOUT: %s", e.stdout)
        logger.error("STDERR: %s", e.stderr)

    except Exception:
        logger.exception("GitHub database backup failed")