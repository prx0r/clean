import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROBE_PATH = ROOT / "scripts" / "probe-bridge.py"

spec = importlib.util.spec_from_file_location("probe_bridge_module_for_tests", PROBE_PATH)
probe_bridge = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = probe_bridge
assert spec.loader is not None
spec.loader.exec_module(probe_bridge)


def source_map_with_tests(formal_tests, *, declared_status="OVERLAPS"):
    return {
        "artifact_type": "argument_fabric_source_map",
        "question_id": "q:test",
        "structural_correspondences": [
            {
                "correspondence_id": "corr:test",
                "left_term": "nn:left",
                "left_scope": "scope:left",
                "right_term": "nn:right",
                "right_scope": "scope:right",
                "shared_structure": "shared structure",
                "important_difference": "important difference",
                "status": declared_status,
                "bridge_probe_id": "bridge:test",
            }
        ],
        "bridge_probe_logic": {
            "candidate_pair": {
                "surface_similarity": ["shared"],
            },
            "formal_tests": formal_tests,
        },
    }


class BridgeProbeTests(unittest.TestCase):
    def test_nanavira_bridge_defaults_to_overlap_without_proof(self):
        data = probe_bridge.load_json(
            ROOT
            / "content"
            / "source-metaphysics"
            / "q-reflexivity-intrinsic-or-constructed.nanavira-map.json"
        )

        result = probe_bridge.evaluate_source_map(data)

        self.assertEqual("OVERLAPS", result.status)
        self.assertIn("positive bridge probes are unproved", " ".join(result.notes))

    def test_bidirectional_proof_with_negative_controls_passed_bridges(self):
        data = source_map_with_tests(
            [
                {
                    "test_id": "bridge:left-to-right",
                    "probe": "Left -> Right",
                    "required_status_for_merge": "PROVED",
                    "actual_status": "PROVED",
                },
                {
                    "test_id": "bridge:right-to-left",
                    "probe": "Right -> Left",
                    "required_status_for_merge": "PROVED",
                    "actual_status": "PROVED",
                },
                {
                    "test_id": "bridge:negative-control",
                    "probe": "Left -> BadInflation",
                    "required_status_for_merge": "NOT_PROVED",
                    "actual_status": "NOT_PROVED",
                },
            ]
        )

        result = probe_bridge.evaluate_source_map(data)

        self.assertEqual("BRIDGES", result.status)

    def test_one_way_proof_only_subsumes(self):
        data = source_map_with_tests(
            [
                {
                    "test_id": "bridge:left-to-right",
                    "probe": "Left -> Right",
                    "required_status_for_merge": "PROVED",
                    "actual_status": "PROVED",
                },
                {
                    "test_id": "bridge:right-to-left",
                    "probe": "Right -> Left",
                    "required_status_for_merge": "PROVED",
                    "actual_status": "UNPROVED",
                },
            ]
        )

        result = probe_bridge.evaluate_source_map(data)

        self.assertEqual("SUBSUMES", result.status)

    def test_failed_negative_control_blocks_bridge(self):
        data = source_map_with_tests(
            [
                {
                    "test_id": "bridge:left-to-right",
                    "probe": "Left -> Right",
                    "required_status_for_merge": "PROVED",
                    "actual_status": "PROVED",
                },
                {
                    "test_id": "bridge:right-to-left",
                    "probe": "Right -> Left",
                    "required_status_for_merge": "PROVED",
                    "actual_status": "PROVED",
                },
                {
                    "test_id": "bridge:negative-control",
                    "probe": "Left -> BadInflation",
                    "required_status_for_merge": "NOT_PROVED",
                    "actual_status": "PROVED",
                },
            ]
        )

        result = probe_bridge.evaluate_source_map(data)

        self.assertEqual("DIFFERENT", result.status)
        self.assertIn("negative control failed", " ".join(result.notes))

    def test_declared_bridge_is_downgraded_when_probes_missing(self):
        data = source_map_with_tests([], declared_status="BRIDGES")

        result = probe_bridge.evaluate_source_map(data)

        self.assertEqual("OVERLAPS", result.status)
        self.assertIn("Declared correspondence is stronger", " ".join(result.notes))


if __name__ == "__main__":
    unittest.main()
