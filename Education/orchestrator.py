"""
Research Orchestrator using Agno Multi-Agent System.
Agno (formerly Phidata) provides lightweight multi-agent orchestration.
"""
from typing import Callable, Dict, Any
from datetime import datetime
from pathlib import Path
import os
import sys
# Ensure the `Education` folder is on sys.path so top-level imports inside
# `planner_agent.py` (e.g., `import config`) resolve to local modules.
sys.path.insert(0, os.path.dirname(__file__))
# Also ensure project root is on sys.path so sibling folders like `scripts/`
# can be imported (scripts.md_to_pdf). This makes PDF generation importable.
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from planner_agent import create_team_agent, create_planner_agent, create_worker_agent
from logger_setup import log
from config import OUTPUT_DIR
import requests
from worker_agent import WorkerAgent
from models import ResearchPlan, Task

# Quick instrumentation: wrap requests.Session.request to log outgoing JSON POSTs
# so we can inspect payloads sent to model APIs when debugging missing `content`.
_orig_request = requests.Session.request

def _logging_request(self, method, url, *args, **kwargs):
    # Only intercept POST JSON payloads and attempt to sanitize tool messages
    try:
        if method and method.upper() == 'POST':
            headers = kwargs.get('headers') or {}
            data = kwargs.get('data')
            json_payload = kwargs.get('json')

            # Determine payload dict
            payload = None
            if json_payload is not None:
                payload = json_payload
            else:
                # try parse data as JSON string
                try:
                    import json as _json
                    if isinstance(data, (bytes, str)):
                        payload = _json.loads(data)
                except Exception:
                    payload = None

            sanitized = False
            # Recursively search for any 'messages' lists in the payload and sanitize
            def _sanitize_recursive(obj):
                nonlocal sanitized
                try:
                    if isinstance(obj, dict):
                        # direct messages list
                        if 'messages' in obj and isinstance(obj['messages'], list):
                            for msg in obj['messages']:
                                if isinstance(msg, dict) and msg.get('role') == 'tool':
                                    if ('content' not in msg) or (msg.get('content') is None):
                                        args_obj = msg.get('arguments') or msg.get('args') or msg.get('tool_call_result') or None
                                        try:
                                            import json as _json2
                                            msg['content'] = _json2.dumps(args_obj) if args_obj is not None else ''
                                        except Exception:
                                            msg['content'] = str(args_obj) if args_obj is not None else ''
                            sanitized = True

                        # continue traversing
                        for v in obj.values():
                            _sanitize_recursive(v)
                    elif isinstance(obj, list):
                        for item in obj:
                            _sanitize_recursive(item)
                except Exception:
                    return

            if isinstance(payload, (dict, list)):
                _sanitize_recursive(payload)
                if sanitized:
                    kwargs['json'] = payload

            # Log sanitized payload or original json for debugging
            try:
                log_msg = f"REQUEST -> {url}\njson={payload if sanitized else json_payload}\ndata={data}\n"
                with open(os.path.join(os.path.dirname(__file__), 'groq_requests.log'), 'a', encoding='utf-8') as f:
                    f.write(datetime.now().isoformat() + ' ' + log_msg + '\n')
            except Exception:
                pass
    except Exception:
        pass

    return _orig_request(self, method, url, *args, **kwargs)

requests.Session.request = _logging_request

# Final-send sanitizers: wrap httpx sync/async request methods if httpx is present.
# Some Groq client implementations use httpx; intercepting httpx.request
# guarantees we sanitize the final payload immediately before the network send.
try:
    import httpx as _httpx

    if not getattr(_httpx, '_grai_sanitizer_wrapped', False):
        _orig_httpx_client_request = getattr(_httpx.Client, 'request', None)
        _orig_httpx_async_request = getattr(_httpx.AsyncClient, 'request', None)

        def _httpx_sanitize_request(self, method, url, *args, **kwargs):
            try:
                # Helper: recursive sanitizer that mutates dict/list in-place
                def _sanitize_recursive(obj):
                    try:
                        if isinstance(obj, dict):
                            if 'messages' in obj and isinstance(obj['messages'], list):
                                for msg in obj['messages']:
                                    if isinstance(msg, dict) and msg.get('role') == 'tool':
                                        if ('content' not in msg) or (msg.get('content') is None):
                                            args_obj = msg.get('arguments') or msg.get('args') or msg.get('tool_call_result') or None
                                            try:
                                                import json as _json2
                                                msg['content'] = _json2.dumps(args_obj) if args_obj is not None else ''
                                            except Exception:
                                                msg['content'] = str(args_obj) if args_obj is not None else ''
                            for v in list(obj.values()):
                                _sanitize_recursive(v)
                        elif isinstance(obj, list):
                            for item in obj:
                                _sanitize_recursive(item)
                    except Exception:
                        return

                # Try json= first
                if 'json' in kwargs and isinstance(kwargs['json'], (dict, list)):
                    _sanitize_recursive(kwargs['json'])

                # If data/content present, try to decode JSON, sanitize, and re-encode as needed
                for key in ('content', 'data'):
                    if key in kwargs and isinstance(kwargs[key], (bytes, str)):
                        try:
                            import json as _json
                            raw = kwargs[key]
                            if isinstance(raw, (bytes, bytearray)):
                                raw_decoded = raw.decode('utf-8')
                            else:
                                raw_decoded = raw
                            parsed = _json.loads(raw_decoded)
                            _sanitize_recursive(parsed)
                            new_payload = _json.dumps(parsed)
                            # Preserve original type
                            if isinstance(raw, (bytes, bytearray)):
                                kwargs[key] = new_payload.encode('utf-8')
                            else:
                                kwargs[key] = new_payload
                        except Exception:
                            # not JSON or decode failed; skip
                            pass

                # If data is a dict (httpx may accept), sanitize in-place
                if 'data' in kwargs and isinstance(kwargs['data'], (dict, list)):
                    _sanitize_recursive(kwargs['data'])

                # If content is a dict (unlikely) sanitize
                if 'content' in kwargs and isinstance(kwargs['content'], (dict, list)):
                    _sanitize_recursive(kwargs['content'])
            except Exception:
                pass
            return _orig_httpx_client_request(self, method, url, *args, **kwargs)

        async def _httpx_async_sanitize_request(self, method, url, *args, **kwargs):
            try:
                def _sanitize_recursive(obj):
                    try:
                        if isinstance(obj, dict):
                            if 'messages' in obj and isinstance(obj['messages'], list):
                                for msg in obj['messages']:
                                    if isinstance(msg, dict) and msg.get('role') == 'tool':
                                        if ('content' not in msg) or (msg.get('content') is None):
                                            args_obj = msg.get('arguments') or msg.get('args') or msg.get('tool_call_result') or None
                                            try:
                                                import json as _json2
                                                msg['content'] = _json2.dumps(args_obj) if args_obj is not None else ''
                                            except Exception:
                                                msg['content'] = str(args_obj) if args_obj is not None else ''
                            for v in list(obj.values()):
                                _sanitize_recursive(v)
                        elif isinstance(obj, list):
                            for item in obj:
                                _sanitize_recursive(item)
                    except Exception:
                        return

                if 'json' in kwargs and isinstance(kwargs['json'], (dict, list)):
                    _sanitize_recursive(kwargs['json'])

                for key in ('content', 'data'):
                    if key in kwargs and isinstance(kwargs[key], (bytes, str)):
                        try:
                            import json as _json
                            raw = kwargs[key]
                            if isinstance(raw, (bytes, bytearray)):
                                raw_decoded = raw.decode('utf-8')
                            else:
                                raw_decoded = raw
                            parsed = _json.loads(raw_decoded)
                            _sanitize_recursive(parsed)
                            new_payload = _json.dumps(parsed)
                            if isinstance(raw, (bytes, bytearray)):
                                kwargs[key] = new_payload.encode('utf-8')
                            else:
                                kwargs[key] = new_payload
                        except Exception:
                            pass

                if 'data' in kwargs and isinstance(kwargs['data'], (dict, list)):
                    _sanitize_recursive(kwargs['data'])

                if 'content' in kwargs and isinstance(kwargs['content'], (dict, list)):
                    _sanitize_recursive(kwargs['content'])
            except Exception:
                pass
            return await _orig_httpx_async_request(self, method, url, *args, **kwargs)

        if _orig_httpx_client_request is not None:
            _httpx.Client.request = _httpx_sanitize_request
        if _orig_httpx_async_request is not None:
            _httpx.AsyncClient.request = _httpx_async_sanitize_request

        setattr(_httpx, '_grai_sanitizer_wrapped', True)
        log.info('Applied httpx request sanitizer')
except Exception:
    # httpx not installed or wrapping failed; continue silently
    pass

# As a final defense, attempt to wrap a Groq client's low-level client/http_client
try:
    import agno.models.groq as _gm
    # Try to wrap attributes on the Groq class that may hold the low-level client
    for attr_name in ('client', 'http_client'):
        client_attr = getattr(_gm.Groq, attr_name, None)
        if client_attr is None:
            client_attr = getattr(_gm, attr_name, None)
        if client_attr is None:
            continue
        # if an instance-level client exists, we can't replace the class attr reliably here,
        # but wrapping the common httpx/requests clients above will cover most cases.
        try:
            orig_req = getattr(client_attr, 'request', None)
            if orig_req and not getattr(orig_req, '_grai_wrapped', False):
                def _client_req_wrapper(self, method, url, *args, **kwargs):
                    try:
                        payload = kwargs.get('json')
                        if payload is None:
                            data = kwargs.get('data') or kwargs.get('content')
                            try:
                                import json as _json
                                if isinstance(data, (bytes, str)):
                                    payload = _json.loads(data)
                            except Exception:
                                payload = None

                        def _sanitize_recursive(obj):
                            try:
                                if isinstance(obj, dict):
                                    if 'messages' in obj and isinstance(obj['messages'], list):
                                        for msg in obj['messages']:
                                            if isinstance(msg, dict) and msg.get('role') == 'tool':
                                                if ('content' not in msg) or (msg.get('content') is None):
                                                    args_obj = msg.get('arguments') or msg.get('args') or msg.get('tool_call_result') or None
                                                    try:
                                                        import json as _json2
                                                        msg['content'] = _json2.dumps(args_obj) if args_obj is not None else ''
                                                    except Exception:
                                                        msg['content'] = str(args_obj) if args_obj is not None else ''
                                    for v in obj.values():
                                        _sanitize_recursive(v)
                                elif isinstance(obj, list):
                                    for item in obj:
                                        _sanitize_recursive(item)
                            except Exception:
                                return

                        if isinstance(payload, (dict, list)):
                            _sanitize_recursive(payload)
                            kwargs['json'] = payload
                    except Exception:
                        pass
                    return orig_req(self, method, url, *args, **kwargs)

                _client_req_wrapper._grai_wrapped = True
                try:
                    setattr(client_attr, 'request', _client_req_wrapper)
                    log.info(f'Wrapped Groq client attr {attr_name} request')
                except Exception:
                    pass
        except Exception:
            pass
except Exception:
    pass


# Guaranteed final-layer monkeypatch for Groq SDK APIClient.request
try:
    import groq
    import inspect
    import json as _json

    _orig_api_request = getattr(groq._client.APIClient, 'request', None)

    if _orig_api_request is not None and not getattr(_orig_api_request, '_grai_wrapped', False):
        if inspect.iscoroutinefunction(_orig_api_request):
            async def _patched_api_request(self, method, url, **kwargs):
                try:
                    # log before sanitization for debugging
                    try:
                        with open(os.path.join(os.path.dirname(__file__), 'groq_requests.log'), 'a', encoding='utf-8') as f:
                            f.write(datetime.now().isoformat() + ' FINAL OUTBOUND BEFORE SANITIZE:\n')
                            f.write(_json.dumps(kwargs, default=str, indent=2) + '\n')
                    except Exception:
                        pass


                    # sanitize kwargs in-place
                    _sanitize_payload_in_kwargs(kwargs)

                    # Some SDK code clones request_options before sending; ensure any clones
                    # would also be sanitized by applying sanitization to a shallow copy
                    try:
                        clone = kwargs.copy()
                        _sanitize_payload_in_kwargs(clone)
                        kwargs.update(clone)
                    except Exception:
                        pass

                    # log after sanitize
                    try:
                        with open(os.path.join(os.path.dirname(__file__), 'groq_requests.log'), 'a', encoding='utf-8') as f:
                            f.write(datetime.now().isoformat() + ' FINAL OUTBOUND AFTER SANITIZE:\n')
                            f.write(_json.dumps(kwargs, default=str, indent=2) + '\n')
                    except Exception:
                        pass
                except Exception:
                    pass
                return await _orig_api_request(self, method, url, **kwargs)

            _patched_api_request._grai_wrapped = True
            setattr(groq._client.APIClient, 'request', _patched_api_request)
            log.info('Patched groq._client.APIClient.request (async) with final sanitizer')
        else:
            def _patched_api_request(self, method, url, **kwargs):
                try:
                    # log before sanitization for debugging
                    try:
                        with open(os.path.join(os.path.dirname(__file__), 'groq_requests.log'), 'a', encoding='utf-8') as f:
                            f.write(datetime.now().isoformat() + ' FINAL OUTBOUND BEFORE SANITIZE:\n')
                            f.write(_json.dumps(kwargs, default=str, indent=2) + '\n')
                    except Exception:
                        pass

                    # sanitize kwargs in-place
                    _sanitize_payload_in_kwargs(kwargs)

                    # Also sanitize and merge a shallow clone to defend against SDK copies
                    try:
                        clone = kwargs.copy()
                        _sanitize_payload_in_kwargs(clone)
                        kwargs.update(clone)
                    except Exception:
                        pass

                    # log after sanitize
                    try:
                        with open(os.path.join(os.path.dirname(__file__), 'groq_requests.log'), 'a', encoding='utf-8') as f:
                            f.write(datetime.now().isoformat() + ' FINAL OUTBOUND AFTER SANITIZE:\n')
                            f.write(_json.dumps(kwargs, default=str, indent=2) + '\n')
                    except Exception:
                        pass
                except Exception:
                    pass
                return _orig_api_request(self, method, url, **kwargs)

            _patched_api_request._grai_wrapped = True
            setattr(groq._client.APIClient, 'request', _patched_api_request)
            log.info('Patched groq._client.APIClient.request (sync) with final sanitizer')
except Exception as _e:
    try:
        log.warning(f'Could not patch groq APIClient.request: {_e}')
    except Exception:
        pass


# Final monkeypatch: wrap Groq SDK internal request entrypoints so we sanitize
# the exact kwargs the SDK will send to the network (httpcore or custom clients).
def _sanitize_payload_in_kwargs(kwargs: dict):
    """Mutate kwargs in-place: sanitize any nested 'messages' lists found in
    `json`, `data`, or `content` entries. Handles bytes/str content decoding.
    """
    try:
        def _sanitize_recursive(obj):
            try:
                if isinstance(obj, dict):
                    if 'messages' in obj and isinstance(obj['messages'], list):
                        for msg in obj['messages']:
                            if isinstance(msg, dict) and msg.get('role') == 'tool':
                                if ('content' not in msg) or (msg.get('content') is None):
                                    args_obj = msg.get('arguments') or msg.get('args') or msg.get('tool_call_result') or None
                                    try:
                                        import json as _json2
                                        msg['content'] = _json2.dumps(args_obj) if args_obj is not None else ''
                                    except Exception:
                                        msg['content'] = str(args_obj) if args_obj is not None else ''
                    for v in list(obj.values()):
                        _sanitize_recursive(v)
                elif isinstance(obj, list):
                    for item in obj:
                        _sanitize_recursive(item)
            except Exception:
                return

        # sanitize json if present
        if 'json' in kwargs and isinstance(kwargs['json'], (dict, list)):
            _sanitize_recursive(kwargs['json'])

        # sanitize top-level messages when provided directly
        if 'messages' in kwargs and isinstance(kwargs['messages'], list):
            _sanitize_recursive({'messages': kwargs['messages']})

        # sanitize request_params if present (some SDK versions nest payloads here)
        if 'request_params' in kwargs and isinstance(kwargs['request_params'], dict):
            # request_params may itself contain json/data/content/messages
            # sanitize nested dict in-place
            _sanitize_recursive(kwargs['request_params'])

        # sanitize body/data/content if bytes/str by attempting JSON decode
        for key in ('body', 'content', 'data'):
            if key in kwargs and isinstance(kwargs[key], (bytes, str)):
                try:
                    import json as _json
                    raw = kwargs[key]
                    if isinstance(raw, (bytes, bytearray)):
                        raw_decoded = raw.decode('utf-8')
                    else:
                        raw_decoded = raw
                    parsed = _json.loads(raw_decoded)
                    _sanitize_recursive(parsed)
                    new_payload = _json.dumps(parsed)
                    if isinstance(raw, (bytes, bytearray)):
                        kwargs[key] = new_payload.encode('utf-8')
                    else:
                        kwargs[key] = new_payload
                except Exception:
                    # not JSON or decode failed; skip
                    pass

        # sanitize data/content/body if they are dict/list directly
        for key in ('data', 'content', 'body'):
            if key in kwargs and isinstance(kwargs[key], (dict, list)):
                _sanitize_recursive(kwargs[key])
    except Exception:
        return


def _wrap_target_callable(target, attr_name):
    """Wrap target.attr_name with a sanitizer that mutates kwargs in-place.
    Supports sync and async callables.
    Returns True if wrapped, False otherwise.
    """
    try:
        orig = getattr(target, attr_name, None)
        if orig is None:
            return False

        # avoid double-wrap
        if getattr(orig, '_grai_sanitizer_wrapped', False):
            return True

        import inspect

        if inspect.iscoroutinefunction(orig):
            async def _wrapped(*args, **kwargs):
                try:
                    _sanitize_payload_in_kwargs(kwargs)
                except Exception:
                    pass
                return await orig(*args, **kwargs)

            _wrapped._grai_sanitizer_wrapped = True
            setattr(target, attr_name, _wrapped)
            return True
        else:
            def _wrapped(*args, **kwargs):
                try:
                    _sanitize_payload_in_kwargs(kwargs)
                except Exception:
                    pass
                return orig(*args, **kwargs)

            _wrapped._grai_sanitizer_wrapped = True
            setattr(target, attr_name, _wrapped)
            return True
    except Exception:
        return False


try:
    # Candidate targets inside Groq SDK to wrap. Try multiple possible locations
    # depending on SDK version.
    import importlib

    candidates = [
        ('groq._client', 'APIClient', 'request'),
        ('groq._client', 'APIClient', '_request'),
        ('groq._client', 'Client', '_request'),
        ('groq.resources.chat.completions', 'Completions', 'create'),
    ]

    for mod_path, cls_name, method_name in candidates:
        try:
            mod = importlib.import_module(mod_path)
            cls = getattr(mod, cls_name, None)
            if cls is None:
                continue
            wrapped = _wrap_target_callable(cls, method_name)
            if wrapped:
                log.info(f'Wrapped Groq SDK target: {mod_path}.{cls_name}.{method_name}')
        except Exception:
            continue
except Exception:
    pass


# Wrap streaming consumers if present so chunked/stream sub-requests are sanitized
try:
    import importlib
    mod = importlib.import_module('groq._client')
    APIClient = getattr(mod, 'APIClient', None)
    if APIClient is not None:
        # common internal stream consumer names
        for stream_name in ('_consume_sync_stream', '_consume_async_stream'):
            orig = getattr(APIClient, stream_name, None)
            if orig and not getattr(orig, '_grai_wrapped', False):
                import inspect
                if inspect.iscoroutinefunction(orig):
                    async def _wrapped_consumer(self, *args, **kwargs):
                        try:
                            # sanitize any request_options or kwargs passed in
                            if args and isinstance(args[0], dict):
                                _sanitize_payload_in_kwargs(args[0])
                            if isinstance(kwargs, dict):
                                _sanitize_payload_in_kwargs(kwargs)
                            # Also sanitize shallow clones if SDK copies them
                            try:
                                if isinstance(kwargs, dict) and hasattr(kwargs, 'copy'):
                                    c = kwargs.copy()
                                    _sanitize_payload_in_kwargs(c)
                                    kwargs.update(c)
                            except Exception:
                                pass
                        except Exception:
                            pass
                        return await orig(self, *args, **kwargs)
                    _wrapped_consumer._grai_wrapped = True
                    setattr(APIClient, stream_name, _wrapped_consumer)
                else:
                    def _wrapped_consumer(self, *args, **kwargs):
                        try:
                            if args and isinstance(args[0], dict):
                                _sanitize_payload_in_kwargs(args[0])
                            if isinstance(kwargs, dict):
                                _sanitize_payload_in_kwargs(kwargs)
                            try:
                                if isinstance(kwargs, dict) and hasattr(kwargs, 'copy'):
                                    c = kwargs.copy()
                                    _sanitize_payload_in_kwargs(c)
                                    kwargs.update(c)
                            except Exception:
                                pass
                        except Exception:
                            pass
                        return orig(self, *args, **kwargs)
                    _wrapped_consumer._grai_wrapped = True
                    setattr(APIClient, stream_name, _wrapped_consumer)
        log.info('Wrapped Groq APIClient stream consumers for sanitizer')
except Exception:
    pass


class ResearchOrchestrator:
    """
    Orchestrates the multi-agent research workflow using Phidata/Agno.
    """
    
    def __init__(self, status_callback: Callable = None):
        """
        Initialize the orchestrator.
        
        Args:
            status_callback: Function to call with status updates
        """
        self.status_callback = status_callback
        
        # Create output directories
        Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        Path(f"{OUTPUT_DIR}/charts").mkdir(parents=True, exist_ok=True)
        
        # Initialize agents
        log.info("Initializing multi-agent system...")
        self.team_agent = create_team_agent()
        
        # State tracking
        self.current_topic = None
        self.research_plan = None
        self.final_report = None
        self.task_status = []
        
        log.info("Research Orchestrator initialized")
    
    def _update_status(self, phase: str, message: str, details: Dict[str, Any] = None):
        """
        Update status and notify callback.
        
        Args:
            phase: Current phase name
            message: Status message
            details: Additional details
        """
        status = {
            "timestamp": datetime.now(),
            "phase": phase,
            "message": message,
            "details": details or {}
        }
        
        log.info(f"[{phase}] {message}")
        
        if self.status_callback:
            self.status_callback(status)
    
    def run_research(self, topic: str, stream: bool = False) -> Dict[str, Any]:
        """
        Execute the complete research workflow.
        
        Args:
            topic: Research topic
            
        Returns:
            Dictionary with research results
        """
        self.current_topic = topic
        log.info(f"Starting research on: {topic}")
        
        def _on_task_update(task_obj):
            # Called by WorkerAgent.execute_plan after each task completes.
            try:
                self._update_status('TASK_PROGRESS', f"Completed task {task_obj.id}: {task_obj.name}")
                # If there's a partial report available, save it so UI can show progress
                try:
                    if hasattr(self, 'worker_instance') and getattr(self.worker_instance, 'report', None):
                        rpt = self.worker_instance.report
                        # Save incremental markdown and HTML preview
                        gen = self.worker_instance.generator
                        try:
                            gen.save_markdown(rpt)
                            gen.save_html(rpt)
                        except Exception:
                            pass
                except Exception:
                    pass
            except Exception:
                pass

        try:
            # Phase 1: Planning
            self._update_status(
                "PLANNING",
                "Analyzing topic and creating research plan...",
                {"topic": topic}
            )
            
            plan_prompt = f"""
Create a detailed research plan for the following topic:

TOPIC: {topic}

Break it down into 6 specific tasks with clear objectives for each task.
"""
            
            # Get planner agent separately for planning phase
            planner = create_planner_agent()
            try:
                plan_response = planner.run(plan_prompt)
                self.research_plan = plan_response.content
            except Exception as e:
                # If the planner call fails, log and re-raise so the workflow
                # does not continue with a fallback plan. The outer exception
                # handler will convert this into an error result.
                log.error(f"Planner LLM call failed: {e}")
                raise
            
            self._update_status(
                "PLAN_CREATED",
                "Research plan created successfully",
                {"plan": self.research_plan}
            )
            
            # Phase 2: Execution
            self._update_status(
                "EXECUTION_START",
                "Worker Agent beginning task execution...",
                {}
            )
            
            execution_prompt = f"""
Execute a comprehensive research project on this topic:

TOPIC: {topic}

RESEARCH PLAN:
{self.research_plan}

Execute each task in sequence:
1. Search for 3 trustworthy sources using the search_web tool
2. Extract content from each source using extract_webpage_content tool
3. Analyze the collected content (statistics and sentiment)
4. Draft a comprehensive research report with all sections
5. Review and improve the draft
6. Format the final report in Markdown with citations and analysis

Provide detailed updates as you complete each task.
"""
            
            # Execution: either run Agno worker agent (batch) or local WorkerAgent (streaming)
            if stream:
                # Use local WorkerAgent to run tasks sequentially and emit partial reports
                self.worker_instance = WorkerAgent()
                # Build a simple ResearchPlan object with six tasks if the planner returned text
                rp = ResearchPlan(topic=topic)
                rp.tasks = [
                    Task(id=1, name='Source Identification', description='Find sources'),
                    Task(id=2, name='Content Collection', description='Extract content'),
                    Task(id=3, name='Data Analysis', description='Analyze content'),
                    Task(id=4, name='Report Drafting', description='Draft report'),
                    Task(id=5, name='Self-Review', description='Review and improve'),
                    Task(id=6, name='Final Production', description='Produce outputs')
                ]
                try:
                    self.worker_instance.execute_plan(rp, task_callback=_on_task_update)
                    # After run, the worker_instance.report should be available
                    self.final_report = self.worker_instance.report.markdown_content if getattr(self.worker_instance, 'report', None) else ''
                except Exception as e:
                    log.error(f"Local Worker execution failed: {e}")
                    raise
            else:
                # Get worker agent for execution (batch)
                worker = create_worker_agent()
                try:
                    execution_response = worker.run(execution_prompt)
                    self.final_report = execution_response.content
                except Exception as e:
                    log.error(f"Worker LLM call failed: {e}")
                    raise
            
            self._update_status(
                "EXECUTION_COMPLETE",
                "All tasks completed successfully!",
                {}
            )
            
            # Save report
            report_path = self._save_report(self.final_report)
            
            self._update_status(
                "REPORT_SAVED",
                f"Report saved to {report_path}",
                {"path": report_path}
            )
            
            result = {
                "success": True,
                "topic": topic,
                "plan": self.research_plan,
                "report": self.final_report,
                "report_path": report_path,
                "timestamp": datetime.now()
            }
            
            log.info("Research workflow completed successfully")
            return result
            
        except Exception as e:
            log.error(f"Research workflow failed: {str(e)}")
            self._update_status(
                "ERROR",
                f"Research failed: {str(e)}",
                {"error": str(e)}
            )
            
            return {
                "success": False,
                "topic": topic,
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    def _save_report(self, report_content: str) -> str:
        """
        Save the research report to a file.
        
        Args:
            report_content: Markdown report content
            
        Returns:
            Path to saved file
        """
        # Save as PDF using the markdown->PDF helper if the content appears to be markdown
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        md_filename = f"{OUTPUT_DIR}/research_report_{timestamp}.md"
        pdf_filename = f"{OUTPUT_DIR}/research_report_{timestamp}.pdf"

        try:
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(report_content)

            # Try to generate a rich PDF from the markdown
            try:
                # First try normal import
                try:
                    from scripts.md_to_pdf import build_pdf
                except Exception:
                    # Fallback: load module by file path (works when scripts/ isn't a package)
                    import importlib.util
                    spec_path = os.path.join(project_root, 'scripts', 'md_to_pdf.py')
                    if os.path.exists(spec_path):
                        spec = importlib.util.spec_from_file_location('md_to_pdf', spec_path)
                        md_mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(md_mod)
                        build_pdf = getattr(md_mod, 'build_pdf')
                    else:
                        raise

                out_pdf = build_pdf(md_filename, out_pdf_path=pdf_filename)
                log.info(f"Report saved as PDF: {out_pdf}")
                return out_pdf
            except Exception as e:
                # Log the full exception and fall back to the markdown file so
                # callers still get an artifact to inspect.
                log.exception(f"PDF generation failed; falling back to markdown file: {e}")
                return md_filename
        except Exception as e:
            log.error(f"Failed to save report: {e}")
            # As a last resort, write directly to a .txt file
            fallback = f"{OUTPUT_DIR}/research_report_{timestamp}.txt"
            try:
                with open(fallback, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                return fallback
            except Exception:
                return md_filename
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        return {
            "topic": self.current_topic,
            "has_plan": self.research_plan is not None,
            "has_report": self.final_report is not None
        }