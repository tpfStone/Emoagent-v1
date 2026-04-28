from pathlib import Path

from dotenv import dotenv_values

ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILES = [
    ".env.development",
    ".env.testing",
    ".env.production",
]
REQUIRED_KEYS = {
    "DATABASE_URL",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "REDIS_URL",
    "LLM_PROVIDER",
    "ENABLE_EMOTION_DETECTION",
    "ENV",
    "DEBUG",
    "LOG_LEVEL",
    "SECRET_KEY",
    "ENABLE_METRICS",
    "ENABLE_API_DOCS",
    "DB_POOL_SIZE",
    "DB_MAX_OVERFLOW",
    "DB_POOL_TIMEOUT",
}


def load_env_template(name: str) -> dict[str, str]:
    values = dotenv_values(ROOT_DIR / name)
    return {key: value for key, value in values.items() if value is not None}


def test_env_templates_are_parseable_and_have_required_keys():
    for env_file in ENV_FILES:
        values = load_env_template(env_file)

        assert values, f"{env_file} should parse at least one key"
        assert REQUIRED_KEYS.issubset(values.keys())


def test_testing_env_disables_slow_or_runtime_only_features():
    values = load_env_template(".env.testing")

    assert values["ENV"] == "testing"
    assert values["LLM_PROVIDER"] == "mock"
    assert values["ENABLE_EMOTION_DETECTION"].lower() == "false"
    assert values["ENABLE_METRICS"].lower() == "false"
    assert values["ENABLE_API_DOCS"].lower() == "true"


def test_production_env_keeps_required_secret_placeholders():
    values = load_env_template(".env.production")

    assert values["ENV"] == "production"
    assert values["LLM_PROVIDER"] == "deepseek"
    assert values["ENABLE_API_DOCS"].lower() == "false"
    assert values["POSTGRES_PASSWORD"].startswith("CHANGE_THIS")
    assert values["REDIS_PASSWORD"].startswith("CHANGE_THIS")
    assert values["DEEPSEEK_API_KEY"].startswith("CHANGE_THIS")
    assert values["SECRET_KEY"].startswith("CHANGE_THIS")
    assert values["GRAFANA_PASSWORD"].startswith("CHANGE_THIS")
