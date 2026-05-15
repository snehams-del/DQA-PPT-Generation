import importlib
import inspect
import pkgutil
import os
from typing import List, Type, Optional
from .base import CostImporter

def get_all_importer_classes() -> List[Type[CostImporter]]:
    """Dynamically loads and returns all CostImporter classes found in the package."""
    package_dir = os.path.dirname(__file__)
    importer_classes = []
    
    for _, module_name, _ in pkgutil.iter_modules([package_dir]):
        if module_name == 'base':
            continue
            
        try:
            module = importlib.import_module(f'.{module_name}', package=__name__)
            
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, CostImporter) and obj is not CostImporter:
                    importer_classes.append(obj)
        except ImportError as e:
            print(f"Warning: Failed to import {module_name}: {e}")
            
    return importer_classes

def get_importer_class(provider_name: str) -> Optional[Type[CostImporter]]:
    """Dynamically loads and returns the CostImporter class for the given provider."""
    classes = get_all_importer_classes()
    for obj in classes:
        if getattr(obj, 'provider_name', None) == provider_name:
            return obj
    return None
