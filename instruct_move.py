import os.path as osp
import pybullet as p
import math
import sys
import pybullet_data
sys.path.insert(0, osp.join(osp.dirname(osp.abspath(__file__)), '../'))

import pb_ompl

class BoxDemo:
    def __init__(self):
        self.obstacles = []

        # --- PyBullet setup ---
        p.connect(p.GUI)
        p.setGravity(0, 0, -9.8)
        p.setTimeStep(1. / 240.)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.loadURDF("plane.urdf")

        # --- Load Franka robot ---
        urdf_path = osp.join("models", "franka_description", "robots", "panda_arm.urdf")
        robot_id = p.loadURDF(urdf_path, (0, 0, 0), useFixedBase=True)
        self.robot = pb_ompl.PbOMPLRobot(robot_id)

        # --- Setup OMPL planner (no obstacles by default) ---
        self.planner = pb_ompl.PbOMPL(self.robot, self.obstacles)
        self.planner.set_planner("BITstar")

        # --- Add any obstacles here (optional) ---
        self.add_obstacles()

    def clear_obstacles(self):
        for obs in self.obstacles:
            p.removeBody(obs)
        self.obstacles.clear()
        self.planner.set_obstacles(self.obstacles)

    def add_obstacles(self):
        # Example: a box in the workspace
        self.add_box([1, 0, 0.7], [0.5, 0.5, 0.05])
        self.planner.set_obstacles(self.obstacles)

    def add_box(self, pos, half_size):
        col = p.createCollisionShape(p.GEOM_BOX, halfExtents=half_size)
        body = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=col, basePosition=pos)
        self.obstacles.append(body)

    def print_help(self):
        """Print the list of available commands."""
        print("\n--- Interactive BoxDemo Commands ---")
        print("  - 'start x1,x2,...,x7': Set the start joint angles.")
        print("  - 'start_xyz x,y,z': Set the start position of the end-effector (IK will compute joint angles).")
        print("  - 'goal x1,x2,...,x7': Set the goal joint angles.")
        print("  - 'goal_xyz x,y,z': Set the goal position of the end-effector (IK will compute joint angles).")
        print("  - 'add_obstacle x,y,z,half_x,half_y,half_z': Add a box obstacle.")
        print("  - 'remove_obstacles': Remove all obstacles.")
        print("  - 'plan': Plan and execute the path.")
        print("  - 'status': Print the current status, joint angles, and end-effector position.")
        print("  - 'help': Show this help message.")
        print("  - 'q' or 'quit': Exit the program.\n")

    def demo(self):
        self.print_help()  # Show the help message at the start

        start = None
        goal = None
        start_xyz = None
        goal_xyz = None

        while True:
            user = input("Enter command -> ").strip()
            if user.lower() in ("q", "quit"):
                break

            if user.lower() == "help":
                self.print_help()

            elif user.startswith("start"):
                if user.startswith("start_xyz"):
                    try:
                        xyz = [float(x) for x in user.split()[1].split(",")]
                        # Use IK to compute joint angles for the given end-effector position
                        start = p.calculateInverseKinematics(
                            self.robot.id,  # Robot ID
                            self.robot.joint_idx[-1],  # End-effector link index
                            xyz  # Desired end-effector position
                        )
                        self.robot.set_state(start)
                        start_xyz = xyz
                        print(f"Start state (computed via IK): {start}")
                        print(f"Start position (XYZ): {start_xyz}")
                    except (ValueError, IndexError):
                        print("Invalid format. Example: start_xyz 0.5,0.5,0.5")
                else:
                    try:
                        start = [float(x) for x in user.split()[1].split(",")]
                        if len(start) != len(self.robot.joint_idx):
                            print(f"Please enter exactly {len(self.robot.joint_idx)} numbers.")
                            start = None
                            continue
                        self.robot.set_state(start)
                        # Compute the XYZ position of the end-effector for the given joint angles
                        end_effector_state = p.getLinkState(self.robot.id, self.robot.joint_idx[-1])
                        start_xyz = end_effector_state[0]
                        print(f"Start state set to: {start}")
                        print(f"Start position (XYZ): {start_xyz}")
                    except (ValueError, IndexError):
                        print("Invalid format. Example: start 0,1.5,0,-0.1,0,0.2,0")

            elif user.startswith("goal"):
                if user.startswith("goal_xyz"):
                    try:
                        xyz = [float(x) for x in user.split()[1].split(",")]
                        # Use IK to compute joint angles for the given end-effector position
                        goal = p.calculateInverseKinematics(
                            self.robot.id,  # Robot ID
                            self.robot.joint_idx[-1],  # End-effector link index
                            xyz  # Desired end-effector position
                        )
                        goal_xyz = xyz
                        print(f"Goal state (computed via IK): {goal}")
                        print(f"Goal position (XYZ): {goal_xyz}")
                    except (ValueError, IndexError):
                        print("Invalid format. Example: goal_xyz 0.5,0.5,0.5")
                else:
                    try:
                        goal = [float(x) for x in user.split()[1].split(",")]
                        if len(goal) != len(self.robot.joint_idx):
                            print(f"Please enter exactly {len(self.robot.joint_idx)} numbers.")
                            goal = None
                            continue
                        # Compute the XYZ position of the end-effector for the given joint angles
                        end_effector_state = p.getLinkState(self.robot.id, self.robot.joint_idx[-1])
                        goal_xyz = end_effector_state[0]
                        print(f"Goal state set to: {goal}")
                        print(f"Goal position (XYZ): {goal_xyz}")
                    except (ValueError, IndexError):
                        print("Invalid format. Example: goal 0,1.5,0,-0.1,0,0.2,0")

            elif user.startswith("add_obstacle"):
                try:
                    params = [float(x) for x in user.split()[1].split(",")]
                    if len(params) != 6:
                        print("Please enter exactly 6 numbers: x,y,z,half_x,half_y,half_z.")
                        continue
                    pos = params[:3]
                    half_size = params[3:]
                    self.add_box(pos, half_size)
                    self.planner.set_obstacles(self.obstacles)
                    print(f"Added obstacle at position {pos} with half-size {half_size}.")
                except (ValueError, IndexError):
                    print("Invalid format. Example: add_obstacle 1,0,0.7,0.5,0.5,0.05")

            elif user == "remove_obstacles":
                self.clear_obstacles()
                print("All obstacles removed.")

            elif user == "plan":
                if start is None or goal is None:
                    print("Please set both the start and goal states before planning.")
                    continue

                print("Planning...")
                res, path = self.planner.plan(goal)
                if not res:
                    print("  ❌ No path found. Try a different goal or adjust obstacles.\n")
                    continue

                print(f"  ✅ Path found with {len(path)} waypoints. Executing...\n")
                self.planner.execute(path)
                print("  🎉 Movement complete.\n")

            elif user == "status":
                # Print the current status
                current_joint_angles = self.robot.get_cur_state()
                end_effector_state = p.getLinkState(self.robot.id, self.robot.joint_idx[-1])
                current_xyz = end_effector_state[0]  # Position of the end-effector
                print("\n--- Current Status ---")
                print(f"Current Joint Angles: {current_joint_angles}")
                print(f"Current End-Effector Position (XYZ): {current_xyz}")
                print(f"Start Joint Angles: {start}")
                print(f"Start Position (XYZ): {start_xyz}")
                print(f"Goal Joint Angles: {goal}")
                print(f"Goal Position (XYZ): {goal_xyz}")
                print("----------------------\n")

            else:
                print("Unknown command. Please try again.")

if __name__ == '__main__':
    demo = BoxDemo()
    demo.demo()