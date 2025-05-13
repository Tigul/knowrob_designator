#!/usr/bin/env python3

import rospy
import actionlib
import json
from std_msgs.msg import String

# Import all designator action types
from knowrob_designator.msg import (
    PushObjectDesignatorAction, PushObjectDesignatorResult, PushObjectDesignatorFeedback,
    DesignatorInitAction, DesignatorInitResult, DesignatorInitFeedback,
    DesignatorResolutionStartAction, DesignatorResolutionStartResult, DesignatorResolutionStartFeedback,
    DesignatorResolutionFinishedAction, DesignatorResolutionFinishedResult, DesignatorResolutionFinishedFeedback,
    DesignatorExecutionStartAction, DesignatorExecutionStartResult, DesignatorExecutionStartFeedback,
    DesignatorExecutionFinishedAction, DesignatorExecutionFinishedResult, DesignatorExecutionFinishedFeedback
)

from knowrob_ros.knowrob_ros_lib import KnowRobRosLib, TripleQueryBuilder, get_default_modalframe
from knowrob_designator.designator_parser import DesignatorParser

class DesignatorLoggerServer:
    def __init__(self):
        rospy.init_node('designator_logger_server')

        # Start an action server for each action type
        self.push_object_server = actionlib.SimpleActionServer(
            '/knowrob/designator/push_object_designator',
            PushObjectDesignatorAction,
            execute_cb=self.handle_push_object_designator,
            auto_start=False
        )
        self.init_server = actionlib.SimpleActionServer(
            '/knowrob/designator/init',
            DesignatorInitAction,
            execute_cb=self.handle_init,
            auto_start=False
        )
        self.resolve_start_server = actionlib.SimpleActionServer(
            '/knowrob/designator/resolving_started',
            DesignatorResolutionStartAction,
            execute_cb=self.handle_resolve_start,
            auto_start=False
        )
        self.resolve_finished_server = actionlib.SimpleActionServer(
            'knowrob/designator/resolving_finished',
            DesignatorResolutionFinishedAction,
            execute_cb=self.handle_resolve_finished,
            auto_start=False
        )
        self.exec_start_server = actionlib.SimpleActionServer(
            '/knowrob/designator/execution_start',
            DesignatorExecutionStartAction,
            execute_cb=self.handle_exec_start,
            auto_start=False
        )
        self.exec_finished_server = actionlib.SimpleActionServer(
            '/knowrob/designator/execution_finished',
            DesignatorExecutionFinishedAction,
            execute_cb=self.handle_exec_finished,
            auto_start=False
        )
        
        # Initialize the KnowRob client
        self.knowrob = KnowRobRosLib()
        self.knowrob.init_clients()        
        
        # Parser for designators
        self.parser = DesignatorParser()     

        # Start all servers
        self.push_object_server.start()
        self.init_server.start()
        self.resolve_start_server.start()
        self.resolve_finished_server.start()
        self.exec_start_server.start()
        self.exec_finished_server.start()

        rospy.loginfo("DesignatorLoggerServer: all servers started.")
        
    def handle_push_object_designator(self, goal):
        rospy.loginfo(f"Push Object Designator")
        rospy.logdebug(f"Full JSON:\n{goal.json_designator}")
        result = PushObjectDesignatorResult(success=True, message="Designator pushed.")
        self.push_object_server.set_succeeded(result)

    def handle_init(self, goal):
        rospy.loginfo(f"Init Designator: {goal.designator_id}")
        rospy.logdebug(f"Full JSON:\n{goal.json_designator}")
        result = DesignatorInitResult(success=True, message="Designator init logged.")
        self.init_server.set_succeeded(result)

    def handle_resolve_start(self, goal):
        feedback = DesignatorResolutionStartFeedback()
        result = DesignatorResolutionStartResult()

        try:
            rospy.loginfo(f"[ResolveStart] Processing Designator: {goal.designator_id}")
            
            # Parse incoming JSON string to dictionary
            designator = json.loads(goal.json_designator)
            rospy.logdebug(f"Parsed JSON Designator: {designator}")

            # Convert to RDF-style triples
            triples = self.parser.parse(designator)

            # Package into ROS Triple messages
            builder = TripleQueryBuilder()
            for s, p, o in triples:
                builder.add(s, p, o)

            feedback.status = f"Sending {len(triples)} triples to KnowRob..."
            self.resolve_start_server.publish_feedback(feedback)

            # Send triples to KnowRob via tell action
            # Note: Commented out for now
            # tell_result = self.knowrob.tell(builder.get_triples(), get_default_modalframe())

            # result.success = (tell_result.status == 1)
            # result.message = "Success" if result.success else "Failed to log to KnowRob"

            result.success = True  # Simulate success for now
            result.message = "done"

        except Exception as e:
            rospy.logerr(f"[ResolveStart] Error: {str(e)}")
            result.success = False
            result.message = str(e)
            result.status = "exception"

        self.resolve_start_server.set_succeeded(result)
    
    def handle_resolve_finished(self, goal):
        rospy.loginfo(f"Finished Resolving Designator: {goal.designator_id} from {goal.resolved_from_id}")
        result = DesignatorResolutionFinishedResult(success=True, message="Resolution finished logged.")
        self.resolve_finished_server.set_succeeded(result)

    def handle_exec_start(self, goal):
        rospy.loginfo(f"Execution Started: {goal.designator_id}")
        result = DesignatorExecutionStartResult(success=True, message="Execution started logged.")
        self.exec_start_server.set_succeeded(result)

    def handle_exec_finished(self, goal):
        rospy.loginfo(f"Execution Finished: {goal.designator_id}")
        result = DesignatorExecutionFinishedResult(success=True, message="Execution finished logged.")
        self.exec_finished_server.set_succeeded(result)

if __name__ == '__main__':
    try:
        DesignatorLoggerServer()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
