import re
import unittest
from pathlib import Path

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPOSITORY_ROOT / ".coderabbit.yaml"


class CodeRabbitConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))

    def test_config_is_a_valid_mapping_with_expected_top_level_sections(self):
        self.assertIsInstance(self.config, dict)
        self.assertEqual(
            set(self.config),
            {
                "language",
                "tone_instructions",
                "early_access",
                "reviews",
                "chat",
                "knowledge_base",
                "code_generation",
            },
        )

    def test_review_language_and_tone_are_valid(self):
        self.assertEqual(self.config["language"], "ru-RU")
        self.assertIsInstance(self.config["tone_instructions"], str)
        self.assertLessEqual(len(self.config["tone_instructions"]), 250)
        self.assertFalse(self.config["early_access"])

    def test_auto_review_covers_regular_branches_but_excludes_drafts(self):
        auto_review = self.config["reviews"]["auto_review"]

        self.assertTrue(auto_review["enabled"])
        self.assertTrue(auto_review["auto_incremental_review"])
        self.assertFalse(auto_review["drafts"])
        self.assertEqual(auto_review["base_branches"], [".*"])

        branch_pattern = re.compile(auto_review["base_branches"][0])
        for branch in ("main", "develop", "feature/resume-export"):
            with self.subTest(branch=branch):
                self.assertIsNotNone(branch_pattern.fullmatch(branch))

    def test_review_output_features_are_enabled_without_automatic_labels(self):
        reviews = self.config["reviews"]

        self.assertEqual(reviews["profile"], "assertive")
        for option in (
            "high_level_summary",
            "sequence_diagrams",
            "estimate_code_review_effort",
            "changed_files_summary",
            "review_details",
            "suggested_labels",
            "poem",
            "enable_prompt_for_ai_agents",
        ):
            with self.subTest(option=option):
                self.assertTrue(reviews[option])

        self.assertFalse(reviews["collapse_walkthrough"])
        self.assertFalse(reviews["auto_apply_labels"])

    def test_service_files_are_excluded_from_review(self):
        path_filters = self.config["reviews"]["path_filters"]

        self.assertEqual(len(path_filters), len(set(path_filters)))
        self.assertTrue(all(item.startswith("!") for item in path_filters))
        self.assertEqual(
            set(path_filters),
            {
                "!**/*.lock",
                "!**/poetry.lock",
                "!**/uv.lock",
                "!**/migrations/versions/**",
                "!**/*.min.js",
            },
        )

    def test_each_supported_python_layer_has_review_instructions(self):
        path_instructions = self.config["reviews"]["path_instructions"]
        instructions_by_path = {
            item["path"]: item["instructions"].strip() for item in path_instructions
        }

        self.assertEqual(
            set(instructions_by_path),
            {
                "**/*.py",
                "app/api/**/*.py",
                "**/{models,repositories,db}/**/*.py",
                "**/tests/**/*.py",
            },
        )
        for path, instructions in instructions_by_path.items():
            with self.subTest(path=path):
                self.assertTrue(instructions)

    def test_pre_merge_checks_warn_without_blocking(self):
        reviews = self.config["reviews"]

        self.assertFalse(reviews["request_changes_workflow"])
        self.assertEqual(
            {
                name: check["mode"]
                for name, check in reviews["pre_merge_checks"].items()
            },
            {
                "title": "warning",
                "description": "warning",
                "issue_assessment": "warning",
            },
        )
        title_requirements = reviews["pre_merge_checks"]["title"]["requirements"]
        self.assertIn("Conventional Commits", title_requirements)
        self.assertIn("72", title_requirements)

    def test_automated_review_tools_and_finishing_touches_are_configured(self):
        reviews = self.config["reviews"]

        self.assertTrue(reviews["finishing_touches"]["docstrings"]["enabled"])
        self.assertTrue(reviews["finishing_touches"]["unit_tests"]["enabled"])
        self.assertEqual(
            {
                name
                for name, settings in reviews["tools"].items()
                if settings["enabled"]
            },
            {"ruff", "gitleaks", "semgrep", "actionlint", "yamllint", "hadolint"},
        )
        self.assertFalse(reviews["tools"]["languagetool"]["enabled"])

    def test_chat_knowledge_and_generation_settings_remain_consistent(self):
        self.assertEqual(self.config["chat"], {"auto_reply": True, "art": True})
        self.assertEqual(
            self.config["knowledge_base"],
            {
                "learnings": {"scope": "local"},
                "pull_requests": {"scope": "local"},
                "web_search": {"enabled": True},
            },
        )
        self.assertEqual(
            self.config["code_generation"]["docstrings"]["language"],
            self.config["language"],
        )


if __name__ == "__main__":
    unittest.main()
