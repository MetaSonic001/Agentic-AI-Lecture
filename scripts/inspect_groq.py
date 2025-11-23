import inspect
import agno.models.groq as gm
print('Groq methods (public):')
print([m for m in dir(gm.Groq) if not m.startswith('_')])
print('\nSignature of invoke:')
print(inspect.signature(gm.Groq.invoke))
print('\nSignature of response:')
print(inspect.signature(gm.Groq.response))
print('\nDoc for invoke:\n', gm.Groq.invoke.__doc__)
print('\nDoc for response:\n', gm.Groq.response.__doc__)
