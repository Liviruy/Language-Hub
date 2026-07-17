#!/usr/bin/env python3
"""Upload audio files and Anki exports to Cloudflare R2.

Usage:
    python scripts/upload_r2.py               # Upload all
    python scripts/upload_r2.py --audio-only   # Only audio
    python scripts/upload_r2.py --exports-only  # Only exports
    python scripts/upload_r2.py --dry-run      # Preview without uploading

What it does:
    - Connects to Cloudflare R2 using credentials from .env
    - Uploads audio files to {bucket}/audio/{lang}/{file}.mp3
    - Uploads Anki .apkg files to {bucket}/exports/{file}.apkg
    - Only uploads files that don't exist yet (incremental)
    - Shows progress and summary
"""

import logging
import sys
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

AUDIO_DIR = PROJECT_ROOT / "data" / "audio"
EXPORTS_DIR = PROJECT_ROOT / "exports"


def get_r2_client():
    """Create a boto3 client configured for Cloudflare R2."""
    account_id = os.getenv("R2_ACCOUNT_ID")
    access_key = os.getenv("R2_ACCESS_KEY")
    secret_key = os.getenv("R2_SECRET_KEY")

    if not all([account_id, access_key, secret_key]):
        log.error(
            "Missing R2 credentials. Add R2_ACCOUNT_ID, R2_ACCESS_KEY, "
            "R2_SECRET_KEY to .env file."
        )
        sys.exit(1)

    endpoint = f"https://{account_id}.r2.cloudflarestorage.com"

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4", connect_timeout=10, retries={"max_attempts": 3}),
    )
    return client


def ensure_bucket(client, bucket_name):
    """Create bucket if it doesn't exist."""
    try:
        client.head_bucket(Bucket=bucket_name)
        log.info("Bucket '%s' exists.", bucket_name)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            log.info("Bucket '%s' does not exist. Creating...", bucket_name)
            try:
                client.create_bucket(Bucket=bucket_name)
                log.info("Bucket '%s' created successfully.", bucket_name)
                return True
            except ClientError as create_error:
                log.error("Failed to create bucket: %s", create_error)
                return False
        else:
            log.error("Error checking bucket: %s", e)
            return False


def file_exists_on_r2(client, bucket, key):
    """Check if a file already exists on R2."""
    try:
        client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError:
        return False


def upload_file(client, local_path, bucket, key, dry_run=False):
    """Upload a single file to R2. Returns True if uploaded, False if skipped."""
    if dry_run:
        log.info("  [DRY-RUN] Would upload: %s → %s", local_path.name, key)
        return "dry-run"

    if file_exists_on_r2(client, bucket, key):
        log.info("  ⏭️  Exists: %s", key)
        return "skipped"

    try:
        client.upload_file(str(local_path), bucket, key)
        size_kb = local_path.stat().st_size / 1024
        log.info("  ✅ Uploaded: %s (%.0f KB)", key, size_kb)
        return "uploaded"
    except ClientError as e:
        log.error("  ❌ Failed to upload %s: %s", key, e)
        return "failed"


def upload_audio(client, bucket, dry_run=False):
    """Upload all audio files incrementally."""
    audio_files = list(AUDIO_DIR.rglob("*.mp3"))
    # Exclude samples
    sample_files = set(AUDIO_DIR.rglob("samples/*.mp3"))
    audio_files = [f for f in audio_files if f not in sample_files]

    if not audio_files:
        log.warning("No audio files found in %s", AUDIO_DIR)
        return {"uploaded": 0, "skipped": 0, "failed": 0, "total": 0}

    log.info("Found %d audio files", len(audio_files))
    stats = {"uploaded": 0, "skipped": 0, "failed": 0, "total": len(audio_files)}

    for f in audio_files:
        # Build R2 key: audio/en/hello.mp3
        relative = f.relative_to(AUDIO_DIR)
        key = f"audio/{relative.as_posix()}"

        result = upload_file(client, f, bucket, key, dry_run)
        if result == "uploaded":
            stats["uploaded"] += 1
        elif result == "skipped":
            stats["skipped"] += 1
        elif result == "failed":
            stats["failed"] += 1

    return stats


def upload_exports(client, bucket, dry_run=False):
    """Upload all .apkg export files incrementally."""
    export_files = list(EXPORTS_DIR.glob("*.apkg"))

    if not export_files:
        log.warning("No .apkg files found in %s", EXPORTS_DIR)
        return {"uploaded": 0, "skipped": 0, "failed": 0, "total": 0}

    log.info("Found %d export files", len(export_files))
    stats = {"uploaded": 0, "skipped": 0, "failed": 0, "total": len(export_files)}

    for f in export_files:
        key = f"exports/{f.name}"

        result = upload_file(client, f, bucket, key, dry_run)
        if result == "uploaded":
            stats["uploaded"] += 1
        elif result == "skipped":
            stats["skipped"] += 1
        elif result == "failed":
            stats["failed"] += 1

    return stats


def print_summary(title, stats, duration=None):
    """Print formatted summary for a section."""
    print(f"\n{title}")
    print(f"  {'='*40}")
    print(f"  Total  : {stats['total']}")
    print(f"  Uploaded: {stats['uploaded']}")
    print(f"  Skipped : {stats['skipped']}")
    print(f"  Failed  : {stats['failed']}")
    print(f"  {'='*40}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Upload assets to Cloudflare R2")
    parser.add_argument("--audio-only", action="store_true", help="Only upload audio")
    parser.add_argument("--exports-only", action="store_true", help="Only upload exports")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be uploaded")
    args = parser.parse_args()

    bucket = os.getenv("R2_BUCKET", "language-hub")
    dry_run = args.dry_run

    # Show what we're about to do
    print(f"{'='*55}")
    print(f"Cloudflare R2 Upload{' (DRY-RUN)' if dry_run else ''}")
    print(f"{'='*55}")
    print(f"  Bucket: {bucket}")

    # Connect (skip in dry-run mode)
    client = None
    if not dry_run:
        client = get_r2_client()
        if not ensure_bucket(client, bucket):
            sys.exit(1)
    else:
        print(f"  Mode  : Preview only (no uploads)")

    upload_audio_flag = not args.exports_only or args.audio_only
    upload_exports_flag = not args.audio_only or args.exports_only

    total_uploaded = 0
    total_skipped = 0
    total_failed = 0

    if upload_audio_flag:
        log.info("\nUploading audio files...")
        audio_stats = upload_audio(client, bucket, dry_run)
        print_summary("Audio", audio_stats)
        total_uploaded += audio_stats["uploaded"]
        total_skipped += audio_stats["skipped"]
        total_failed += audio_stats["failed"]

    if upload_exports_flag:
        log.info("\nUploading export files...")
        export_stats = upload_exports(client, bucket, dry_run)
        print_summary("Exports", export_stats)
        total_uploaded += export_stats["uploaded"]
        total_skipped += export_stats["skipped"]
        total_failed += export_stats["failed"]

    # Final summary
    print(f"\n{'='*55}")
    print(f"OVERALL SUMMARY{' (DRY-RUN)' if dry_run else ''}")
    print(f"{'='*55}")
    print(f"  Uploaded: {total_uploaded}")
    print(f"  Skipped : {total_skipped}")
    print(f"  Failed  : {total_failed}")
    print(f"{'='*55}")

    if dry_run:
        print(f"\nRun without --dry-run to actually upload.")

    # Return exit code
    if total_failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
