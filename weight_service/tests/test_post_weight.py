import pytest
from unittest.mock import patch, MagicMock


class TestPostWeightEndpoint:
    """Corrected essential tests for POST /weight"""

    #
    # Helpers to avoid repeating long patch lists
    #

    def mock_all_valid(self, mocker, truck_tara=2000, container_taras=None, last_weigh=None):
        """Utility to patch all helpers with consistent mocks"""
        if container_taras is None:
            container_taras = {"C1": 100, "C2": 150}

        # validate_truck_exists → True
        mocker.patch("Routes.post_weight.validate_truck_exists", return_value=True)

        # validate_containers → No errors
        mocker.patch("Routes.post_weight.validate_containers", return_value=[])

        # get_last_weigh
        mocker.patch("Routes.post_weight.get_last_weigh", return_value=last_weigh)

        # get_truck_tara
        mocker.patch("Routes.post_weight.get_truck_tara", return_value=truck_tara)

        # get_all_containers_info
        mocker.patch(
            "Routes.post_weight.get_all_containers_info",
            return_value=[{"container_id": cid, "weight": w} for cid, w in container_taras.items()],
        )

        # save_transaction → return new id
        mocker.patch("Routes.post_weight.save_transaction", return_value=100)

        # calculate_out_values for OUT flows
        mocker.patch(
            "Routes.post_weight.calculate_out_values",
            return_value=(truck_tara, 2550),
        )

    #
    # TESTS
    #

    def test_invalid_weight_not_integer(self, client):
        """Weight must be an integer"""
        resp = client.post("/weight", json={
            "direction": "in",
            "truck": "123-45-678",
            "containers": "C1",
            "weight": "aaa",
            "unit": "kg",
            "force": "false",
            "produce": "orange"
        })

        assert resp.status_code == 400
        assert "weight must be integer" in resp.get_json()["error"]

    def test_unregistered_truck(self, client, mocker):
        """Truck must be registered"""
        mocker.patch("Routes.post_weight.validate_truck_exists", return_value=False)

        resp = client.post("/weight", json={
            "direction": "in",
            "truck": "BADTRUCK",
            "containers": "C1",
            "weight": 1000,
            "unit": "kg",
            "force": "false",
            "produce": "orange"
        })

        assert resp.status_code == 400
        assert "Truck is not registered" in resp.get_json()["error"]

    def test_in_creates_new_session(self, client, mocker):
        """IN creates a new transaction"""
        self.mock_all_valid(mocker, last_weigh=None)

        resp = client.post("/weight", json={
            "direction": "in",
            "truck": "123-45-678",
            "containers": "C1,C2",
            "weight": 5000,
            "unit": "kg",
            "force": "false",
            "produce": "orange"
        })

        assert resp.status_code == 200
        body = resp.get_json()
        assert body["id"] == 100
        assert body["bruto"] == 5000

    def test_out_without_in_error(self, client, mocker):
        """OUT without a previous IN should be rejected"""
        self.mock_all_valid(mocker, last_weigh=None)

        resp = client.post("/weight", json={
            "direction": "out",
            "truck": "123-45-678",
            "containers": "C1",
            "weight": 4800,
            "unit": "kg",
            "force": "false",
            "produce": "orange"
        })

        assert resp.status_code == 400
        assert "OUT without a previous IN" in resp.get_json()["error"]

    def test_none_after_in_error(self, client, mocker):
        """NONE after IN should be rejected"""
        last = {
            "id": 5,
            "direction": "in",
            "session_id": 5,
            "bruto": 5000,
            "datetime": "2024-01-15 10:00:00"
        }

        self.mock_all_valid(mocker, last_weigh=last)

        resp = client.post("/weight", json={
            "direction": "none",
            "truck": "123-45-678",
            "containers": "C1",
            "weight": 100,
            "unit": "kg",
            "force": "false",
            "produce": "orange"
        })

        assert resp.status_code == 400
        assert "NONE after IN" in resp.get_json()["error"]

    def test_in_after_in_requires_force(self, client, mocker):
        """IN after IN without force should fail"""

        last = {
            "id": 99,
            "direction": "in",
            "session_id": 99,
            "bruto": 5000,
            "datetime": "2024-01-15 10:00:00"
        }

        self.mock_all_valid(mocker, last_weigh=last)

        resp = client.post("/weight", json={
            "direction": "in",
            "truck": "123-45-678",
            "containers": "C1",
            "weight": 5100,
            "unit": "kg",
            "force": "false",
            "produce": "orange"
        })

        assert resp.status_code == 400
        assert "requires force=true" in resp.get_json()["error"]

    def test_in_after_in_with_force(self, client, mocker):
        """IN after IN with force overwrites last weighs"""
        last = {
            "id": 10,
            "direction": "in",
            "session_id": 10,
            "bruto": 5000,
            "datetime": "2024-01-15 10:00:00"
        }

        self.mock_all_valid(mocker, last_weigh=last)

        resp = client.post("/weight", json={
            "direction": "in",
            "truck": "123-45-678",
            "containers": "C1",
            "weight": 5100,
            "unit": "kg",
            "force": "true",
            "produce": "orange"
        })

        assert resp.status_code == 200
        assert resp.get_json()["id"] == 100

    def test_out_with_unknown_container_neto_na(self, client, mocker):
        """If any container has unknown tara → neto=None"""

        # unknown container → weight=None
        mocker.patch("Routes.post_weight.validate_truck_exists", return_value=True)
        mocker.patch("Routes.post_weight.validate_containers", return_value=[])

        mocker.patch("Routes.post_weight.get_last_weigh", return_value={
            "id": 100,
            "direction": "in",
            "session_id": 100,
            "bruto": 5000,
            "datetime": "2024-01-15 10:00:00"
        })

        mocker.patch("Routes.post_weight.get_truck_tara", return_value=2000)

        mocker.patch("Routes.post_weight.get_all_containers_info", return_value=[
            {"container_id": "C1", "weight": 100},
            {"container_id": "C2", "weight": None},  # UNKNOWN!!
        ])

        # simulate calculate_out_values returning neto=None
        mocker.patch(
            "Routes.post_weight.calculate_out_values",
            return_value=(2000, None)
        )

        mocker.patch("Routes.post_weight.save_transaction", return_value=100)

        resp = client.post("/weight", json={
            "direction": "out",
            "truck": "123-45-678",
            "containers": "C1,C2",
            "weight": 4800,
            "unit": "kg",
            "force": "false",
            "produce": "orange"
        })

        assert resp.status_code == 200
        assert resp.get_json()["neto"] is None

    def test_complete_in_out_flow(self, client, mocker):
        """IN → OUT end-to-end logic"""
        # IN phase
        self.mock_all_valid(mocker, last_weigh=None)

        resp_in = client.post("/weight", json={
            "direction": "in",
            "truck": "123-45-678",
            "containers": "C1,C2",
            "weight": 5000,
            "unit": "kg",
            "force": "false",
            "produce": "orange"
        })
        assert resp_in.status_code == 200

        # OUT phase
        last = {
            "id": 100,
            "direction": "in",
            "session_id": 100,
            "bruto": 5000,
            "datetime": "2024-01-15 10:00:00"
        }
        self.mock_all_valid(mocker, last_weigh=last)

        resp_out = client.post("/weight", json={
            "direction": "out",
            "truck": "123-45-678",
            "containers": "C1,C2",
            "weight": 4800,
            "unit": "kg",
            "force": "false",
            "produce": "orange"
        })

        assert resp_out.status_code == 200
        body = resp_out.get_json()
        assert body["neto"] == 2550
        assert body["truckTara"] == 2000
