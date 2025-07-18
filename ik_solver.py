"""
Adapted from OmniGibson and the Lula IK solver
"""
import pdb
import omnigibson.lazy as lazy
import numpy as np
from scipy.spatial.transform import Rotation as R

class IKSolver:
    """
    Class for thinly wrapping Lula IK solver
    """

    def __init__(
        self,
        robot_description_path,
        robot_urdf_path,
        eef_name,
        reset_joint_pos,
        world2robot_homo,
        robot_name,
        robot
    ):
        # Create robot description, kinematics, and config
        self.robot_description = lazy.lula.load_robot(robot_description_path, robot_urdf_path)
        self.kinematics = self.robot_description.kinematics()
        self.config = lazy.lula.CyclicCoordDescentIkConfig()
        self.eef_name = eef_name
        self.reset_joint_pos = reset_joint_pos
        self.world2robot_homo = world2robot_homo
        self.robot_name=robot_name.lower()
        self.robot=robot
        breakpoint()

    def solve(
        self,
        target_pose_homo,
        position_tolerance=0.01,
        orientation_tolerance=0.05,
        position_weight=1.0,
        orientation_weight=0.05,
        max_iterations=150,
        initial_joint_pos=None,
    ):
        """
        Backs out joint positions to achieve desired @target_pos and @target_quat

        Args:
            target_pose_homo (np.ndarray): [4, 4] homogeneous transformation matrix of the target pose in world frame
            position_tolerance (float): Maximum position error (L2-norm) for a successful IK solution
            orientation_tolerance (float): Maximum orientation error (per-axis L2-norm) for a successful IK solution
            position_weight (float): Weight for the relative importance of position error during CCD
            orientation_weight (float): Weight for the relative importance of position error during CCD
            max_iterations (int): Number of iterations used for each cyclic coordinate descent.
            initial_joint_pos (None or n-array): If specified, will set the initial cspace seed when solving for joint
                positions. Otherwise, will use self.reset_joint_pos

        Returns:
            ik_results (lazy.lula.CyclicCoordDescentIkResult): IK result object containing the joint positions and other information.
        """
        # convert target pose to robot base frame
        target_pose_robot = np.dot(self.world2robot_homo, target_pose_homo)
        # if self.robot_name == "piper":
        #     link6_pos = self.robot.links["link6"].get_position()
        #     link7_pos = self.robot.links["link7"].get_position()
        #     link8_pos = self.robot.links["link8"].get_position()
        #     finger_center = 0.5 * (link7_pos + link8_pos)
        #     offset_vector_world = 0.95 * ((finger_center - link6_pos).numpy())
        #     # Convert offset to robot base frame (only rotation applies)
        #     R_world_to_robot = self.world2robot_homo[:3, :3]
        #     offset_vector_robot = R_world_to_robot @ offset_vector_world
        #     target_pose_robot[:3, 3] -= offset_vector_robot

        target_pose_pos = target_pose_robot[:3, 3]
        target_pose_rot = target_pose_robot[:3, :3]
        ik_target_pose = lazy.lula.Pose3(lazy.lula.Rotation3(target_pose_rot), target_pose_pos)
        # Set the cspace seed and tolerance
        initial_joint_pos = self.reset_joint_pos if initial_joint_pos is None else np.array(initial_joint_pos)
        # Patch: ensure 8D seed for Piper
        if self.robot_name == "piper" and len(initial_joint_pos) == 6:
            gripper_defaults = self.reset_joint_pos[6:] if len(self.reset_joint_pos) == 8 else [1.0, 1.0]
            initial_joint_pos = np.concatenate([initial_joint_pos, gripper_defaults])
        elif self.robot_name == "frankapanda":
            # Franka expects 7D arm only
            if len(initial_joint_pos) != 7:
                initial_joint_pos = self.reset_joint_pos[:7]
        self.config.cspace_seeds = [initial_joint_pos]
        self.config.position_tolerance = position_tolerance
        self.config.orientation_tolerance = orientation_tolerance
        self.config.ccd_position_weight = position_weight
        self.config.ccd_orientation_weight = orientation_weight
        self.config.max_num_descents = max_iterations
        # Compute target joint positions
        if self.robot_name == "piper":
            ik_results = lazy.lula.compute_ik_ccd(self.kinematics, ik_target_pose, "link8", self.config)
        elif self.robot_name == "fetch":
            ik_results = lazy.lula.compute_ik_ccd(self.kinematics, ik_target_pose, self.eef_name, self.config)    
        elif self.robot_name == "frankapanda":
            leftfinger_position = self.robot.links["panda_leftfinger"].get_position_orientation()[0]
            rightfinger_position = self.robot.links["panda_rightfinger"].get_position_orientation()[0]
            finger_center = 0.5 * (leftfinger_position + rightfinger_position)
            self.eef_offset = 0.5 * (rightfinger_position - leftfinger_position)  
            
            # Use fixed Euler angles: e.g., z-down grasp (flipped pitch)           
            grasp_euler = [0.0, 22.6, 2.0]  # roll=0, pitch=180°, yaw=0
            rotation = R.from_euler('xyz', grasp_euler).as_matrix()
            # rotation = ik_target_pose.rotation.matrix()
            position = ik_target_pose.translation + self.eef_offset.cpu().numpy()

            ik_target_pose = lazy.lula.Pose3(lazy.lula.Rotation3(rotation), position)
            ik_results = lazy.lula.compute_ik_ccd(self.kinematics, ik_target_pose, self.eef_name, self.config)  
        breakpoint()
        return ik_results