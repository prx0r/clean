import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GATE_PATH = ROOT / "scripts" / "nyaya-truthmap-gate.py"

spec = importlib.util.spec_from_file_location("nyaya_truthmap_gate", GATE_PATH)
nyaya_truthmap_gate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = nyaya_truthmap_gate
assert spec.loader is not None
spec.loader.exec_module(nyaya_truthmap_gate)


def base_claim(**overrides):
    claim = {
        "claim_id": "cl:test-gate-valid",
        "claim_text": "fMRI shows DMN decoupling during nondual states.",
        "targets": [{"target_id": "D3", "target_type": "discriminator"}],
        "source_type": "experiment",
        "source_id": "src:test",
        "pramana": "pratyaksa",
        "tradition_scope": "neuroscience",
        "hetu": "DMN decoupling is measured during nondual-state reports",
        "sadhya": "nondual states have an observable neural signature",
        "vyapti_statement": "If a state reliably produces a neural signature under controls, that signature bears on its empirical characterization.",
        "vyapti_confidence": 0.72,
        "log_bayes_factor": 0.3,
        "falsifier": {
            "type": "empirical",
            "condition": "Competently sampled nondual-state reports show no consistent neural signature under controls.",
            "status": "untested",
        },
    }
    claim.update(overrides)
    return claim


def failure_types(result):
    return {failure.fallacy_type for failure in result.failures}


class NyayaGateTests(unittest.TestCase):
    def test_gate_accepts_valid_empirical_claim(self):
        result = nyaya_truthmap_gate.validate(base_claim())

        self.assertEqual(result.outcome, "accepted")
        self.assertTrue(result.can_update_posterior)
        self.assertEqual(result.pramana, "pratyaksa")
        self.assertEqual(result.evidence_dimension, "empirical")
        self.assertEqual(result.failures, [])

    def test_gate_flags_savyabhicara_for_overclaiming_meditation(self):
        claim = base_claim(
            claim_id="cl:test-savyabhicara",
            claim_text="Meditation always produces nondual awareness; meditation proves consciousness is fundamental.",
            pramana="anumana",
            tradition_scope="contemplative",
            source_type="practitioner_report",
            hetu="meditation produces nondual awareness",
            sadhya="consciousness is fundamental",
            log_bayes_factor=1.0,
        )

        result = nyaya_truthmap_gate.validate(claim)

        self.assertIn("savyabhicara", failure_types(result))
        self.assertIn("asiddha", failure_types(result))
        self.assertEqual(result.outcome, "needs_review")
        self.assertFalse(result.can_update_posterior)

    def test_gate_flags_badhita_for_claim_contradicted_by_neuroscience(self):
        claim = base_claim(
            claim_id="cl:test-badhita",
            claim_text="Consciousness has no neural correlates; the brain is irrelevant to consciousness.",
            pramana="anumana",
            tradition_scope="idealism",
            source_type="paper",
            hetu="consciousness has no neural correlates",
            sadhya="the brain is irrelevant to consciousness",
            log_bayes_factor=0.8,
        )

        result = nyaya_truthmap_gate.validate(claim)

        self.assertIn("badhita", failure_types(result))
        self.assertEqual(result.outcome, "needs_review")
        self.assertFalse(result.can_update_posterior)

    def test_gate_accepts_faithful_textual_report(self):
        claim = base_claim(
            claim_id="cl:test-faithful-report",
            claim_text="Plotinus says the body is in the soul, not the soul in the body.",
            targets=[{"target_id": "crux:plotinus-body-soul-relation", "target_type": "crux"}],
            source_type="text",
            source_id="text:plotinus-enneads",
            pramana="sabda",
            tradition_scope="neoplatonic",
            claim_type="faithful_report",
            hetu="the passage reports Plotinus's body-in-soul thesis",
            sadhya="Plotinus should be represented as making that textual claim",
            vyapti_statement="If the passage faithfully reports the primary text, it may update textual provenance without asserting the metaphysical thesis.",
            log_bayes_factor=0.1,
            falsifier={
                "type": "philological",
                "condition": "The primary text or a stronger translation does not support this report.",
                "status": "untested",
            },
        )

        result = nyaya_truthmap_gate.validate(claim)

        self.assertEqual(result.outcome, "accepted")
        self.assertEqual(result.pramana, "sabda")
        self.assertEqual(result.evidence_dimension, "textual")
        self.assertEqual(result.failures, [])

    def test_gate_requires_falsifier(self):
        claim = base_claim(
            claim_id="cl:test-missing-falsifier",
            claim_text="Consciousness is fundamental.",
            pramana="sabda",
            tradition_scope="trika",
        )
        del claim["falsifier"]

        result = nyaya_truthmap_gate.validate(claim)

        self.assertEqual(result.outcome, "hollow")
        self.assertFalse(result.can_update_posterior)
        self.assertEqual(result.falsifier_status, "missing")

    def test_gate_requires_tradition_scope(self):
        claim = base_claim(
            claim_id="cl:test-missing-tradition",
            claim_text="The self is an illusion.",
            pramana="anumana",
        )
        claim.pop("tradition_scope")

        result = nyaya_truthmap_gate.validate(claim)

        self.assertEqual(result.tradition_scope, "unknown")
        self.assertEqual(result.outcome, "needs_review")
        self.assertFalse(result.can_update_posterior)

    def test_gate_parses_ascii_nnexpr_alias(self):
        claim = base_claim(
            claim_id="cl:test-valid-nnexpr",
            nn_expr="vyapti(difference,determination)",
        )

        result = nyaya_truthmap_gate.validate(claim)

        self.assertEqual(result.outcome, "accepted")
        self.assertEqual(result.nnexpr_probe.status, "parsed")
        self.assertEqual(
            result.nnexpr_probe.normalized_expression,
            "vyāpti(difference,determination)",
        )
        self.assertEqual(result.nnexpr_probe.parsed_tree["kind"], "binary")

    def test_invalid_nnexpr_blocks_bridge_claim(self):
        claim = base_claim(
            claim_id="cl:test-invalid-bridge-nnexpr",
            claim_text="This is a bridge candidate to a same formal node.",
            targets=[{"target_id": "bridge:test", "target_type": "bridge"}],
            pramana="upamana",
            evidence_dimension="analogical",
            nn_expr="vyapti(difference)",
            tradition_scope="cross_tradition",
        )

        result = nyaya_truthmap_gate.validate(claim)

        self.assertEqual(result.nnexpr_probe.status, "invalid")
        self.assertEqual(result.outcome, "needs_review")
        self.assertFalse(result.can_update_posterior)
        self.assertIn("NNExpr", result.reasoning)

    def test_invalid_nnexpr_on_ordinary_claim_is_visible_but_not_blocking(self):
        claim = base_claim(
            claim_id="cl:test-invalid-ordinary-nnexpr",
            nn_expr="vyapti(difference)",
        )

        result = nyaya_truthmap_gate.validate(claim)

        self.assertEqual(result.nnexpr_probe.status, "invalid")
        self.assertEqual(result.outcome, "accepted")
        self.assertTrue(result.can_update_posterior)

    def test_result_json_preserves_nnexpr_metadata(self):
        claim = base_claim(
            claim_id="cl:test-result-json-nnexpr",
            nn_expr="abheda(duration,invariance)",
        )

        data = nyaya_truthmap_gate.result_to_json(nyaya_truthmap_gate.validate(claim))

        self.assertEqual(data["nnexpr_probe"]["status"], "parsed")
        self.assertEqual(
            data["nnexpr_probe"]["parsed_tree"]["op"],
            "abheda",
        )


if __name__ == "__main__":
    unittest.main()
