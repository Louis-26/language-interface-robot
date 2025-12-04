# set up environment
```bash
conda create -n language_interface_robot python=3.10.16 -y
```

# Data
download from https://drive.google.com/uc?id=153XoDitOarYKKlsMuBxYeyDYNrXBuAoN&export=download

```bash
conda activate language_interface_robot
pip install gdown
chmod +x load_data.sh
./load_data.sh
```

# System version
- python: 3.10.16
- ubuntu: 22.04

Implemented natural language interface (NLI) and PyBullet environment for instructive motion planning.


# PyBullet Environment for Instructive motion planning
Tested with:<br>
**Python 3.10.16**<br>
**Ubuntu 20.04**

## Installation instructions:
### Install OMPL Python Wheel
Install the OMPL Python wheel from the pre-release version:
```bash
chmod +x install_ompl.sh
./install_ompl.sh
pip list | grep ompl # check if ompl is installed correctly
```

### Install OMPL from source
It is very important that you compile ompl with the correct python version with the CMake flag.
```bash
wget https://github.com/ompl/ompl/archive/refs/heads/main.zip -O ompl-main.zip
unzip ompl-main.zip -d ompl-temp
mkdir ompl
mv ompl-temp/ompl-main/* ompl/
rm -rf ompl-temp
mkdir build/Release
cd build/Release
cmake ../.. -DPYTHON_EXEC=/path/to/python-X.Y # This is important!!! Make sure you are pointing to the correct python version.
make -j 4 update_bindings # replace "4" with the number of cores on your machine. This step takes some time.
make -j 4 # replace "4" with the number of cores on your machine
```

### Install Pybullet
Just install pybullet normally.
```bash
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