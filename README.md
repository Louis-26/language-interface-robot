# Data
download from https://drive.google.com/uc?id=153XoDitOarYKKlsMuBxYeyDYNrXBuAoN&export=download

Implemented natural language interface (NLI) and PyBullet environment for instructive motion planning.

# Language Interface
Without speech triggers (press button to control speech input):
```
cd language_interface
python nli.py
```
With speech triggers:
```
cd language_interface
python nli_trigger.py
```
# PyBullet Environment for Instructive motion planning
Tested with:<br>
**Python 3.10.16**<br>
**Ubuntu 20.04**

## Installation instructions:
### Install OMPL Python Wheel
Install the OMPL Python wheel from the pre-release version:
```
pip install https://github.com/ompl/ompl/releases/download/prerelease/ompl-1.7.0-cp310-cp310-manylinux_2_28_x86_64.whl
```
### Install OMPL from source
It is very important that you compile ompl with the correct python version with the CMake flag.
```
git clone https://github.com/ompl/ompl.git
mkdir build/Release
cd build/Release
cmake ../.. -DPYTHON_EXEC=/path/to/python-X.Y # This is important!!! Make sure you are pointing to the correct python version.
make -j 4 update_bindings # replace "4" with the number of cores on your machine. This step takes some time.
make -j 4 # replace "4" with the number of cores on your machine
```

### Install Pybullet
Just install pybullet normally.
```
pip install pybullet
```

## Demo
To run the instructive motion planning example:
```
python instruct_move.py
```

## Additional Information
1. Currently tested planners include PRM, RRT, RRTstar, RRTConnect, EST, FMT* and BIT*. But all planners in OMPL should work. Just add them in the set_planner API in PbOMPL class.
2. To work with other robot, you might need to inherit from PbOMPLRobot class in PbOMPL and override several functionalities. Refer to my_planar_robot.py for an example. Refer to demo_plannar.py for an example.
