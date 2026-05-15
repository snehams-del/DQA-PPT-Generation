from abc import ABC, abstractmethod

class CostImporter(ABC):
    """
    Abstract base class for all cost importers.
    """
    provider_name: str = ""

    @abstractmethod
    def get_applicable_contract_id(self) -> str:
        """
        Returns the ID of the contract this importer is responsible for.
        """
        pass

    @abstractmethod
    def get_current_spend(self) -> float:
        """
        Returns the absolute current spend from the provider.
        """
        pass
