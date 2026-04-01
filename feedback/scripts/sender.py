#!/usr/bin/env python3
"""
Unified Feedback Sender

Provides a unified interface for sending feedback to GitHub or GitLab.
"""

import json
import re
import hashlib
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

from github_client import GitHubClient
from gitlab_client import GitLabClient


class FeedbackSender:
    """Unified feedback sender supporting GitHub and GitLab."""

    def __init__(self, config_path: Optional[Path] = None, queue_path: Optional[Path] = None):
        """
        Initialize feedback sender.

        Args:
            config_path: Path to config.yaml
            queue_path: Path to feedback_queue.json
        """
        self.config_path = config_path or Path(__file__).parent.parent / "data" / "config.yaml"
        self.queue_path = queue_path or Path(__file__).parent.parent / "data" / "feedback_queue.json"

        self.config = self._load_config()
        self.queue = self._load_queue()

        # Initialize clients
        self.github_client = None
        self.gitlab_client = None

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            import yaml
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception:
            return {"enabled": False}

    def _load_queue(self) -> Dict[str, Any]:
        """Load feedback queue from JSON file."""
        try:
            with open(self.queue_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"version": "1.0", "sent": [], "pending": []}

    def _save_queue(self):
        """Save feedback queue to JSON file."""
        with open(self.queue_path, "w", encoding="utf-8") as f:
            json.dump(self.queue, f, indent=2, ensure_ascii=False)

    def is_enabled(self) -> bool:
        """Check if feedback system is enabled."""
        return self.config.get("enabled", False)

    def is_skill_excluded(self, skill_name: str) -> bool:
        """Check if a skill is in the exclusion list."""
        excluded = self.config.get("excluded_skills", [])
        return skill_name in excluded

    def sanitize_text(self, text: str) -> str:
        """
        Sanitize text by removing sensitive information.

        Args:
            text: Original text

        Returns:
            Sanitized text
        """
        if not text:
            return text

        sanitization = self.config.get("sanitization", {})

        # Remove paths
        if sanitization.get("remove_paths", True):
            # Replace Windows paths
            text = re.sub(r"[A-Za-z]:\\[^\s]+", "<PATH>", text)
            # Replace Unix paths
            text = re.sub(r"/home/[^\s]+", "<PATH>", text)
            text = re.sub(r"/Users/[^\s]+", "<PATH>", text)

        # Redact sensitive patterns
        redact_patterns = sanitization.get("redact_patterns", [])
        for pattern in redact_patterns:
            text = re.sub(pattern, "[REDACTED]", text, flags=re.IGNORECASE)

        return text

    def hash_filename(self, filename: str) -> str:
        """Hash a filename for privacy."""
        sanitization = self.config.get("sanitization", {})
        if not sanitization.get("hash_filenames", True):
            return filename

        # Keep extension
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        hashed = hashlib.md5(name.encode()).hexdigest()[:6]
        return f"file_{hashed}.{ext}" if ext else f"file_{hashed}"

    def get_environment(self) -> Dict[str, str]:
        """Collect environment information."""
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
        }

    def check_rate_limit(self) -> bool:
        """
        Check if rate limit allows sending.

        Returns:
            True if allowed, False if rate limited
        """
        rate_limit = self.config.get("rate_limit", {})
        max_per_day = rate_limit.get("max_per_day", 5)

        # Count today's sent items
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today_count = sum(
            1 for item in self.queue.get("sent", [])
            if item.get("timestamp", "").startswith(today)
        )

        return today_count < max_per_day

    def check_duplicate(self, dedupe_key: str) -> bool:
        """
        Check if feedback is a duplicate within merge window.

        Args:
            dedupe_key: Key for deduplication

        Returns:
            True if duplicate (should skip), False if new
        """
        rate_limit = self.config.get("rate_limit", {})
        merge_window = rate_limit.get("merge_window_hours", 24)

        # Check recent sent items
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=merge_window)

        for item in self.queue.get("sent", []):
            try:
                item_time = datetime.fromisoformat(item.get("timestamp", ""))
                if item_time > cutoff and item.get("dedupe_key") == dedupe_key:
                    return True
            except (ValueError, TypeError):
                continue

        return False

    def generate_dedupe_key(self, skill_name: str, error_type: str, scenario: str = "") -> str:
        """Generate a deduplication key."""
        key_data = f"{skill_name}:{error_type}:{scenario}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def send_feedback(
        self,
        skill_name: str,
        skill_version: str,
        feedback_type: str,
        channel: str,
        error_type: Optional[str] = None,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send feedback to the configured channel.

        Args:
            skill_name: Name of the skill
            skill_version: Version of the skill
            feedback_type: Type of feedback (e.g., "execution_failure")
            channel: "github" or "gitlab"
            error_type: Type of error (optional)
            error_message: Error message (optional)
            stack_trace: Stack trace (optional)
            additional_info: Additional information (optional)

        Returns:
            Result dict with 'success', 'url', or 'error'
        """
        # Check if enabled
        if not self.is_enabled():
            return {"success": False, "error": "Feedback system is disabled"}

        # Check exclusion
        if self.is_skill_excluded(skill_name):
            return {"success": False, "error": f"Skill '{skill_name}' is excluded from feedback"}

        # Sanitize sensitive data
        error_message = self.sanitize_text(error_message)
        stack_trace = self.sanitize_text(stack_trace)

        # Check rate limit
        if not self.check_rate_limit():
            return {"success": False, "error": "Daily rate limit reached"}

        # Check duplicate
        dedupe_key = self.generate_dedupe_key(skill_name, error_type or feedback_type)
        if self.check_duplicate(dedupe_key):
            return {"success": False, "error": "Duplicate feedback within merge window"}

        # Get environment
        environment = self.get_environment()

        # Send to appropriate channel
        if channel == "github":
            target = self.config.get("target", {}).get("github", {})
            repo = target.get("repo", "")
            labels = target.get("labels", ["feedback"])

            if not self.github_client:
                self.github_client = GitHubClient(repo)
            else:
                self.github_client.repo = repo

            body = self.github_client.format_feedback_body(
                skill_name=skill_name,
                skill_version=skill_version,
                feedback_type=feedback_type,
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
                environment=environment,
                additional_info=additional_info
            )

            title = f"[自动反馈] {skill_name} - {error_type or feedback_type}"
            result = self.github_client.create_issue(title=title, body=body, labels=labels)

        elif channel == "gitlab":
            target = self.config.get("target", {}).get("gitlab", {})
            project_id = target.get("project_id", "")
            labels = target.get("labels", ["feedback"])

            if not self.gitlab_client:
                self.gitlab_client = GitLabClient(project_id)
            else:
                self.gitlab_client.project_id = project_id

            body = self.gitlab_client.format_feedback_body(
                skill_name=skill_name,
                skill_version=skill_version,
                feedback_type=feedback_type,
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
                environment=environment,
                additional_info=additional_info
            )

            title = f"[自动反馈] {skill_name} - {error_type or feedback_type}"
            result = self.gitlab_client.create_issue(title=title, body=body, labels=labels)

        else:
            return {"success": False, "error": f"Unknown channel: {channel}"}

        # Record in queue if successful
        if result.get("success"):
            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "skill_name": skill_name,
                "feedback_type": feedback_type,
                "channel": channel,
                "dedupe_key": dedupe_key,
                "url": result.get("url"),
                "issue_number": result.get("number") or result.get("iid")
            }
            self.queue["sent"].append(record)
            self._save_queue()

        return result


def main():
    """Test the feedback sender."""
    import argparse

    parser = argparse.ArgumentParser(description="Send feedback")
    parser.add_argument("--skill", required=True, help="Skill name")
    parser.add_argument("--version", default="1.0.0", help="Skill version")
    parser.add_argument("--type", default="test", help="Feedback type")
    parser.add_argument("--channel", choices=["github", "gitlab"], default="github", help="Target channel")
    parser.add_argument("--error", help="Error message")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (don't actually send)")

    args = parser.parse_args()

    sender = FeedbackSender()

    if args.dry_run:
        print("Dry run mode - not sending")
        print(f"Skill: {args.skill}")
        print(f"Type: {args.type}")
        print(f"Channel: {args.channel}")
        print(f"Enabled: {sender.is_enabled()}")
        print(f"Rate limit OK: {sender.check_rate_limit()}")
        return

    result = sender.send_feedback(
        skill_name=args.skill,
        skill_version=args.version,
        feedback_type=args.type,
        channel=args.channel,
        error_message=args.error
    )

    if result.get("success"):
        print(f"Success! Issue created: {result.get('url')}")
    else:
        print(f"Failed: {result.get('error')}")


if __name__ == "__main__":
    main()
