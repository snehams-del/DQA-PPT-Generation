from .base import CostImporter

class MockProviderImporter(CostImporter):
    provider_name = "mock"

    def get_applicable_contract_id(self) -> str:
        # Returning a dummy contract ID for testing
        return "1DhBwF2yXlOSdlzkYIAaWqdRWdiFFjmLX"

    def get_current_spend(self) -> float:
        import random
        return random.uniform(500.0, 2000.0)
