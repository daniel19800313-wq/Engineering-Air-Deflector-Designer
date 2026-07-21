"""Simulation workspace HTTP contract tests."""
import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.api.simulation import WorkspaceSimulationRequest, _solver_input


def request_payload(free_area_ratio=0.7, deflectors=None):
    return {
        "grille_width_mm": 4000,
        "grille_height_mm": 2000,
        "plenum_depth_mm": 2000,
        "inlet_width_mm": 400,
        "inlet_height_mm": 400,
        "inlet": {"position": {"x": 0, "y": 0, "z": 2}, "direction": {"x": 0, "y": 0, "z": -1}},
        "fans": [{"equipment_id": "SF-501", "enabled": True, "frequency_hz": 50}, {"equipment_id": "SF-502", "enabled": False, "frequency_hz": 0}],
        "rows": 2,
        "columns": 4,
        "outlet_width_mm": 300,
        "outlet_height_mm": 300,
        "free_area_ratio": free_area_ratio,
        "deflectors": [] if deflectors is None else deflectors,
    }


class SimulationApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_zero_deflector_baseline_returns_solver_results(self):
        response = self.client.post("/api/v1/simulations/airflow", json=request_payload())
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["deflector_count"], 0)
        self.assertEqual(len(body["outlets"]), 8)
        self.assertTrue(body["conserved"])

    def test_free_area_and_velocity_are_solver_owned(self):
        body = self.client.post("/api/v1/simulations/airflow", json=request_payload(0.7)).json()
        outlet = body["outlets"][0]
        self.assertEqual(outlet["free_area_ratio"]["value"], 0.7)
        self.assertEqual(outlet["outlet_velocity_mps"]["availability"], "available")
        self.assertAlmostEqual(body["total_outlet_airflow_cfm"]["value"], (110000 * 50 / 60) / 1.69901082)

    def test_free_area_wire_contract_accepts_ratio_and_rejects_ui_percent(self):
        accepted = self.client.post("/api/v1/simulations/airflow", json=request_payload(0.7))
        self.assertEqual(accepted.status_code, 200)
        payload = request_payload(0.7)
        payload["free_area_percent"] = "70"
        rejected = self.client.post("/api/v1/simulations/airflow", json=payload)
        self.assertEqual(rejected.status_code, 422)
        self.assertIn("extra_forbidden", rejected.text)

    def test_missing_free_area_never_fabricates_velocity(self):
        body = self.client.post("/api/v1/simulations/airflow", json=request_payload(None)).json()
        velocity = body["outlets"][0]["outlet_velocity_mps"]
        self.assertIsNone(velocity["value"])
        self.assertEqual(velocity["unavailable_reason"], "OUTLET_VELOCITY_FREE_AREA_RATIO_UNAVAILABLE")

    def test_non_eight_cell_grid_is_rejected_explicitly(self):
        payload = request_payload(); payload["columns"] = 3
        response = self.client.post("/api/v1/simulations/airflow", json=payload)
        self.assertEqual(response.status_code, 422)
        self.assertIn("exactly eight outlets", response.text)

    def test_inlet_boundary_is_normalized_and_forwarded_to_solver(self):
        directions = ((0, 0, -2), (0, 0, 3), (4, 0, 0), (-5, 0, 0), (0, 6, 0), (0, -7, 0), (1, 2, -2))
        for x, y, z in directions:
            with self.subTest(direction=(x, y, z)):
                payload = request_payload()
                payload["inlet"] = {"position": {"x": 0.1, "y": -0.1, "z": 1.8}, "direction": {"x": x, "y": y, "z": z}}
                solver_input = _solver_input(WorkspaceSimulationRequest.model_validate(payload))
                magnitude = (x * x + y * y + z * z) ** 0.5
                self.assertAlmostEqual(solver_input.inlet.direction.x, x / magnitude)
                self.assertAlmostEqual(solver_input.inlet.direction.y, y / magnitude)
                self.assertAlmostEqual(solver_input.inlet.direction.z, z / magnitude)
                self.assertEqual(solver_input.inlet.center_m.x, 0.1)
                self.assertEqual(solver_input.inlet.center_m.y, -0.1)
                self.assertEqual(solver_input.inlet.center_m.z, 1.8)

    def test_zero_length_inlet_direction_is_rejected(self):
        payload = request_payload()
        payload["inlet"]["direction"] = {"x": 0, "y": 0, "z": 0}
        response = self.client.post("/api/v1/simulations/airflow", json=payload)
        self.assertEqual(response.status_code, 422)
        self.assertIn("must not be zero length", response.text)

    def test_verified_fan_profiles_apply_affinity_laws(self):
        payload = request_payload()
        payload["fans"] = [{"equipment_id": "SF-501", "enabled": True, "frequency_hz": 60}, {"equipment_id": "SF-502", "enabled": True, "frequency_hz": 50}]
        response = self.client.post("/api/v1/simulations/airflow", json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        fans = {item["equipment_id"]: item for item in response.json()["fan_operating_results"]}
        self.assertEqual(set(fans), {"SF-501", "SF-502"})
        self.assertEqual(fans["SF-501"]["motor_power_hp"]["value"], 100)
        self.assertAlmostEqual(fans["SF-501"]["current_airflow_cmh"]["value"], 110000)
        self.assertAlmostEqual(fans["SF-501"]["current_static_pressure_pa"]["value"], 1600)
        self.assertAlmostEqual(fans["SF-502"]["current_airflow_cmh"]["value"], 110000 * 50 / 60)
        self.assertAlmostEqual(fans["SF-502"]["current_static_pressure_pa"]["value"], 1600 * (50 / 60) ** 2)
        self.assertEqual(fans["SF-502"]["estimation_label"], "Estimated using Fan Affinity Laws")
        expected_total = (110000 + 110000 * 50 / 60) / 1.69901082
        self.assertAlmostEqual(response.json()["total_inlet_airflow_cfm"]["value"], expected_total)

    def test_disabled_fan_is_zero_and_does_not_emit_flow(self):
        body = self.client.post("/api/v1/simulations/airflow", json=request_payload()).json()
        sf502 = next(item for item in body["fan_operating_results"] if item["equipment_id"] == "SF-502")
        self.assertEqual(sf502["status"], "OFF")
        self.assertEqual(sf502["current_airflow_cmh"]["value"], 0)
        self.assertEqual(sf502["current_static_pressure_pa"]["value"], 0)

    def test_fan_frequency_above_nameplate_limit_is_rejected(self):
        payload = request_payload(); payload["fans"][0]["frequency_hz"] = 61
        self.assertEqual(self.client.post("/api/v1/simulations/airflow", json=payload).status_code, 422)

    def test_both_fans_off_is_rejected_without_solver_output(self):
        payload = request_payload(); payload["fans"] = [{"equipment_id": "SF-501", "enabled": False, "frequency_hz": 0}, {"equipment_id": "SF-502", "enabled": False, "frequency_hz": 0}]
        response = self.client.post("/api/v1/simulations/airflow", json=payload)
        self.assertEqual(response.status_code, 422)
        self.assertIn("At least one enabled fan", response.text)


if __name__ == "__main__":
    unittest.main()
