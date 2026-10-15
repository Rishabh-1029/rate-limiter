from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field


# Rate-Limit Algorithms
class RateLimitAlgorithm(StrEnum):
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"

# Client Identifiers
class ClientIdentifierType(StrEnum):
    API_KEY = "api_key"
    IP_ADDRESS = "ip_address"
    USER_ID = "user_id"

# Policy Object
class RateLimitPolicy(BaseModel):

    model_config = ConfigDict(frozen = True, extra = "forbid")

    name: str = Field(
        ...,
        min_length = 1,
        description = "Unique name or label for the policy/service"
    )
    max_requests: int = Field(
        ...,
        gt=0,
        description = "Maximum number of request allowed"
    )
    window_seconds: int = Field(
        ...,
        gt=0,
        description = "Window size in seconds"
    )
    version: int = Field(
        default = 1,
        gt=0,
        description = "Policy version"
    )
    algorithm: RateLimitAlgorithm = Field(
        default = RateLimitAlgorithm.FIXED_WINDOW,
        description = "Rate Limit Algorithm, default: Fixed Window"
    )
    identifier_type: ClientIdentifierType = Field(
        default = ClientIdentifierType.API_KEY,
        description = "Client partion key, default: API key"
    )

    def build_rate_limit_key(self, client_id: str) -> str:
        """
        creates a namespaced state key for the storage layer
        Format: rl:{policy_name}:v{version}:{client_id}
        Example: rl:auth_service:v1:user_987
        """
        return f"rl:{self.name}:v{self.version}:{client_id}"

    
