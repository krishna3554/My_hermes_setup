from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


def test_github_issue_url_infers_repo_and_requires_draft_pr_workflow():
    from mini_swe_runner import build_github_issue_prompt

    prompt = build_github_issue_prompt(
        "https://github.com/acme/widgets/issues/123",
    )

    assert "Target upstream repository: acme/widgets" in prompt
    assert "gh repo fork acme/widgets --clone=false" in prompt
    assert "gh pr create --draft --repo acme/widgets" in prompt
    assert "Never run `gh pr ready`" in prompt


def test_github_issue_reference_requires_explicit_repo():
    from mini_swe_runner import build_github_issue_prompt

    with pytest.raises(ValueError, match="--repo OWNER/REPO"):
        build_github_issue_prompt("#123")


def test_github_issue_url_rejects_mismatched_explicit_repo():
    from mini_swe_runner import build_github_issue_prompt

    with pytest.raises(ValueError, match="does not match"):
        build_github_issue_prompt(
            "https://github.com/acme/widgets/issues/123",
            repo="other/project",
        )


def test_run_task_kimi_omits_temperature():
    """Kimi models should NOT have client-side temperature overrides.

    The Kimi gateway selects the correct temperature server-side.
    """
    with patch("openai.OpenAI") as mock_openai:
        client = MagicMock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="done", tool_calls=[]))]
        )
        mock_openai.return_value = client

        from mini_swe_runner import MiniSWERunner

        runner = MiniSWERunner(
            model="kimi-for-coding",
            base_url="https://api.kimi.com/coding/v1",
            api_key="test-key",
            env_type="local",
            max_iterations=1,
        )
        runner._create_env = MagicMock()
        runner._cleanup_env = MagicMock()

        result = runner.run_task("2+2")

    assert result["completed"] is True
    assert "temperature" not in client.chat.completions.create.call_args.kwargs


def test_run_task_public_moonshot_kimi_k2_5_omits_temperature():
    """kimi-k2.5 on the public Moonshot API should not get a forced temperature."""
    with patch("openai.OpenAI") as mock_openai:
        client = MagicMock()
        client.base_url = "https://api.moonshot.ai/v1"
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="done", tool_calls=[]))]
        )
        mock_openai.return_value = client

        from mini_swe_runner import MiniSWERunner

        runner = MiniSWERunner(
            model="kimi-k2.5",
            base_url="https://api.moonshot.ai/v1",
            api_key="test-key",
            env_type="local",
            max_iterations=1,
        )
        runner._create_env = MagicMock()
        runner._cleanup_env = MagicMock()

        result = runner.run_task("2+2")

    assert result["completed"] is True
    assert "temperature" not in client.chat.completions.create.call_args.kwargs
