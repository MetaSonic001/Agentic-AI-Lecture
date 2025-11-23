import sys, os
# Ensure package import resolution
sys.path.insert(0, os.path.dirname(__file__))

# Import modules
from orchestrator import ResearchOrchestrator
import planner_agent

# Monkeypatch the Agent.run method to avoid calling external LLMs
try:
    import agno.agent as ag_agent_module
    original_run = getattr(ag_agent_module.Agent, 'run', None)
except Exception:
    ag_agent_module = None
    original_run = None

class DummyResponse:
    def __init__(self, content):
        self.content = content

def dummy_run(self, prompt, *args, **kwargs):
    # Return a simple dummy response object with a .content attribute
    return DummyResponse("DUMMY_CONTENT for prompt: " + (prompt[:240] if isinstance(prompt, str) else str(prompt)))

if ag_agent_module and original_run is not None:
    ag_agent_module.Agent.run = dummy_run
else:
    # Also patch planner_agent.Agent if direct import used
    try:
        planner_agent.Agent.run = dummy_run
    except Exception:
        pass


def status_cb(s):
    print('STATUS:', s)

print('Starting smoke test (no external LLM calls)')
orch = ResearchOrchestrator(status_callback=status_cb)
result = orch.run_research('test topic for smoke run')
print('WORKFLOW RESULT:')
print(result)

# Restore original run if possible
if ag_agent_module and original_run is not None:
    ag_agent_module.Agent.run = original_run

print('Test complete')
