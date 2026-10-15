from typing import Optional
from app.models.policy import RateLimitPolicy

class PolicyAlreadyExistsError(Exception):
    """ Raised when policy already exists """
    pass

class PolicyNotFoundError(KeyError):
    """ Raises when policy not found """
    pass

class PolicyRegistry:
    """ Manages active Rate limit polices in memory and lookup logic """

    def __init__(self) -> None:
        self._policies: dict[str, RateLimitPolicy] = {}

    def register(self, policy: RateLimitPolicy, overwrite: bool = False) -> None:
        """
        Register a new policy.
        Fails fast if a policy with the same name already exists unless overwrite=True.
        """
        if policy.name in self._policies and not overwrite:
            raise PolicyAlreadyExistsError(
                f"Policy {policy.name} is already registered"
                f"Pass Overwrite = True, if overwrite is intentional"
            )
        self._policies[policy.name] = policy

    def get(self, name: str) -> RateLimitPolicy:
        """
        Retrieve a policy by exact name.
        Fails explicitly if the policy does not exist.
        """
        if name not in self._policies:
            raise PolicyNotFoundError(
                f"Rate policy: '{name}' not found"
            )
        return self._policies[name]
    
    def list_policies(self) -> list[RateLimitPolicy]:
        """ Return all registered policies """
        return list(self._policies.values())
    
    def unregister(self, name: str) -> None:
        """ Remove policy """
        if name not in self._policies:
            raise PolicyNotFoundError(
                f"Rate policy: '{name}' does not exist"
            )
        del self._policies[name]
        