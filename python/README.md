# Brief
- This project is intended to play go game via a certain sort of robot arm
- Dependencies:
  - ROS, Moveit
  - PhonixGo, Bazel
  - OpenCV

- There are 3 main parts of this project
  - robot_eye: A camera capture the image of chessboard
  - Human_level_robot: An abstract robot, can understand chessboard, warehouse,etc
    - soft_robot: ROS and MoveIt
    - hard_robot: Controlled by Marlin-firmware
  - manager: The brain of the whole system.

# TODO: project name
- This project's name is serieriously not matched.
- A better name is required.
- Solution A: rename the project to a new name
- Solution B: create a new project and stop to maintain this one
- Candidates of new names:
 - `Go_game_robot`, `GoBot`, `GoGaBot`, 
 - We appreciate any suggestion of a better idea. 

## ros_marlin_bridge
- Subscribe ros message, 
- convert to gcode, 
- send to marlin
  - Marlin side, might be busy


# Launch
- How to create and make the file executable?
  - copy the text of the file
  - `cd ~`
  - `touch a.bash`
  - `nano a.bash`
  - paste the text 
  - Ctrl + s to save
  - Ctrl + x to exit nano
  - sudo chmod 777 ./a.bash
- How to launch?
 - `cd ~`
 - `./a.bash`

```
#! /bin/bash

# This file is at user root folder
# To launch this bash file , type
# ./a.bash  + <Enter>



gnome-terminal --tab --title="ROS go_scara_moveit" -- bash -ic "roslaunch go_scara_moveit demo.launch"

cd ~/PhoenixGo
gnome-terminal --tab --title="Phoenix Go" -- bash -ic 'bazel-bin/mcts/mcts_main --gtp --config_path=etc/mcts_1gpu.conf --logtostderr --v=0 --listen_port=50007'

gnome-terminal --tab --title='Serial Permission ' -- bash -ic "sudo chmod 666 /dev/ttyUSB0"


cd ~/gitrepo/ros_marlin_bridge
python2 starter.py

```




