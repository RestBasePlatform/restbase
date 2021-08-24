import json
import os

from fastapi.testclient import TestClient


def test_install_from_github(test_client: TestClient, test_module_url: str):
    request_body = {
        "source": "GithubURL",
        "github_url": test_module_url,
    }
    response = test_client.post("/v1/modules/install/", data=json.dumps(request_body))
    assert response.status_code == 200
    assert "TestModule" in os.listdir("./modules")


def test_install_from_release(test_client: TestClient):
    request_body = {
        "module_name": "TestModule",
        "version": "0.1",
        "source": "release",
    }
    response = test_client.post("/v1/modules/install/", data=json.dumps(request_body))
    assert response.status_code == 200
    assert "TestModule" in os.listdir("./modules")


def test_remove_module(test_client: TestClient):
    request_body = {
        "module_name": "TestModule",
        "version": "0.1",
        "source": "release",
    }
    response = test_client.post("/v1/modules/install/", data=json.dumps(request_body))
    assert response.status_code == 200
    assert "TestModule" in os.listdir("./modules")
    request_body = {
        "module_name": "TestModule",
        "version": "0.1",
    }
    response = test_client.delete("/v1/modules/delete/", data=json.dumps(request_body))
    assert response.status_code == 200
    assert "0.1" not in os.listdir("modules/TestModule")


def test_remove_all_modules(test_client: TestClient):
    request_body = {
        "module_name": "TestModule",
        "version": "0.1",
        "source": "release",
    }
    response = test_client.post("/v1/modules/install/", data=json.dumps(request_body))
    assert response.status_code == 200
    assert "TestModule" in os.listdir("./modules")
    response = test_client.delete("/v1/modules/delete/all/")
    assert response.status_code == 200
    assert "0.1" not in os.listdir("modules/TestModule")
