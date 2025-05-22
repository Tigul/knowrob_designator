# Logs that a new designator was resolved from another.
# - `designator_id`: Unique ID of resolved designator
# - `resolved_from_id`: ID of the designator it was resolved from
# - `json_designator`: Full JSON structure of the resolved designator
# - `timestamp`: Time of resolution
string designator_id
string resolved_from_id
string json_designator
builtin_interfaces/Time stamp