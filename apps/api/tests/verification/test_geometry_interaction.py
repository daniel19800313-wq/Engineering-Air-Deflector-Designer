"""Sprint 1.7 evaluator classifications, invariants, and regression tests."""
import tempfile
import unittest
from pathlib import Path

from app.solver.core import EngineeringValue
from app.solver.geometry import Vector3
from app.solver.geometry_interaction import DeclaredRouting, GeometryInteractionEvaluator, GeometryInteractionPolicy, GeometryInteractionStateAdapter, IncomingGeometricPath, InteractionClassification, PlanarDeflectorReference, RoutingClassification
from app.solver.results import ResultPackager, SolverProvenance
from app.solver.state import ExecutionState, SegmentState
from app.solver.visualization import VisualizationAdapter
from app.verification.interaction_runner import canonical_interaction_cases, result_payload, run


class GeometryInteractionTests(unittest.TestCase):
    def test_all_canonical_classifications(self) -> None:
        for case in canonical_interaction_cases():
            payload = result_payload(case)
            self.assertEqual(payload["interaction"], case.expected_interaction, case.case_id)
            self.assertEqual(payload["routing"], case.expected_routing, case.case_id)

    def test_routing_cannot_select_undeclared_cv(self) -> None:
        case = canonical_interaction_cases()[1]
        routing = DeclaredRouting(("CV_CONTINUE",), "CV_CONTINUE", "NOT_DECLARED", False)
        result = GeometryInteractionEvaluator().evaluate(case.path, case.plate, routing, case.policy)
        self.assertEqual(result.routing, RoutingClassification.REJECTED)
        self.assertIsNone(result.selected_downstream_cv_id)

    def test_no_engineering_magnitude_or_recommendation_created(self) -> None:
        payload = result_payload(canonical_interaction_cases()[1])
        self.assertEqual(payload["engineering_magnitudes"], {})
        self.assertIsNone(payload["recommendation"])

    def test_deterministic_geometry_is_byte_stable(self) -> None:
        case = canonical_interaction_cases()[1]
        self.assertEqual(result_payload(case), result_payload(case))

    def test_provenance_preserved(self) -> None:
        case = canonical_interaction_cases()[1]
        result = result_payload(case)
        self.assertEqual(result["provenance"]["path_id"], case.path.path_id)
        self.assertEqual(result["provenance"]["evaluator_version"], case.policy.evaluator_version)

    def test_failed_adapter_does_not_mutate_accepted_state(self) -> None:
        case = canonical_interaction_cases()[4]
        value = EngineeringValue.unavailable("not physics")
        accepted = SegmentState("accepted", value, value, value)
        adapter = GeometryInteractionStateAdapter(GeometryInteractionEvaluator(), case.path, case.plate, case.routing, case.policy)
        with self.assertRaises(ValueError): adapter.evaluate(accepted, case.plate.deflector_id)
        self.assertEqual(accepted.node_id, "accepted")

    def test_accepted_adapter_returns_candidate_without_mutation(self) -> None:
        case = canonical_interaction_cases()[1]
        value = EngineeringValue.unavailable("not physics")
        accepted = SegmentState("accepted", value, value, value)
        adapter = GeometryInteractionStateAdapter(GeometryInteractionEvaluator(), case.path, case.plate, case.routing, case.policy)
        candidate = adapter.evaluate(accepted, case.plate.deflector_id)
        self.assertEqual(accepted.node_id, "accepted")
        self.assertEqual(candidate.node_id, "CV_REDIRECT")
        self.assertIs(candidate.remaining_flow, accepted.remaining_flow)

    def test_failed_result_visualization_isolated(self) -> None:
        package = ResultPackager().package_conceptual(ExecutionState.FAILED, SolverProvenance("s", "v", "r", "p", "a"), (), None, ())
        self.assertEqual(VisualizationAdapter().create_payload(package).cells, ())

    def test_intentionally_corrupted_golden_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            run(target, update=True, confirmed=True)
            path = target / "face-intersection.json"
            path.write_text(path.read_text(encoding="utf-8").replace("face_intersection", "no_intersection"), encoding="utf-8")
            self.assertNotEqual(run(target), 0)


if __name__ == "__main__": unittest.main()
