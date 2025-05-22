#!/usr/bin/env python3

import rospy
import actionlib
import json
from knowrob_designator.msg import DesignatorQueryIncrementalAction, DesignatorQueryIncrementalGoal

def send_query(query_json, query_type="entityvar", query_id=""):
    # Create action client
    client = actionlib.SimpleActionClient('/knowrob/designator/query_incremental', DesignatorQueryIncrementalAction)

    rospy.loginfo("Waiting for action server...")
    client.wait_for_server()
    rospy.loginfo("Action server available.")

    # Create goal
    goal = DesignatorQueryIncrementalGoal()
    goal.query_type = query_type
    goal.query_id = query_id
    goal.designator_json = json.dumps(query_json)

    # Send goal
    rospy.loginfo(f"Sending query (query_id={query_id}):\n{goal.designator_json}")
    client.send_goal(goal)
    client.wait_for_result()

    # Get result
    result = client.get_result()
    return result


if __name__ == '__main__':
    rospy.init_node('designator_query_test')

    # -------------------------
    # Query 1: what to use for breakfast
    breakfast_query = {"anObject": {"type": "?x", "usedFor": "breakfast"}}

    result1 = send_query(breakfast_query)
    print("\n--- Breakfast query result 1 ---")
    print(f"Success: {result1.success}")
    print(f"Binding: {result1.binding_as_json}")
    print(f"Query ID: {result1.query_id}")

    result2 = send_query(query_json={}, query_id=str(result1.query_id))
    print("\n--- Breakfast query result 2 (incremental) ---")
    print(f"Success: {result2.success}")
    print(f"Binding: {result2.binding_as_json}")
    print(f"Query ID: {result2.query_id}")

    # -------------------------
    # Query 2: where is the Milk stored
    milk_location_query = {
        "anAction": {
            "type": "searching",
            "anObject": {"type": "Milk"},
            "aLocation": {
                "?x": {
                    "insideOf": {
                        "anObject": {"URDFLink": "?_"}
                    }
                }
            }
        }
    }

    result3 = send_query(milk_location_query)
    print("\n--- Milk location query result ---")
    print(f"Success: {result3.success}")
    print(f"Binding: {result3.binding_as_json}")
    print(f"Query ID: {result3.query_id}")
