import traceback
import sys

try:
    exec(open('main.py', encoding='utf-8').read())
except Exception as e:
    print('Error:', e)
    print('Traceback:')
    traceback.print_exc()
    sys.exit(1)