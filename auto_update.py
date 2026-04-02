#!/usr/bin/env python3
"""Auto-update todayfortune.net - generate data and push to GitHub."""

import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

SITE_DIR = Path(__file__).parent


def update_and_push():
    """Generate new data and push to GitHub."""
    # Generate data
    log.info("Generating site data...")
    result = subprocess.run(
        ["python3", str(SITE_DIR / "update_site.py")],
        cwd=str(SITE_DIR),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log.error("Data generation failed: %s", result.stderr[-300:])
        return False
    log.info("Data generated.")

    # Git add, commit, push
    log.info("Pushing to GitHub...")
    subprocess.run(["git", "add", "-A"], cwd=str(SITE_DIR), capture_output=True)
    result = subprocess.run(
        ["git", "commit", "-m", "Daily update"],
        cwd=str(SITE_DIR),
        capture_output=True,
        text=True,
    )
    if "nothing to commit" in result.stdout:
        log.info("No changes to push.")
        return True

    result = subprocess.run(
        ["git", "push"],
        cwd=str(SITE_DIR),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log.error("Push failed: %s", result.stderr[-300:])
        return False

    log.info("Site updated and pushed!")
    return True


if __name__ == "__main__":
    update_and_push()
