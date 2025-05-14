#!/usr/bin/env python3

import rospy
import json
from std_msgs.msg import String

# Import all designator message types
from knowrob_designator.msg import (
    PushObjectDesignator,
    DesignatorInit,
    DesignatorResolutionStart,
    DesignatorResolutionFinished,
    DesignatorExecutionStart,
    DesignatorExecutionFinished
)

from knowrob_ros.knowrob_ros_lib import KnowRobRosLib, TripleQueryBuilder, get_default_modalframe
from knowrob_designator.designator_parser import DesignatorParser

class DesignatorLoggerNode:
    def __init__(self):
        rospy.init_node('designator_logger_node')

        # Initialize subscribers for each message type
        rospy.Subscriber('/knowrob/designator/push_object_designator', PushObjectDesignator, self.handle_push_object_designator)
        rospy.Subscriber('/knowrob/designator/init', DesignatorInit, self.handle_init)
        rospy.Subscriber('/knowrob/designator/resolving_started', DesignatorResolutionStart, self.handle_resolve_start)
        rospy.Subscriber('/knowrob/designator/resolving_finished', DesignatorResolutionFinished, self.handle_resolve_finished)
        rospy.Subscriber('/knowrob/designator/execution_start', DesignatorExecutionStart, self.handle_exec_start)
        rospy.Subscriber('/knowrob/designator/execution_finished', DesignatorExecutionFinished, self.handle_exec_finished)

        # Initialize the KnowRob client
        self.knowrob = KnowRobRosLib()
        self.knowrob.init_clients()        
        
        # Parser for designators
        self.parser = DesignatorParser()     

        rospy.loginfo("DesignatorLoggerNode: all subscribers initialized.")

    def handle_push_object_designator(self, msg):
        rospy.loginfo("Push Object Designator")
        rospy.logdebug(f"Full JSON:\n{msg.json_designator}")

    def handle_init(self, msg):
        rospy.loginfo(f"Init Designator: {msg.designator_id}")
        rospy.logdebug(f"Full JSON:\n{msg.json_designator}")

    def handle_resolve_start(self, msg):
        try:
            rospy.loginfo(f"[ResolveStart] Processing Designator: {msg.designator_id}")
            designator = json.loads(msg.json_designator)
            rospy.logdebug(f"Parsed JSON Designator: {designator}")

            triples = self.parser.parse(designator)

            builder = TripleQueryBuilder()
            for s, p, o in triples:
                builder.add(s, p, o)

            # Optionally tell KnowRob (simulated here)
            # tell_result = self.knowrob.tell(builder.get_triples(), get_default_modalframe())

            rospy.loginfo(f"Sent {len(triples)} triples to KnowRob.")

        except Exception as e:
            rospy.logerr(f"[ResolveStart] Error: {str(e)}")

    def handle_resolve_finished(self, msg):
        rospy.loginfo(f"Finished Resolving Designator: {msg.designator_id} from {msg.resolved_from_id}")

    def handle_exec_start(self, msg):
        rospy.loginfo(f"Execution Started: {msg.designator_id}")

    def handle_exec_finished(self, msg):
        rospy.loginfo(f"Execution Finished: {msg.designator_id}")

if __name__ == '__main__':
    try:
        DesignatorLoggerNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
