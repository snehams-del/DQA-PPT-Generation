# Import the root_agent from your agent.py file
from .agent import root_agent

# Make it available as 'agent' when the package is imported
agent = root_agent

# You can also optionally define __all__ to specify what gets imported
# with "from capital_guess_game import *"
__all__ = ['agent', 'root_agent']
