#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Full client for all KnowRob designator actions

import rospy
import actionlib
import uuid
from time import sleep
from knowrob_designator.msg import (
    PushObjectDesignatorAction, PushObjectDesignatorGoal,
    DesignatorInitAction, DesignatorInitGoal,
    DesignatorResolutionStartAction, DesignatorResolutionStartGoal,
    DesignatorResolutionFinishedAction, DesignatorResolutionFinishedGoal,
    DesignatorExecutionStartAction, DesignatorExecutionStartGoal,
    DesignatorExecutionFinishedAction, DesignatorExecutionFinishedGoal
)
from knowrob_ros.knowrob_ros_lib import KnowRobRosLib
from knowrob_ros.knowrob_ros_lib import get_default_modalframe

def send_action(client, goal, label):
    rospy.loginfo(f"[{label}] Waiting for action server...")
    client.wait_for_server()
    rospy.loginfo(f"[{label}] Sending goal...")
    client.send_goal(goal)
    client.wait_for_result()
    result = client.get_result()
    rospy.loginfo(f"[{label}] Result: success={result.success}, message='{result.message}''")

def testQueryDesig():
    know = KnowRobRosLib()
    know.init_clients()  # After rospy.init_node()
    
    query = "triple(?d, rdf:type, soma:PyCramDesignator)"
    rospy.loginfo(f"asking [{query}] ...")
    result = know.ask_one(query, get_default_modalframe())
    rospy.loginfo(f"response: [{result}]")

def main():
    rospy.init_node('knowrob_designator_full_test_client')
    
    ##########################################################
    ############### Object Designators ########################
        
    # 0. PushObjectDesignator
    push_client = actionlib.SimpleActionClient('/knowrob/designator/push_object_designator', PushObjectDesignatorAction)
    push_goal = PushObjectDesignatorGoal()
    push_goal.json_designator = """
    {
      "anObject": {
        "type": "Milk"
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
    
    ##########################################################
    ############### Action Designators ########################
    
    # Create a designator ID and JSON designator
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
    
    # Finally do some testing queries with KnowRob
    testQueryDesig()

if __name__ == '__main__':
    main()
