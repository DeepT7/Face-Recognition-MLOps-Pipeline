from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_required_deployment_files_exist():
    expected_files = [
        "Dockerfile",
        "docker-compose.yaml",
        "app/main.py",
        "requirements.txt",
    ]

    missing_files = [path for path in expected_files if not (ROOT / path).is_file()]

    assert missing_files == []


def test_compose_defines_api_and_triton_services():
    compose_file = (ROOT / "docker-compose.yaml").read_text(encoding="utf-8")

    assert "triton:" in compose_file
    assert "api:" in compose_file
    assert "TRITON_SERVER_URL=triton:8001" in compose_file
