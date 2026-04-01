#!/usr/bin/env python3
"""
GitHub Client for Feedback System

Uses GitHub CLI (gh) to create issues for feedback.
Requires: gh CLI installed and authenticated
"""

import subprocess
import json
from typing import Optional, Dict, Any
from pathlib import Path


class GitHubClient:
    """GitHub CLI wrapper for creating feedback issues."""

    def __init__(self, repo: str):
        """
        Initialize GitHub client.

        Args:
            repo: Repository in format 'owner/repo'
        """
        self.repo = repo

    def check_cli_available(self) -> bool:
        """Check if GitHub CLI is installed and authenticated."""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Create a GitHub issue.

        Args:
            title: Issue title
            body: Issue body (markdown)
            labels: List of labels to apply

        Returns:
            Dict with 'success', 'url', 'number' or 'error'
        """
        if not self.check_cli_available():
            return {
                "success": False,
                "error": "GitHub CLI not available or not authenticated. Run 'gh auth login' first."
            }

        cmd = [
            "gh", "issue", "create",
            "--repo", self.repo,
            "--title", title,
            "--body", body
        ]

        if labels:
            cmd.extend(["--label", ",".join(labels)])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                issue_url = result.stdout.strip()
                # Extract issue number from URL
                issue_number = issue_url.split("/")[-1] if issue_url else None

                return {
                    "success": True,
                    "url": issue_url,
                    "number": issue_number
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr.strip() or "Unknown error"
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Request timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def format_feedback_body(
        self,
        skill_name: str,
        skill_version: str,
        feedback_type: str,
        error_type: Optional[str] = None,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
        environment: Optional[Dict[str, str]] = None,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format feedback as GitHub issue body.

        Returns:
            Markdown formatted body
        """
        lines = [
            f"## [自动反馈] {skill_name} - {feedback_type}",
            "",
            f"**Skill**: {skill_name} v{skill_version}",
            f"**类型**: {feedback_type}",
            f"**时间**: {self._get_timestamp()}",
            ""
        ]

        if environment:
            lines.append("### 环境信息")
            for key, value in environment.items():
                lines.append(f"- **{key}**: {value}")
            lines.append("")

        if error_type:
            lines.extend([
                "### 错误信息",
                f"**错误类型**: `{error_type}`",
                ""
            ])

        if error_message:
            lines.extend([
                "```",
                error_message,
                "```",
                ""
            ])

        if stack_trace:
            lines.extend([
                "### 堆栈信息（已脱敏）",
                "```",
                stack_trace,
                "```",
                ""
            ])

        if additional_info:
            lines.extend([
                "### 附加信息",
                "```json",
                json.dumps(additional_info, indent=2, ensure_ascii=False),
                "```",
                ""
            ])

        lines.extend([
            "---",
            "*此反馈由自动反馈系统生成，不包含用户个人信息。*"
        ])

        return "\n".join(lines)

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    # Test the client
    client = GitHubClient("owner/repo")

    if client.check_cli_available():
        print("GitHub CLI is available and authenticated")
    else:
        print("GitHub CLI is not available or not authenticated")
        print("Please run: gh auth login")
