from __future__ import annotations

import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from scripts.python import version_lineage as vl


POLICY_SPEC = importlib.util.spec_from_file_location(
    "repository_policy",
    vl.ROOT / ".github" / "scripts" / "check_repository_policy.py",
)
assert POLICY_SPEC and POLICY_SPEC.loader
repository_policy = importlib.util.module_from_spec(POLICY_SPEC)
POLICY_SPEC.loader.exec_module(repository_policy)


def row(schema: str, **values: str) -> dict[str, str]:
    return {field: values.get(field, "") for field in vl.SCHEMAS[schema]}


class VersionLineageTests(unittest.TestCase):
    def minimal_registries(self) -> dict[str, vl.Registry]:
        common = {
            "version_kind": "reconstructed/pre-git",
            "date_start": "2026-06-20",
            "first_evidence_date": "2026-06-20",
            "status": "current",
            "lineage_confidence": "three-source-confirmed",
            "main_change": "Test change",
            "data_change": "Data definition is explicit.",
            "method_change": "Method definition is explicit.",
            "result_presentation_change": "Result presentation is explicit.",
            "current_use": "Test current use",
            "evidence_visibility": "public",
            "public_evidence_paths": "repo://docs/results/test/report.md",
            "notes": "Test evidence boundary",
        }
        versions = [
            row(
                "version_registry.csv",
                canonical_id="data-base",
                display_name="Data base",
                namespace="data",
                current_truth_role="data-base",
                **{**common, "status": "current_data_base"},
            ),
            row(
                "version_registry.csv",
                canonical_id="scale-g185",
                display_name="G185",
                namespace="scale",
                current_truth_role="active-scale",
                **{**common, "version_kind": "sample_rule"},
            ),
            row(
                "version_registry.csv",
                canonical_id="g185-current",
                display_name="Current G185 method",
                namespace="g185",
                current_truth_role="parallel-method",
                **common,
            ),
        ]
        artifacts = [
            row(
                "artifact_registry.csv",
                artifact_id="data-base-artifact",
                canonical_id="data-base",
                role="analysis-input",
                status="present",
                path_uri="local://data/base.dta",
                storage_scope="repository-ignored",
                format="dta",
                size_bytes="100",
                sha256="a" * 64,
                row_count="69038",
                column_count="100",
                schema_sha256="b" * 64,
                builder_entrypoint="repo://scripts/python/build.py",
                observed_modified_at="2026-06-20T00:00:00+08:00",
                visibility="local",
                git_policy="never-track",
                lineage_confidence="three-source-confirmed",
                notes="Metadata only",
            )
        ]
        samples = [
            row(
                "sample_rules.csv",
                sample_rule_id="sample-g185",
                base_artifact_id="data-base-artifact",
                semantic_name="scale-g185",
                predicate_json=json.dumps({"main_sample": 1}, separators=(",", ":")),
                rule_vector="main_sample=1",
                row_count="46299",
                grid_count="13236",
                region_counts_json="{}",
                rule_code_path="repo://scripts/python/rules.py",
                rule_code_sha256="c" * 64,
                status="current",
                verified_at="2026-06-20",
            )
        ]
        methods = [
            row(
                "method_registry.csv",
                method_id="method-g185-current",
                canonical_id="g185-current",
                outcome="ln_yield",
                estimand="damage-avoidance margin",
                exposures="drought|heat",
                controls="gdd_10_30",
                fixed_effects="grid_id|year",
                inference="grid-clustered",
                bootstrap_method="wild-score",
                reps="999",
                seed="42",
                entrypoint="repo://scripts/python/run.py",
                claim_boundary="association, not identified causal mediation",
            )
        ]
        runs = [
            row(
                "analysis_runs.csv",
                analysis_run_id="run-g185-current",
                canonical_id="g185-current",
                input_artifact_ids="data-base-artifact",
                sample_rule_id="sample-g185",
                method_id="method-g185-current",
                entrypoint="repo://scripts/python/run.py",
                parameter_manifest="repo://quality_reports/test-manifest.json",
                environment_lock="repo://requirements.txt",
                result_manifest="repo://quality_reports/test-results.json",
                public_result="repo://docs/results/test/report.md",
                run_started_at="2026-06-20T00:00:00+08:00",
                run_completed_at="2026-06-20T01:00:00+08:00",
                reproducibility_status="verified_current",
            )
        ]
        conversations = [
            row(
                "conversation_registry.csv",
                thread_id="019ee65b-340f-7293-a148-7bf9fedd66c0",
                source_type="user",
                started_at="2026-06-20T00:00:00Z",
                ended_at="2026-06-20T01:00:00Z",
                scope_reason="disposition=relevant;exact-cwd",
                canonical_ids="g185-current",
                decision_summary="G185 method boundary",
                evidence_level="single-source-inferred",
                raw_committed="false",
            )
        ]
        changes = [
            row(
                "change_events.csv",
                event_id="event-1",
                thread_id="019ee65b-340f-7293-a148-7bf9fedd66c0",
                event_time="2026-06-20T00:30:00Z",
                tool="apply_patch",
                operation="update-file",
                path_or_artifact_id="repo://scripts/python/run.py",
                command_sha256="d" * 64,
                verification_status="verified-session",
                notes="Sanitized event",
            )
        ]
        data = {
            "version_registry.csv": versions,
            "version_aliases.csv": [
                row(
                    "version_aliases.csv",
                    alias="G185",
                    alias_scope="scale",
                    canonical_id="scale-g185",
                    meaning="Frozen sample rule",
                    collision_group="g185",
                    notes="Not a software version",
                )
            ],
            "artifact_registry.csv": artifacts,
            "data_lineage.csv": [],
            "sample_rules.csv": samples,
            "method_registry.csv": methods,
            "analysis_runs.csv": runs,
            "conversation_registry.csv": conversations,
            "change_events.csv": changes,
        }
        return {
            name: vl.Registry(name, vl.SCHEMAS[name], rows)
            for name, rows in data.items()
        }

    def test_minimal_registry_graph_is_valid(self) -> None:
        self.assertEqual(vl.validate_registries(self.minimal_registries()), [])

    def test_planned_not_run_forbids_execution_and_result_evidence(self) -> None:
        empty_fields = (
            "result_manifest",
            "public_result",
            "code_git_sha",
            "run_started_at",
            "run_completed_at",
        )
        def planned_registries() -> dict[str, vl.Registry]:
            registries = self.minimal_registries()
            version = next(
                row
                for row in registries["version_registry.csv"].rows
                if row["canonical_id"] == "g185-current"
            )
            version["status"] = "exploratory"
            version["current_truth_role"] = "planned-test-version"
            return registries

        registries = planned_registries()
        planned = registries["analysis_runs.csv"].rows[0]
        planned["reproducibility_status"] = "planned_not_run"
        for field in empty_fields:
            planned[field] = ""
        self.assertEqual(vl.validate_registries(registries), [])

        invalid_values = {
            "result_manifest": "repo://quality_reports/test-results.json",
            "public_result": "repo://docs/results/test/report.md",
            "code_git_sha": "a" * 40,
            "run_started_at": "2026-07-22T00:00:00+08:00",
            "run_completed_at": "2026-07-22T01:00:00+08:00",
        }
        for field, value in invalid_values.items():
            with self.subTest(field=field):
                invalid = planned_registries()
                candidate = invalid["analysis_runs.csv"].rows[0]
                candidate["reproducibility_status"] = "planned_not_run"
                for empty_field in empty_fields:
                    candidate[empty_field] = ""
                candidate[field] = value
                errors = vl.validate_registries(invalid)
                self.assertTrue(
                    any(
                        f"planned_not_run must leave {field} empty" in error
                        for error in errors
                    )
                )

    def test_failed_quality_gate_requires_execution_but_forbids_final_result(self) -> None:
        def failed_registries() -> dict[str, vl.Registry]:
            registries = self.minimal_registries()
            version = next(
                row
                for row in registries["version_registry.csv"].rows
                if row["canonical_id"] == "g185-current"
            )
            version["status"] = "exploratory"
            version["current_truth_role"] = "failed-quality-gate-test-version"
            failed = registries["analysis_runs.csv"].rows[0]
            failed.update(
                {
                    "result_manifest": "",
                    "public_result": "",
                    "code_git_sha": "a" * 40,
                    "run_started_at": "2026-07-23T00:50:12.816656Z",
                    "run_completed_at": "",
                    "reproducibility_status": "failed_quality_gate",
                }
            )
            return registries

        self.assertEqual(vl.validate_registries(failed_registries()), [])

        for field in ("code_git_sha", "run_started_at"):
            with self.subTest(missing=field):
                registries = failed_registries()
                registries["analysis_runs.csv"].rows[0][field] = ""
                errors = vl.validate_registries(registries)
                self.assertTrue(
                    any(
                        f"failed_quality_gate requires "
                        f"{'valid ' if field == 'run_started_at' else ''}{field}"
                        in error
                        for error in errors
                    )
                )

        invalid_values = {
            "code_git_sha": "not-a-git-sha",
            "run_started_at": "2026-07-23",
        }
        for field, value in invalid_values.items():
            with self.subTest(invalid=field):
                registries = failed_registries()
                registries["analysis_runs.csv"].rows[0][field] = value
                errors = vl.validate_registries(registries)
                expected = (
                    "invalid code_git_sha"
                    if field == "code_git_sha"
                    else "failed_quality_gate requires valid run_started_at"
                )
                self.assertTrue(any(expected in error for error in errors))

        forbidden_values = {
            "result_manifest": "repo://quality_reports/test-results.json",
            "public_result": "repo://docs/results/test/report.md",
            "run_completed_at": "2026-07-23T01:00:00Z",
        }
        for field, value in forbidden_values.items():
            with self.subTest(forbidden=field):
                registries = failed_registries()
                registries["analysis_runs.csv"].rows[0][field] = value
                errors = vl.validate_registries(registries)
                self.assertTrue(
                    any(
                        f"failed_quality_gate must leave {field} empty" in error
                        for error in errors
                    )
                )

    def test_climate_stress_planned_run_freezes_inputs_and_planned_edges(self) -> None:
        registries = vl.load_all()
        run = next(
            row
            for row in registries["analysis_runs.csv"].rows
            if row["analysis_run_id"]
            == "run-data-climate-stress-panel-v1-pilot-planned-20260722"
        )
        expected_inputs = {
            "data-v3-expanded-main",
            "data-v3-expanded-phenowindows",
            "climate-stress-era5-repair-required-v1",
            "climate-stress-gleam43a-2020-sm-bundle",
            "climate-stress-chm-spei-monthly-bundle",
            "climate-stress-chm-spei-2w",
            "climate-stress-daily-temperature-validation-2013-2019",
            "climate-stress-maize-phenology-2010-2019",
        }
        self.assertEqual(set(vl.split_ids(run["input_artifact_ids"])), expected_inputs)
        self.assertEqual(run["reproducibility_status"], "planned_not_run")
        for field in (
            "result_manifest",
            "public_result",
            "code_git_sha",
            "run_started_at",
            "run_completed_at",
        ):
            self.assertEqual(run[field], "")

        climate_runs = [
            row
            for row in registries["analysis_runs.csv"].rows
            if row["canonical_id"] == "data-climate-stress-2010-2019-v1"
        ]
        self.assertEqual(len(climate_runs), 4)
        self.assertEqual(
            sum(
                row["reproducibility_status"] == "planned_not_run"
                for row in climate_runs
            ),
            1,
        )
        self.assertEqual(
            sum(
                row["reproducibility_status"] == "failed_quality_gate"
                for row in climate_runs
            ),
            3,
        )
        failed_runs = {
            row["analysis_run_id"]: row
            for row in climate_runs
            if row["reproducibility_status"] == "failed_quality_gate"
        }
        self.assertEqual(
            set(failed_runs),
            {
                "run-data-climate-stress-panel-v1-pilot-fullscope-a-auditfix-20260723T000001",
                "run-data-climate-stress-panel-v1-pilot-fullscope-a-aggfix-20260723T054913",
                "run-data-climate-stress-panel-v1-pilot-fullscope-a-exportfix-20260723T112218Z",
            },
        )
        expected_failed_execution = {
            "run-data-climate-stress-panel-v1-pilot-fullscope-a-auditfix-20260723T000001": (
                "82cbbf80aa1a9280731cfaf24ba1fd4bd079f6aa",
                "2026-07-23T00:50:12.816656Z",
            ),
            "run-data-climate-stress-panel-v1-pilot-fullscope-a-aggfix-20260723T054913": (
                "46800627b7bab0e94a96eaff524c450cf98916e9",
                "2026-07-23T05:53:24.927504Z",
            ),
            "run-data-climate-stress-panel-v1-pilot-fullscope-a-exportfix-20260723T112218Z": (
                "29b4052d34932502a38c890f6359755bbdc5e402",
                "2026-07-23T11:24:17.380865Z",
            ),
        }
        for run_id, (code_sha, started_at) in expected_failed_execution.items():
            failed = failed_runs[run_id]
            self.assertEqual(failed["input_artifact_ids"], run["input_artifact_ids"])
            for field in (
                "method_id",
                "entrypoint",
                "parameter_manifest",
                "environment_lock",
            ):
                self.assertEqual(failed[field], run[field])
            self.assertEqual(failed["code_git_sha"], code_sha)
            self.assertEqual(failed["run_started_at"], started_at)
            for field in ("result_manifest", "public_result", "run_completed_at"):
                self.assertEqual(failed[field], "")
        version = next(
            row
            for row in registries["version_registry.csv"].rows
            if row["canonical_id"] == "data-climate-stress-2010-2019-v1"
        )
        self.assertEqual(
            version["current_truth_role"],
            "three_physical_pilots_failed_quality_gate_replacement_planned",
        )
        self.assertEqual(version["result_run_date"], "")

        artifacts = {
            row["artifact_id"]: row
            for row in registries["artifact_registry.csv"].rows
        }
        for artifact_id in expected_inputs:
            self.assertIn(artifact_id, artifacts)
            self.assertEqual(artifacts[artifact_id]["status"], "present")

        planned_pairs = {
            (row["input_artifact_id"], row["output_artifact_id"])
            for row in registries["data_lineage.csv"].rows
            if row["verification_status"] == "single-source-inferred"
        }
        direct_planned_inputs = expected_inputs.difference(
            {
                "climate-stress-era5-repair-required-v1",
                "climate-stress-gleam43a-2020-sm-bundle",
                "data-v3-expanded-main",
            }
        )
        for artifact_id in direct_planned_inputs:
            self.assertIn(
                (artifact_id, "data-climate-stress-panel-v1-pilot-output"),
                planned_pairs,
            )
            self.assertIn(
                (artifact_id, "data-climate-stress-panel-v1-full-output"),
                planned_pairs,
            )
        self.assertIn(
            (
                "data-climate-stress-panel-v1-pilot-output",
                "data-climate-stress-panel-v1-pilot-manifest",
            ),
            planned_pairs,
        )
        self.assertIn(
            (
                "data-climate-stress-panel-v1-full-output",
                "data-climate-stress-panel-v1-full-manifest",
            ),
            planned_pairs,
        )

    def test_post_git_user_decision_requires_sanitized_scope_contract(self) -> None:
        registries = self.minimal_registries()
        decision = row(
            "conversation_registry.csv",
            thread_id="019f8058-2f2f-7152-b3eb-d6eb004dee60",
            source_type="user",
            started_at="2026-07-22",
            ended_at="2026-07-22",
            scope_reason=(
                "included:post-git-user-decision;"
                "decision_id=decision-test-authorization-20260722;authorization-only"
            ),
            canonical_ids="g185-current",
            decision_summary=(
                "Scoped download authorization; existing files remain immutable; "
                "one method endpoint remains PENDING_USER_DECISION."
            ),
            evidence_level="direct-user-confirmed",
            raw_committed="false",
        )
        registries["conversation_registry.csv"].rows.append(decision)
        self.assertEqual(vl.validate_registries(registries), [])
        evidence = vl.generated_conversation_evidence(registries)
        self.assertIn("decision-test-authorization-20260722", evidence)
        self.assertIn("Git后用户授权决策", evidence)

        invalid = self.minimal_registries()
        invalid_decision = dict(decision)
        invalid_decision["scope_reason"] = "disposition=relevant;exact-cwd"
        invalid_decision["evidence_level"] = "single-source-inferred"
        invalid["conversation_registry.csv"].rows.append(invalid_decision)
        errors = vl.validate_registries(invalid)
        self.assertTrue(
            any("timestamp outside reconstruction window" in error for error in errors)
        )

        duplicate = self.minimal_registries()
        duplicate["conversation_registry.csv"].rows.append(dict(decision))
        second = dict(decision)
        second["thread_id"] = "019f8058-2f2f-7152-b3eb-d6eb004dee61"
        duplicate["conversation_registry.csv"].rows.append(second)
        errors = vl.validate_registries(duplicate)
        self.assertTrue(
            any("duplicate post-Git decision_id" in error for error in errors)
        )

    def test_detailed_changelog_has_three_change_dimensions(self) -> None:
        text = vl.generated_version_changelog(self.minimal_registries())
        self.assertIn("### 数据变化", text)
        self.assertIn("### 方法变化", text)
        self.assertIn("### 结果呈现变化", text)
        self.assertIn("damage-avoidance margin", text)
        self.assertIn("本版本运行使用或定义的样本规则", text)
        self.assertIn("rows=46299；grids=13236", text)
        self.assertIn("data-base-artifact", text)

    def test_reference_scale_requires_registered_sample_rule(self) -> None:
        registries = self.minimal_registries()
        registries["version_registry.csv"].rows.append(
            row(
                "version_registry.csv",
                canonical_id="scale-g057",
                display_name="G057",
                namespace="scale",
                version_kind="sample_rule",
                date_start="2026-06-11",
                first_evidence_date="2026-06-11",
                status="reference",
                lineage_confidence="three-source-confirmed",
                main_change="Reference scale",
                data_change="Frozen sample mask.",
                method_change="Reference evaluation.",
                result_presentation_change="Selection context only.",
                current_use="Reference",
                evidence_visibility="public",
                public_evidence_paths="repo://docs/results/test/report.md",
                notes="No sample row in this test fixture.",
            )
        )
        self.assertIn(
            "version_registry.csv: scale lacks registered sample rule: scale-g057",
            vl.validate_registries(registries),
        )

    def test_collection_never_writes_raw_text_or_absolute_project_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            sessions = base / "sessions"
            output = base / "output"
            sessions.mkdir()
            session = sessions / "rollout.jsonl"
            records = [
                {
                    "type": "session_meta",
                    "payload": {
                        "id": "019db408-ee6f-7552-be7e-206e06c45586",
                        "timestamp": "2026-04-22T00:00:00Z",
                        "cwd": str(vl.ROOT),
                        "source": "vscode",
                    },
                },
                {
                    "type": "response_item",
                    "timestamp": "2026-04-22T00:01:00Z",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": "TOP SECRET GGCP10 scale request"}
                        ],
                    },
                },
                {
                    "type": "response_item",
                    "timestamp": "2026-07-13T00:02:00Z",
                    "payload": {
                        "type": "custom_tool_call",
                        "name": "apply_patch",
                        "call_id": "call-after-cutoff",
                        "input": "\n".join(
                            [
                                "*** Begin Patch",
                                f"*** Update File: {vl.ROOT / 'scripts/python/after_cutoff.py'}",
                                "@@",
                                "+AFTER_CUTOFF_SENTINEL = True",
                                "*** End Patch",
                            ]
                        ),
                    },
                },
                {
                    "type": "response_item",
                    "timestamp": "2026-04-22T00:02:00Z",
                    "payload": {
                        "type": "custom_tool_call",
                        "name": "apply_patch",
                        "call_id": "call-1",
                        "input": "\n".join(
                            [
                                "*** Begin Patch",
                                f"*** Update File: {vl.ROOT / 'scripts/python/version_lineage.py'}",
                                "@@",
                                "-old_value = 1",
                                "+LEAK_SENTINEL = 'TOP SECRET patch body'",
                                "*** End Patch",
                            ]
                        ),
                    },
                },
            ]
            session.write_text("\n".join(json.dumps(item) for item in records), encoding="utf-8")
            count, events = vl.collect_conversations(
                sessions, output, vl.date(2026, 1, 1), vl.date(2026, 7, 13)
            )
            self.assertEqual((count, events), (1, 1))
            combined = (output / "conversation_registry.csv").read_text(encoding="utf-8")
            combined += (output / "change_events.csv").read_text(encoding="utf-8")
            self.assertNotIn("TOP SECRET", combined)
            self.assertNotIn("LEAK_SENTINEL", combined)
            self.assertNotIn("AFTER_CUTOFF_SENTINEL", combined)
            self.assertNotIn(str(vl.ROOT), combined)
            self.assertIn("raw_committed", combined)
            with (output / "conversation_registry.csv").open(encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(rows[0]["raw_committed"], "false")
            self.assertEqual(rows[0]["canonical_ids"], "")
            self.assertIn("temporal-screened=", rows[0]["scope_reason"])
            with (output / "change_events.csv").open(encoding="utf-8") as stream:
                event_rows = list(csv.DictReader(stream))
            self.assertEqual(event_rows[0]["operation"], "update-file")
            self.assertEqual(
                event_rows[0]["path_or_artifact_id"],
                "repo://scripts/python/version_lineage.py",
            )
            self.assertNotIn("\n", event_rows[0]["path_or_artifact_id"])
            self.assertLess(len(event_rows[0]["path_or_artifact_id"]), 200)

            registries = vl.load_all()
            for name in ("conversation_registry.csv", "change_events.csv"):
                path = output / name
                with path.open(encoding="utf-8") as stream:
                    collected_rows = list(csv.DictReader(stream))
                registries[name] = vl.Registry(name, vl.SCHEMAS[name], collected_rows)
            self.assertEqual(vl.validate_registries(registries, strict=True), [])

    def test_uri_traversal_and_ambiguous_aliases_are_rejected(self) -> None:
        self.assertIsNone(vl.resolve_local_uri("repo://../../outside.txt"))
        self.assertIsNone(vl.resolve_local_uri("local://../private.csv"))

        registries = self.minimal_registries()
        registries["version_aliases.csv"].rows.extend(
            [
                row(
                    "version_aliases.csv",
                    alias="v1",
                    alias_scope="report",
                    canonical_id="data-base",
                    meaning="Report collision",
                    collision_group="v1",
                    notes="Ambiguous by design",
                ),
                row(
                    "version_aliases.csv",
                    alias="v1",
                    alias_scope="data",
                    canonical_id="scale-g185",
                    meaning="Data collision",
                    collision_group="v1",
                    notes="Ambiguous by design",
                ),
            ]
        )
        registries["conversation_registry.csv"].rows[0]["canonical_ids"] = "v1"
        errors = vl.validate_registries(registries)
        self.assertTrue(any("ambiguous alias v1" in error for error in errors))

        registries = self.minimal_registries()
        registries["analysis_runs.csv"].rows[0]["parameter_manifest"] = (
            "repo://../../private.json"
        )
        errors = vl.validate_registries(registries)
        self.assertTrue(any("unsafe URI path" in error for error in errors))

        registries = self.minimal_registries()
        registries["conversation_registry.csv"].rows[0]["canonical_ids"] = "G185"
        errors = vl.validate_registries(registries)
        self.assertTrue(any("use canonical ID instead of alias G185" in error for error in errors))

    def test_malformed_region_counts_and_temporal_inversion_are_reported(self) -> None:
        registries = self.minimal_registries()
        registries["sample_rules.csv"].rows[0]["region_counts_json"] = "[1]"
        errors = vl.validate_registries(registries)
        self.assertTrue(any("region_counts_json must be an object" in error for error in errors))

        registries = self.minimal_registries()
        conversation = registries["conversation_registry.csv"].rows[0]
        conversation["started_at"] = "2026-06-19T14:00:00Z"
        conversation["ended_at"] = "2026-06-19T15:00:00Z"
        registries["change_events.csv"].rows[0]["event_time"] = "2026-06-19T14:30:00Z"
        errors = vl.validate_registries(registries)
        self.assertTrue(any("temporal inversion for g185-current" in error for error in errors))

    def test_topic_classifier_uses_registered_scale_search_id(self) -> None:
        canonical_ids, _ = vl.classify_topic("GGCP10 scale G057 G049")
        self.assertIn("scale-search-region-first", canonical_ids.split("|"))

    def test_repository_policy_detects_raw_sessions_and_missing_repo_uris(self) -> None:
        raw_record = (
            '{"type":"session_meta","payload":{"id":'
            '"019db408-ee6f-7552-be7e-206e06c45586"}}'
        )
        self.assertIsNotNone(repository_policy.RAW_TRANSCRIPT_PATTERN.search(raw_record))
        errors = repository_policy.validate_snapshot_repo_uris(
            {
                "quality_reports/version_registry.csv": (
                    "public_evidence_paths\nrepo://docs/missing.md\n"
                )
            },
            set(),
        )
        self.assertTrue(any("Missing repo URI target" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
