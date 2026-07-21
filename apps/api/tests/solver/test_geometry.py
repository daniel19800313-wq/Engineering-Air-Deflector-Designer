"""Milestone 2 isolated geometry-engine tests."""
import unittest

from app.solver.geometry import BoxGeometry, GeometryModel, GeometryValidator, InletGeometry, OutletCellGeometry, Vector3


def valid_geometry() -> GeometryModel:
    outlets = tuple(
        OutletCellGeometry(f"R{r}C{c}", r, c, Vector3(float(c), float(r), 0), 0.1, 0.1, Vector3(0, 0, -1))
        for r in range(2) for c in range(4)
    )
    return GeometryModel(BoxGeometry(1, 1, 1), InletGeometry(Vector3(0, 0, 1), 0.2, 0.2, Vector3(1, 0, 0)), outlets, None)


class GeometryValidatorTests(unittest.TestCase):
    def test_accepts_structural_primary_geometry(self) -> None:
        self.assertTrue(GeometryValidator().validate(valid_geometry()).is_valid)

    def test_rejects_wrong_cell_count_without_repair(self) -> None:
        model = valid_geometry()
        invalid = GeometryModel(model.plenum, model.inlet, model.outlets[:-1], None)
        report = GeometryValidator().validate(invalid)
        self.assertFalse(report.is_valid)
        self.assertEqual(report.diagnostics[0].code, "GEOMETRY_OUTLET_COUNT")

    def test_rejects_non_finite_dimension(self) -> None:
        model = valid_geometry()
        invalid = GeometryModel(BoxGeometry(float("nan"), 1, 1), model.inlet, model.outlets, None)
        self.assertFalse(GeometryValidator().validate(invalid).is_valid)


if __name__ == "__main__":
    unittest.main()
