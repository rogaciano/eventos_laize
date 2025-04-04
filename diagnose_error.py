import sys
import traceback

try:
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'check'])
except Exception as e:
    print("FULL ERROR MESSAGE:")
    traceback.print_exc()
    print("\n\nERROR TYPE:", type(e))
    print("ERROR MESSAGE:", str(e))
