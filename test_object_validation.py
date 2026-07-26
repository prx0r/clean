import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VALIDATOR_PATH = ROOT / "scripts" / "validate-objects.py"

spec = importlib.util.spec_from_file_location("validate_objects_module", VALIDATOR_PATH)
validate_objects = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validate_objects
assert spec.loader is not None
spec.loader.exec_module(validate_objects)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


class ObjectValidationTests(unittest.TestCase):
    def test_validator_catches_duplicate_eo_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            eo = {
                "eo_id": "eo:test",
                "schema_version": 2,
                "title": "Test EO",
                "status": "draft",
                "syllogism": {
                    "pratijna": {},
                    "hetu": {},
                    "udaharana": {},
                    "upanaya": {},
                    "nigamana": {},
                },
                "candidates": [
                    {"candidate_id": "cand:a"},
                    {"candidate_id": "cand:b"},
                ],
                "state_of_play": {
                    "summary": "summary",
                    "what_survives": "survives",
                    "what_is_weakened": "weakened",
                    "what_would_change_our_mind": "test",
                },
            }
            write_json(root / "content" / "essay-objects" / "eo-test.json", eo)
            write_json(root / "content" / "essay-objects" / "eo-test" / "eo.json", eo)

            issues = validate_objects.validate_all_eos(root)
            codes = {issue.code for issue in issues}

            self.assertIn("duplicate_eo_id", codes)

    def test_validator_catches_ro_question_link_typo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "content" / "research-objects" / "ro-test" / "ro.json",
                {
                    "ro_id": "ro:test",
                    "schema_version": 2,
                    "title": "Test RO",
                    "status": "draft",
                    "current_version": "1.0.0",
                    "sources": [{"source_id": "so:test"}],
                    "body": [{"passage_id": "p_001", "text": "text"}],
                    "bears_on_quequestions": [{"question_id": "q:test"}],
                },
            )

            issues = validate_objects.validate_all_ros(root)

            self.assertIn(
                "ro_bears_on_questions_typo",
                {issue.code for issue in issues},
            )

    def test_validator_accepts_minimal_argument_dossier(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "content" / "source-metaphysics" / "q-test.argument.json",
                {
                    "artifact_type": "argument_fabric_dossier",
                    "question_id": "q:test",
                    "question": "What is being tested?",
                    "candidate_explanations": [
                        {
                            "candidate_id": "cand:test",
                            "name": "Test candidate",
                            "hard_to_vary_core": ["core"],
                            "falsifiers": [{"condition": "break it"}],
                        }
                    ],
                    "cruxes": [
                        {
                            "crux_id": "crux:test",
                            "question": "A crux?",
                        }
                    ],
                },
            )

            issues = validate_objects.validate_all_dossiers(root)

            self.assertEqual([], [issue for issue in issues if issue.severity == "error"])

    def test_validator_accepts_generic_source_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "content" / "source-metaphysics" / "q-test.map.json",
                {
                    "artifact_type": "argument_fabric_source_map",
                    "question_id": "q:test",
                    "source_packet_id": "packet:test",
                    "nnexpr_mappings": [],
                    "argument_edges": [],
                    "bridge_probe_logic": {"current_classification": "OVERLAPS"},
                    "state_of_play_delta": {"current_best_answer": "test"},
                    "structural_correspondences": [
                        {
                            "correspondence_id": "corr:test",
                            "left_term": "nn:left",
                            "left_scope": "scope:left",
                            "right_term": "nn:right",
                            "right_scope": "scope:right",
                            "shared_structure": "shared",
                            "important_difference": "different",
                            "status": "OVERLAPS",
                        }
                    ],
                    "directional_critique_pairs": [
                        {
                            "pair_id": "critique:test",
                            "critic_lens": "scope:left",
                            "target_lens": "scope:right",
                            "reveals_about_target": "gap",
                            "pressure_type": "test_gap",
                            "target_response_required": "answer gap",
                            "status": "open",
                        }
                    ],
                },
            )

            issues = validate_objects.validate_all_source_maps(root)

            self.assertEqual([], [issue for issue in issues if issue.severity == "error"])

    def test_validator_rejects_source_map_missing_generic_arrays(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "content" / "source-metaphysics" / "q-test.map.json",
                {
                    "artifact_type": "argument_fabric_source_map",
                    "question_id": "q:test",
                    "source_packet_id": "packet:test",
                    "nnexpr_mappings": [],
                    "argument_edges": [],
                    "bridge_probe_logic": {"current_classification": "OVERLAPS"},
                    "state_of_play_delta": {"current_best_answer": "test"},
                },
            )

            issues = validate_objects.validate_all_source_maps(root)
            codes = {issue.code for issue in issues}

            self.assertIn("source_map_missing_structural_correspondences", codes)
            self.assertIn("source_map_missing_directional_critique_pairs", codes)

    def test_validator_rejects_bad_source_map_statuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "content" / "source-metaphysics" / "q-test.map.json",
                {
                    "artifact_type": "argument_fabric_source_map",
                    "question_id": "q:test",
                    "source_packet_id": "packet:test",
                    "nnexpr_mappings": [],
                    "argument_edges": [],
                    "structural_correspondences": [
                        {
                            "correspondence_id": "corr:test",
                            "left_term": "nn:left",
                            "left_scope": "scope:left",
                            "right_term": "nn:right",
                            "right_scope": "scope:right",
                            "shared_structure": "shared",
                            "important_difference": "different",
                            "status": "MERGED_BY_VIBES",
                        }
                    ],
                    "directional_critique_pairs": [
                        {
                            "pair_id": "critique:test",
                            "critic_lens": "scope:left",
                            "target_lens": "scope:right",
                            "reveals_about_target": "gap",
                            "pressure_type": "test_gap",
                            "target_response_required": "answer gap",
                            "status": "settled_forever",
                        }
                    ],
                },
            )

            issues = validate_objects.validate_all_source_maps(root)
            codes = {issue.code for issue in issues}

            self.assertIn("source_map_invalid_correspondence_status", codes)
            self.assertIn("source_map_invalid_critique_pair_status", codes)


if __name__ == "__main__":
    unittest.main()
