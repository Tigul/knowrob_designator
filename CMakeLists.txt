cmake_minimum_required(VERSION 3.0.2)
project(knowrob_designator)

## Find catkin and required components
find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  message_generation
)

catkin_python_setup()

## Declare ROS messages
add_message_files(
  DIRECTORY msg
  FILES
    PushObjectDesignator.msg
    DesignatorInit.msg
    DesignatorResolutionStart.msg
    DesignatorResolutionFinished.msg
    DesignatorExecutionStart.msg
    DesignatorExecutionFinished.msg
)

## Generate messages
generate_messages(
  DEPENDENCIES
  std_msgs
)

## Declare catkin package
catkin_package(
  CATKIN_DEPENDS rospy std_msgs message_runtime
)

# list all executable python and shell scripts for installation
install(PROGRAMS
   scripts/*
   DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
