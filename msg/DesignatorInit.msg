# Logs a root or nested designator being created.
# - `designator_id`: Unique ID of this designator
# - `parent_id`: ID of parent designator (or empty for root)
# - `json_designator`: Full JSON structure of the designator
# - `timestamp`: Time of logging
string designator_id
string parent_id
string json_designator
builtin_interfaces/Time stamp