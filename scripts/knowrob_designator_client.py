#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Full client for all KnowRob designator actions

import rospy
import actionlib
import uuid
from time import sleep
from knowrob_designator.msg import (
    DesignatorInitAction, DesignatorInitGoal,
    DesignatorResolutionStartAction, DesignatorResolutionStartGoal,
    DesignatorResolutionFinishedAction, DesignatorResolutionFinishedGoal,
    DesignatorExecutionStartAction, DesignatorExecutionStartGoal,
    DesignatorExecutionFinishedAction, DesignatorExecutionFinishedGoal
)

def send_action(client, goal, label):
    rospy.loginfo(f"[{label}] Waiting for action server...")
    client.wait_for_server()
    rospy.loginfo(f"[{label}] Sending goal...")
    client.send_goal(goal)
    client.wait_for_result()
    result = client.get_result()
    rospy.loginfo(f"[{label}] Result: success={result.success}, message='{result.message}''")

def main():
    rospy.init_node('knowrob_designator_full_test_client')

    json_designator = """
    {
      "anAction": {
        "type": "Transporting",
        "objectActedOn": {
          "anObject": {
            "type": "Milk"
          }
        },
        "target": {
          "theLocation": {
            "goal": {
              "theObject": {
                "name": "Table1"
              }
            }
          }
        }
      }
    }
    """

    designator_id = f"desig_{uuid.uuid4()}"
    resolved_id = f"desig_{uuid.uuid4()}"
    now = rospy.Time.now()

    # 1. DesignatorInit
    init_client = actionlib.SimpleActionClient('/knowrob/designator/init', DesignatorInitAction)
    init_goal = DesignatorInitGoal()
    init_goal.designator_id = designator_id
    init_goal.parent_id = ""  # root designator
    init_goal.json_designator = json_designator
    init_goal.stamp = now
    send_action(init_client, init_goal, "Init")

    # 2. DesignatorResolvingStarted
    resolving_client = actionlib.SimpleActionClient('/knowrob/designator/resolving_started', DesignatorResolutionStartAction)
    resolving_goal = DesignatorResolutionStartGoal()
    resolving_goal.designator_id = designator_id
    resolving_goal.json_designator = json_designator
    resolving_goal.stamp = now
    send_action(resolving_client, resolving_goal, "ResolveStart")

    # 3. DesignatorResolutionFinished with resolved target
    resolved_client = actionlib.SimpleActionClient('/knowrob/designator/resolving_finished', DesignatorResolutionFinishedAction)

    resolved_designator = """
    {
      "anAction": {
        "type": "Transporting",
        "objectActedOn": {
          "anObject": {
            "type": "Milk"
          }
        },
        "target": {
          "pose": {
            "x": 1.2,
            "y": 0.8,
            "z": 0.75,
            "frame": "map"
          }
        }
      }
    }
    """

    resolved_goal = DesignatorResolutionFinishedGoal()
    resolved_goal.designator_id = resolved_id
    resolved_goal.resolved_from_id = designator_id
    resolved_goal.json_designator = resolved_designator
    resolved_goal.stamp = rospy.Time.now()
    send_action(resolved_client, resolved_goal, "ResolveFinished")


    # 4. DesignatorExecutionStart
    exec_start_client = actionlib.SimpleActionClient('/knowrob/designator/execution_start', DesignatorExecutionStartAction)
    exec_start_goal = DesignatorExecutionStartGoal()
    exec_start_goal.designator_id = resolved_id
    exec_start_goal.json_designator = resolved_designator
    exec_start_goal.stamp = now
    send_action(exec_start_client, exec_start_goal, "ExecutionStart")

    # 5. DesignatorExecutionFinished
    exec_finished_client = actionlib.SimpleActionClient('/knowrob/designator/execution_finished', DesignatorExecutionFinishedAction)
    exec_finished_goal = DesignatorExecutionFinishedGoal()
    exec_finished_goal.designator_id = resolved_id
    exec_finished_goal.json_designator = resolved_designator
    exec_finished_goal.stamp = now
    send_action(exec_finished_client, exec_finished_goal, "ExecutionFinished")

if __name__ == '__main__':
    main()
