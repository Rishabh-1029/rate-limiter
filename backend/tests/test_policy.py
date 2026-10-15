# backend/tests/test_policy.py
import pytest
from pydantic import ValidationError

from app.models.policy import ClientIdentifierType, RateLimitAlgorithm, RateLimitPolicy
from app.core.policy import PolicyAlreadyExistsError, PolicyNotFoundError, PolicyRegistry


def test_valid_policy_creation():
    policy = RateLimitPolicy(
        name="public_api",
        max_requests=100,
        window_seconds=60,
    )
    assert policy.name == "public_api"
    assert policy.max_requests == 100
    assert policy.algorithm == RateLimitAlgorithm.FIXED_WINDOW
    assert policy.identifier_type == ClientIdentifierType.API_KEY


@pytest.mark.parametrize("invalid_kwargs", [
    {"name": "", "max_requests": 10, "window_seconds": 60},  # Empty name
    {"name": "test", "max_requests": 0, "window_seconds": 60},  # 0 limit
    {"name": "test", "max_requests": -5, "window_seconds": 60},  # Negative limit
    {"name": "test", "max_requests": 10, "window_seconds": 0},  # 0 window
    {"name": "test", "max_requests": 10, "window_seconds": -1},  # Negative window
])
def test_policy_invalid_constraints(invalid_kwargs):
    with pytest.raises(ValidationError):
        RateLimitPolicy(**invalid_kwargs)


def test_unknown_fields_are_forbidden():
    with pytest.raises(ValidationError):
        RateLimitPolicy(name="test", max_requests=10, window_seconds=60, extra_param="hack")


def test_state_key_generation():
    policy = RateLimitPolicy(name="checkout", max_requests=5, window_seconds=10, version=2)
    key = policy.build_rate_limit_key("client_xyz")
    assert key == "rl:checkout:v2:client_xyz"


def test_registry_registration_and_lookup():
    registry = PolicyRegistry()
    policy = RateLimitPolicy(name="auth", max_requests=5, window_seconds=30)

    registry.register(policy)
    retrieved = registry.get("auth")
    assert retrieved == policy


def test_registry_fails_on_missing_policy():
    registry = PolicyRegistry()
    with pytest.raises(PolicyNotFoundError):
        registry.get("non_existent_policy")


def test_registry_blocks_duplicate_without_overwrite():
    registry = PolicyRegistry()
    p1 = RateLimitPolicy(name="billing", max_requests=10, window_seconds=60)
    p2 = RateLimitPolicy(name="billing", max_requests=20, window_seconds=60)

    registry.register(p1)
    with pytest.raises(PolicyAlreadyExistsError):
        registry.register(p2)

    # Allowed with explicit overwrite
    registry.register(p2, overwrite=True)
    assert registry.get("billing").max_requests == 20