## KnowRob Designator Action Interfaces

These interfaces enable robots to semantically log and track the lifecycle of CRAM *designators* during task execution. Each stage of a designator's usage is logged via a separate ROS action.

---

### 1. `/knowrob/designator/init`

**Action Type:** `DesignatorInitAction`
**Purpose:** Registers a new (typically symbolic) designator with KnowRob.

#### When to Use

Call this when a designator is first created. It represents an abstract intention, such as “bring the milk to the table,” and may contain nested symbolic sub-designators.

#### Goal Fields

* `designator_id`: Unique identifier for this designator.
* `parent_id`: Optional ID of a parent designator (use `""` for root).
* `json_designator`: The symbolic JSON designator.
* `stamp`: Time the designator was created.

#### Example

```python
goal = DesignatorInitGoal()
goal.designator_id = "desig_123"
goal.parent_id = ""
goal.json_designator = '{"anAction": {"type": "Transporting", "objectActedOn": {"anObject": {"type": "Milk"}}, "target": {"theLocation": {"goal": {"theObject": {"name": "Table1"}}}}}}'
goal.stamp = rospy.Time.now()
```

---

### 2. `/knowrob/designator/resolving_started`

**Action Type:** `DesignatorResolutionStartAction`
**Purpose:** Signals that resolution (e.g., grounding of symbolic references) has started.

#### When to Use

Call this before resolving the symbolic designator into a grounded one (e.g., a pose in space).

#### Goal Fields

* `designator_id`: ID of the designator being resolved.
* `json_designator`: The original symbolic JSON.
* `stamp`: Time resolution started.

#### Example

```python
goal = DesignatorResolutionStartGoal()
goal.designator_id = "desig_123"
goal.json_designator = same_json_as_init
goal.stamp = rospy.Time.now()
```

---

### 3. `/knowrob/designator/resolving_finished`

**Action Type:** `DesignatorResolutionFinishedAction`
**Purpose:** Logs the grounded (resolved) version of a symbolic designator.

#### When to Use

After successful resolution of a symbolic designator, use this to log its grounded form.

#### Goal Fields

* `designator_id`: ID of the new, resolved designator.
* `resolved_from_id`: ID of the original symbolic designator.
* `json_designator`: The resolved JSON designator (e.g., with pose data).
* `stamp`: Time resolution completed.

#### Example

```python
goal = DesignatorResolutionFinishedGoal()
goal.designator_id = "desig_456"
goal.resolved_from_id = "desig_123"
goal.json_designator = '{"anAction": {"type": "Transporting", "objectActedOn": {"anObject": {"type": "Milk"}}, "target": {"pose": {"x": 1.2, "y": 0.8, "z": 0.75, "frame": "map"}}}}'
goal.stamp = rospy.Time.now()
```

---

### 4. `/knowrob/designator/execution_start`

**Action Type:** `DesignatorExecutionStartAction`
**Purpose:** Signals that the execution of a resolved designator has started.

#### When to Use

Once the robot begins acting on the resolved designator (e.g., starts moving to pick up an object), log the execution start.

#### Goal Fields

* `designator_id`: ID of the resolved designator being executed.
* `json_designator`: The grounded designator (e.g., with numeric poses).
* `stamp`: Time execution began.

#### Example

```python
goal = DesignatorExecutionStartGoal()
goal.designator_id = "desig_456"
goal.json_designator = "" # Allowed to be empty, if not different from the last logged version
goal.stamp = rospy.Time.now()
```

---

### 5. `/knowrob/designator/execution_finished`

**Action Type:** `DesignatorExecutionFinishedAction`
**Purpose:** Logs that the execution of the designator has been completed.

#### When to Use

After the task related to the designator is complete (e.g., object placed on table), log this event.

#### Goal Fields

* `designator_id`: ID of the resolved designator that was executed.
* `json_designator`: Same designator content as before (for traceability).
* `stamp`: Time execution finished.

#### Example

```python
goal = DesignatorExecutionFinishedGoal()
goal.designator_id = "desig_456"
goal.json_designator = ""
goal.stamp = rospy.Time.now()
``` 
---

### 6. `/knowrob/designator/push_object_designator`

**Action Type:** `PushObjectDesignatorAction`
**Purpose:** Adds or updates an object designator in the KnowRob knowledge base.

#### When to Use

Use this action to assert the presence or update the semantic state of a physical object in the environment. This can be done after object detection, tracking, or perception to inform KnowRob about the current scene.

#### Goal Fields

* `json_designator`: JSON description of the object (type, pose, name, etc.).
* `stamp`: Timestamp when the object was perceived.

#### Result Fields

* `success`: Whether the object was successfully added.
* `message`: Informational message for logging or debugging.

#### Feedback Fields

* `status`: Optional feedback status.

#### Example

```python
push_client = actionlib.SimpleActionClient('/knowrob/designator/push_object_designator', PushObjectDesignatorAction)

push_goal = PushObjectDesignatorGoal()
push_goal.json_designator = """
{
  "anObject": {
    "type": "Milk",
    "pose": {
      "x": 1.0, 
      "y": 0.5,
      "z": 0.75,
      "frame": "map"
    }
  }
}
"""
push_goal.stamp = rospy.Time.now()

send_action(push_client, push_goal, "PushObjectDesignator")
```

> Note: This action can be called repeatedly to update object poses or semantic types during runtime. It is typically decoupled from task-level designator flows.
