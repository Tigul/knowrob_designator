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

print_triples = True

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
        rospy.loginfo("----------------------------------------------------------")
        rospy.loginfo("Push Object Designator")
        rospy.logdebug(f"Full JSON:\n{msg.json_designator}")

    def handle_init(self, msg):
        rospy.loginfo("----------------------------------------------------------")
        rospy.loginfo(f"Init Designator: {msg.designator_id}")
        rospy.logdebug(f"Full JSON:\n{msg.json_designator}")

    def handle_resolve_start(self, msg):
        rospy.loginfo("----------------------------------------------------------")
        rospy.loginfo(f"[Init] Encoding new Action designator: {msg.designator_id}")
        designator = json.loads(msg.json_designator)
        description_content = designator.get('description', {})
        designator_id = msg.designator_id
        # Always treat the designator as an Action
        # If anAction as highest level key, then use the rest of the JSON as description content
        if 'anAction' in designator:
            description_content = designator['anAction']
        uri, triples = self.parser.create_unresolved_designator('Action', description_content, designator_id)
        # Translate triples to knowrob triples
        builder = TripleQueryBuilder()
        for s, p, o in triples:
            # Remove leading < or trailing > if present
            s = s[1:] if s.startswith("<") else s
            s = s[:-1] if s.endswith(">") else s

            p = p[1:] if p.startswith("<") else p
            p = p[:-1] if p.endswith(">") else p

            o = o[1:] if o.startswith("<") else o
            o = o[:-1] if o.endswith(">") else o

            # Add the triple to the builder
            builder.add(s, p, o)
        # Set the modal frame
        modal_frame = get_default_modalframe()
        # modal_frame.minPastTimestamp = msg.stamp.to_sec()
        # modal_frame.confidence = 1.0
        # Add the designator to knowrob
        self.knowrob.tell(builder.get_triples(), modal_frame)
        rospy.loginfo(f"Sent {len(triples)} unresolved Action designator triples for {designator_id}")
        if print_triples:
            to_print = ""
            to_print += f"Unresolved triples for {designator_id}:\n"
            for s, p, o in triples:
                to_print += f"{s} {p} {o}\n"
            rospy.loginfo(to_print)

    def handle_resolve_finished(self, msg):
        rospy.loginfo("----------------------------------------------------------")
        rospy.loginfo(f"[ResolveStart] Processing Action designator resolution for: {msg.designator_id} from {getattr(msg, 'resolved_from_id', None)}")
        designator_json = json.loads(msg.json_designator)
        input_id = msg.resolved_from_id
        output_designator_id = msg.designator_id
        # Always treat the designator as an Action
        # If anAction as highest level key, then use the rest of the JSON as description content
        if 'anAction' in designator_json:
            designator_json = designator_json['anAction']
        resolving_uri, output_uri, triples = self.parser.create_designator_resolving(
            input_id,
            output_designator_id,
            'Action',
            designator_json,
            output_referent_content=None
            )
        # Translate triples to knowrob triples
        builder = TripleQueryBuilder()
        for s, p, o in triples:
            builder.add(s, p, o)
        # Set the modal frame
        modal_frame = get_default_modalframe()
        # modal_frame.minPastTimestamp = msg.stamp.to_sec()
        # modal_frame.confidence = 1.0
        # Add the designator to knowrob
        self.knowrob.tell(builder.get_triples(), modal_frame)
        rospy.loginfo(f"Sent {len(triples)} resolving triples for Action task {resolving_uri}")
        if print_triples:
            to_print = ""
            to_print += f"Resolving triples for {resolving_uri}:\n"
            for s, p, o in triples:
                to_print += f"{s} {p} {o}\n"
            rospy.loginfo(to_print)

    def handle_exec_start(self, msg):
        rospy.loginfo("----------------------------------------------------------")
        rospy.loginfo(f"Execution Started: {msg.designator_id}")
        designator = json.loads(msg.json_designator)
        # Get the task type from the designator
        # If anAction as highest level key, then use the rest of the JSON as description content
        if 'anAction' in designator:
            designator = designator['anAction']
        task_type = designator.get('type')
        # Always treat the designator as an Action
        uri, triples = self.parser.create_event(msg.designator_id, task_type)
        # Translate triples to knowrob triples
        builder = TripleQueryBuilder()
        for s, p, o in triples:
            builder.add(s, p, o)
        # Set the modal frame
        modal_frame = get_default_modalframe()
        # modal_frame.minPastTimestamp = msg.stamp.to_sec()
        # modal_frame.confidence = 1.0
        # Add the designator to knowrob
        self.knowrob.tell(builder.get_triples(), modal_frame)
        rospy.loginfo(f"Sent {len(triples)} execution start triples for {msg.designator_id}")
        if print_triples:
            # first create whole string then print it
            to_print = ""
            to_print += f"Execution start triples for {msg.designator_id}:\n"
            for s, p, o in triples:
                to_print += f"{s} {p} {o}\n"
            rospy.loginfo(to_print)              
            
    def handle_exec_finished(self, msg):
        # TODO: How do i add the end time?
        rospy.loginfo("----------------------------------------------------------")
        rospy.loginfo(f"Execution Finished: {msg.designator_id}")

if __name__ == '__main__':
    try:
        DesignatorLoggerNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
