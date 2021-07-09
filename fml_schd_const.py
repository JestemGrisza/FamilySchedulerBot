from enum import Enum

DAY_NAME_FULL = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
DAY_NAME_3CHAR = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
DAY_NAME_2CHAR = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']

# Reg ex time hh:mm
TIME_REGEXP_LONG = '^(2[0-3]|[01]?[0-9]):([0-5]?[0-9])$'
# Reg ex time hh
TIME_REGEXP_SHORT = '^(2[0-3]|[01]?[0-9])$'
# Reg ex that matches dates.
# Formats accepted dd/mm/yyyy or dd-mm-yyyy or dd.mm.yyyy format
DATE_REGEXP_LONG = '^[0-9]{2}[-/.][0-9]{2}[-/.][0-9]{4}$'
DATE_REGEXP_SHORT = '^[0-9]{2}[-/.][0-9]{2}$'
#
DEFAULT_TASK_DURATION = 60

# State for task: Active, Notified, InProgress, Delayed, Canceled, Done
# Don't used yet


class State(Enum):
    active = 1
    notified = 2
    in_progress = 3
    delayed = 4
    canceled = 5
    done = 6
