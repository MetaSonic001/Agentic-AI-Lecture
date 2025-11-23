import py_compile
files = [
    'Education/orchestrator.py',
    'Education/planner_agent.py'
]
failed = False
for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print(f'OK: {f}')
    except py_compile.PyCompileError as e:
        print(f'ERROR: {f}\n{e}')
        failed = True
if failed:
    raise SystemExit(2)
print('All syntax checks passed')
