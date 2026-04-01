#!/usr/bin/env python3
"""
GitLab Client for Feedback System

Uses GitLab CLI (glab) to create issues for feedback.
Requires: glab CLI installed and authenticated
"""

import subprocess
import json
from typing import Optional, Dict, Any
from pathlib import Path


class GitLabClient:
    """GitLab CLI wrapper for creating feedback issues."""

    def __init__(self, project_id: str):
        """
        Initialize GitLab client.

        Args:
            project_id: Project ID or namespace/project path
        """
        self.project_id = project_id

    def check_cli_available(self) -> bool:
        """Check if GitLab CLI is installed and authenticated."""
        try:
            result = subprocess.run(
                ["glab", "auth", "status"],
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
        Create a GitLab issue.

        Args:
            title: Issue title
            body: Issue body (markdown)
            labels: List of labels to apply

        Returns:
            Dict with 'success', 'url', 'iid' or 'error'
        """
        if not self.check_cli_available():
            return {
                "success": False,
                "error": "GitLab CLI not available or not authenticated. Run 'glab auth login' first."
            }

        cmd = [
            "glab", "issue", "create",
            "--repo", self.project_id,
            "--title", title,
            "--description", body
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
                # glab outputs the issue URL
                output = result.stdout.strip()

                # Try to extract URL and IID from output
                issue_url = None
                issue_iid = None

                for line in output.split("\n"):
                    line = line.strip()
                    if line.startswith("http"):
                        issue_url = line
                        # Extract IID from URL
                        parts = line.split("/issues/")
                        if len(parts) > 1:
                            issue_iid = parts[1].split("/")[0].split("#")[0]
                        break

                return {
                    "success": True,
                    "url": issue_url or output,
                    "iid": issue_iid
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr.strip() or result.stdout.strip() or "Unknown error"
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
        Format feedback as GitLab issue body.

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
    client = GitLabClient("namespace/project")

    if client.check_cli_available():
        print("GitLab CLI is available and authenticated")
    else:
        print("GitLab CLI is not available or not authenticated")
        print("Please run: glab auth login")
