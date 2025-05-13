cmake_minimum_required(VERSION 3.0.2)
project(knowrob_designator)

## Find catkin and required components
find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  actionlib
  actionlib_msgs
  message_generation
)

catkin_python_setup()

## Declare ROS actions
add_action_files(
  DIRECTORY action
  FILES
    PushObjectDesignator.action
    DesignatorInit.action
    DesignatorResolutionStart.action
    DesignatorResolutionFinished.action
    DesignatorExecutionStart.action
    DesignatorExecutionFinished.action
)

## Generate messages from actions
generate_messages(
  DEPENDENCIES
  std_msgs
  actionlib_msgs
)

## Declare catkin package
catkin_package(
  CATKIN_DEPENDS rospy std_msgs actionlib actionlib_msgs message_runtime
)

# list all executable python and shell scripts for installation
install(PROGRAMS
   scripts/*
   DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
