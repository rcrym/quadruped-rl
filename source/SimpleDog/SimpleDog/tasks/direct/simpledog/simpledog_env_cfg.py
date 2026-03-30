from isaaclab.utils import configclass

from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg


from isaaclab_assets.robots.simple_dog import SIMPLEDOG_CFG


@configclass
class SimpledogRoughEnvCfg(LocomotionVelocityRoughEnvCfg):
    def __post_init__(self):
        # post init of parent
        super().__post_init__()

        self.scene.robot = SIMPLEDOG_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        
        # Uncomment below for height scanner and for the terrain curriculum
        # self.scene.height_scanner.prim_path = "{ENV_REGEX_NS}/Robot/trunk"
        # scale down the terrains because the robot is small
        self.scene.terrain.terrain_generator.sub_terrains["boxes"].grid_height_range = (0.025, 0.1)
        self.scene.terrain.terrain_generator.sub_terrains["random_rough"].noise_range = (0.01, 0.06)
        self.scene.terrain.terrain_generator.sub_terrains["random_rough"].noise_step = 0.01

        # Remove height scanner.
        self.scene.height_scanner = None
        self.observations.policy.height_scan = None
        # # Remove terrain curriculum.
        # self.curriculum.terrain_levels = None


        # reduce action scale
        self.actions.joint_pos.scale = 0.25
        
        # event
        self.events.push_robot = None
        self.events.add_base_mass.params["mass_distribution_params"] = (-1.0, 3.0)
        self.events.add_base_mass.params["asset_cfg"].body_names = "trunk"
        self.events.base_external_force_torque.params["asset_cfg"].body_names = "trunk"
        self.events.reset_robot_joints.params["position_range"] = (1.0, 1.0)
        self.events.reset_base.params = {
            "pose_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5),
            # "roll": (-math.pi, math.pi),      # allow any rotation lol
            # "pitch": (-math.pi, math.pi),
            "yaw": (-3.14, 3.14)},
            "velocity_range": {
                "x": (0.0, 0.0),
                "y": (0.0, 0.0),
                "z": (0.0, 0.0),
                "roll": (0.0, 0.0),
                "pitch": (0.0, 0.0),
                "yaw": (0.0, 0.0),
            },
        }




        # rewards
        # consider feet slide

        self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_calf"
        self.rewards.feet_air_time.weight = 0.1
        self.rewards.undesired_contacts = None
        self.rewards.dof_torques_l2.weight = -0.0002
        self.rewards.track_lin_vel_xy_exp.weight = 3.0
        self.rewards.track_ang_vel_z_exp.weight = 0.75
        self.rewards.dof_acc_l2.weight = -2.5e-7
        self.rewards.flat_orientation_l2.weight = -0.0005

# logs\rsl_rl\custom_quad_rough\2025-11-24_23-02-54 -- long run, still just say there tilted balancing
        # self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_calf"
        # self.rewards.feet_air_time.weight = 0.005
        # self.rewards.undesired_contacts = None
        # self.rewards.dof_torques_l2.weight = -0.0002
        # self.rewards.track_lin_vel_xy_exp.weight = 1.5
        # self.rewards.track_ang_vel_z_exp.weight = 0.75
        # self.rewards.dof_acc_l2.weight = -2.5e-7
        # self.rewards.flat_orientation_l2.weight = -0.005


# logs\rsl_rl\custom_quad_rough\2025-11-24_22-49-45 -- not sure but metrics seemed similar to one below
        # self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_calf" 
        # self.rewards.feet_air_time.weight = 0.01
        # self.rewards.dof_torques_l2.weight = -0.0002
        # self.rewards.track_lin_vel_xy_exp.weight = 1.5
        # self.rewards.track_ang_vel_z_exp.weight = 0.75
        # self.rewards.dof_acc_l2.weight = -2.5e-7
        # self.rewards.undesired_contacts = None
        # self.rewards.flat_orientation_l2.weight = -0.01

# logs\rsl_rl\custom_quad_rough\2025-11-24_21-37-44 -- still just freezing there
        # self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_calf" 
        # self.rewards.feet_air_time.weight = 0.01
        # self.rewards.dof_torques_l2.weight = -0.0002
        # self.rewards.track_lin_vel_xy_exp.weight = 1.5
        # self.rewards.track_ang_vel_z_exp.weight = 0.75
        # self.rewards.dof_acc_l2.weight = -2.5e-7
        # self.rewards.undesired_contacts.params["sensor_cfg"].body_names = ".*_(hip|thigh)"
        # self.rewards.undesired_contacts.weight = -0.1
        # self.rewards.flat_orientation_l2.weight = -0.1

# logs\rsl_rl\custom_quad_rough\2025-11-24_21-22-26 -- kind of started to try to crawl but just kept feet in air and balanced to not have thighs touch ground
        # self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_calf" 
        # self.rewards.feet_air_time.weight = 0.01
        # self.rewards.dof_torques_l2.weight = -0.0002
        # self.rewards.track_lin_vel_xy_exp.weight = 1.5
        # self.rewards.track_ang_vel_z_exp.weight = 0.75
        # self.rewards.dof_acc_l2.weight = -2.5e-7
        # self.rewards.undesired_contacts.params["sensor_cfg"].body_names = ".*_(hip|thigh)"
        # self.rewards.undesired_contacts.weight = -1.0
        # self.rewards.flat_orientation_l2.weight = -1.0

            # needs to be foot
        # logs\rsl_rl\custom_quad_rough\2025-11-24_20-33-15 - just tried to balance with two feet in air
        # self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_calf" 
        # self.rewards.feet_air_time.weight = 0.01
        # self.rewards.dof_torques_l2.weight = -0.0002
        # self.rewards.track_lin_vel_xy_exp.weight = 1.5
        # self.rewards.track_ang_vel_z_exp.weight = 0.75
        # self.rewards.dof_acc_l2.weight = -2.5e-7
        # self.rewards.undesired_contacts.params["sensor_cfg"].body_names = ".*_(hip|thigh)"
        # self.rewards.undesired_contacts.weight = -5.0
        # self.rewards.flat_orientation_l2.weight = -1.0


        # logs\rsl_rl\custom_quad_rough\2025-11-19_10-33-42 - Dogs looked like I was rewarding non-flat orientation
        # self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_calf"
        # self.rewards.feet_air_time.weight = 0.01
        # self.rewards.dof_torques_l2.weight = -0.0002
        # self.rewards.track_lin_vel_xy_exp.weight = 1.5
        # self.rewards.track_ang_vel_z_exp.weight = 0.75
        # self.rewards.dof_acc_l2.weight = -2.5e-7

        # self.rewards.undesired_contacts.params["sensor_cfg"].body_names = ".*_(hip|thigh)"
        # self.rewards.undesired_contacts.weight = -1
        # self.rewards.flat_orientation_l2.weight = 0.5


        # logs\rsl_rl\custom_quad_rough\2025-11-19_10-33-42 - accidentally did contacts none
        # self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_calf"
        # self.rewards.undesired_contacts.weight = -1
        # self.rewards.flat_orientation_l2.weight = 0.5
        # self.rewards.feet_air_time.weight = 0.005
        # self.rewards.undesired_contacts = None
        # self.rewards.dof_torques_l2.weight = -0.0002
        # self.rewards.track_lin_vel_xy_exp.weight = 1.5
        # self.rewards.track_ang_vel_z_exp.weight = 0.75
        # self.rewards.dof_acc_l2.weight = -2.5e-7

        # logs\rsl_rl\custom_quad_rough\2025-11-19_10-04-53
        # self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_calf"
        # self.rewards.feet_air_time.weight = 0.001
        # self.rewards.undesired_contacts = None
        # self.rewards.dof_torques_l2.weight = -0.00002
        # self.rewards.track_lin_vel_xy_exp.weight = 5
        # self.rewards.track_ang_vel_z_exp.weight = 0.75
        # self.rewards.dof_acc_l2.weight = -2.5e-8

        # logs\rsl_rl\custom_quad_rough\2025-11-19_08-31-55 - long night run but had ground plane
        #  might have been custom_quad_rough\2025-11-18_23-35-01 actually
        # self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_calf"
        # self.rewards.feet_air_time.weight = 0.005
        # self.rewards.undesired_contacts = None
        # self.rewards.dof_torques_l2.weight = -0.0002
        # self.rewards.track_lin_vel_xy_exp.weight = 1.5
        # self.rewards.track_ang_vel_z_exp.weight = 0.75
        # self.rewards.dof_acc_l2.weight = -2.5e-7

        # logs\rsl_rl\custom_quad_rough\2025-10-28_22-35-12 - first long night run
        # self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_calf"
        # self.rewards.feet_air_time.weight = 0.01
        # self.rewards.undesired_contacts = None
        # self.rewards.dof_torques_l2.weight = -0.00002
        # self.rewards.track_lin_vel_xy_exp.weight = 1.5
        # self.rewards.track_ang_vel_z_exp.weight = 0.75
        # self.rewards.dof_acc_l2.weight = -2.5e-10

        # tutorial
        # self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_foot"
        # self.rewards.feet_air_time.weight = 0.01
        # self.rewards.undesired_contacts = None
        # self.rewards.dof_torques_l2.weight = -0.0002
        # self.rewards.track_lin_vel_xy_exp.weight = 1.5
        # self.rewards.track_ang_vel_z_exp.weight = 0.75
        # self.rewards.dof_acc_l2.weight = -2.5e-7


        # anymal c
        # self.rewards.flat_orientation_l2.weight = -5.0
        # self.rewards.dof_torques_l2.weight = -2.5e-5
        # self.rewards.feet_air_time.weight = 0.5

        # terminations
        self.terminations.base_contact.params["sensor_cfg"].body_names = "trunk"

@configclass
class CurriculumCfg_PLAY:
    pass

@configclass
class SimpledogRoughEnvCfg_PLAY(SimpledogRoughEnvCfg):
    curriculum: CurriculumCfg_PLAY = CurriculumCfg_PLAY()


    def __post_init__(self):
        super().__post_init__()

        # number of envs and spacing
        self.scene.num_envs = 50
        self.scene.env_spacing = 2

        self.events.add_base_mass = None


        # flat terrain only
        # --------------------
        # Terrain (flat plane)
        # --------------------
        self.scene.terrain.terrain_type = "plane"
        self.scene.terrain.terrain_generator = None
        self.scene.terrain.env_spacing = self.scene.env_spacing
        self.scene.terrain.max_init_terrain_level = None

        # curriculum (CRITICAL)
        self.curriculum.terrain_levels = None


        self.scene.terrain.terrain_generator = None
        self.scene.terrain.max_init_terrain_level = None

        # fixed spawn orientation (no random yaw)
        self.scene.robot.init_state.rot = (1.0, 0.0, 0.0, 0.0)
        self.scene.robot.init_state.randomize_rot = False

        self.events.reset_base = None

        self.commands.base_velocity.debug_vis = False

        # disable randomness for play
        self.observations.policy.enable_corruption = False
        self.events.base_external_force_torque = None
        self.events.push_robot = None

# @configclass
# class SimpledogRoughEnvCfg_PLAY(SimpledogRoughEnvCfg):

#     def __post_init__(self):
#         # post init of parent
#         super().__post_init__()

#         # make a smaller scene for play
#         self.scene.num_envs = 50
#         self.scene.env_spacing = 2.5
#         # spawn the robot randomly in the grid (instead of their terrain levels)
#         self.scene.terrain.max_init_terrain_level = None
#         # reduce the number of terrains to save memory
#         if self.scene.terrain.terrain_generator is not None:
#             self.scene.terrain.terrain_generator.num_rows = 5
#             self.scene.terrain.terrain_generator.num_cols = 5
#             self.scene.terrain.terrain_generator.curriculum = False

#         # disable randomization for play
#         self.observations.policy.enable_corruption = False
#         # remove random pushing event
#         self.events.base_external_force_torque = None
#         self.events.push_robot = None
        





# Good long run but dog could only walk backwards:



# from isaaclab.utils import configclass

# from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg


# from isaaclab_assets.robots.simple_dog import SIMPLEDOG_CFG


# @configclass
# class SimpledogRoughEnvCfg(LocomotionVelocityRoughEnvCfg):
#     def __post_init__(self):
#         # post init of parent
#         super().__post_init__()

#         self.scene.robot = SIMPLEDOG_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
#         self.scene.height_scanner.prim_path = "{ENV_REGEX_NS}/Robot/base"
#         # scale down the terrains because the robot is small
#         self.scene.terrain.terrain_generator.sub_terrains["boxes"].grid_height_range = (0.025, 0.1)
#         self.scene.terrain.terrain_generator.sub_terrains["random_rough"].noise_range = (0.01, 0.06)
#         self.scene.terrain.terrain_generator.sub_terrains["random_rough"].noise_step = 0.01

#         # reduce action scale
#         self.actions.joint_pos.scale = 0.25

#         # event
#         self.events.push_robot = None
#         self.events.add_base_mass.params["mass_distribution_params"] = (-1.0, 3.0)
#         self.events.add_base_mass.params["asset_cfg"].body_names = "base"
#         self.events.base_external_force_torque.params["asset_cfg"].body_names = "base"
#         self.events.reset_robot_joints.params["position_range"] = (1.0, 1.0)
#         self.events.reset_base.params = {
#             "pose_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5), "yaw": (-3.14, 3.14)},
#             "velocity_range": {
#                 "x": (0.0, 0.0),
#                 "y": (0.0, 0.0),
#                 "z": (0.0, 0.0),
#                 "roll": (0.0, 0.0),
#                 "pitch": (0.0, 0.0),
#                 "yaw": (0.0, 0.0),
#             },
#         }

#         # rewards
        # self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_calf"
        # self.rewards.feet_air_time.weight = 0.01
        # self.rewards.undesired_contacts = None
        # self.rewards.dof_torques_l2.weight = -0.0002
        # self.rewards.track_lin_vel_xy_exp.weight = 1.5
        # self.rewards.track_ang_vel_z_exp.weight = 0.75
        # self.rewards.dof_acc_l2.weight = -2.5e-8
        #         # self.rewards.dof_acc_l2.weight = -2.5e-7

        # self.rewards.feet_air_time.params["sensor_cfg"].body_names = ".*_calf"
        # self.rewards.feet_air_time.weight = 0.01
        # self.rewards.undesired_contacts = None
        # self.rewards.dof_torques_l2.weight = -0.00002
        # self.rewards.track_lin_vel_xy_exp.weight = 1.5
        # self.rewards.track_ang_vel_z_exp.weight = 0.75
        # self.rewards.dof_acc_l2.weight = -2.5e-10

#         # terminations
#         self.terminations.base_contact.params["sensor_cfg"].body_names = "base"

# @configclass
# class SimpledogRoughEnvCfg_PLAY(SimpledogRoughEnvCfg):
#     def __post_init__(self):
#         # post init of parent
#         super().__post_init__()

#         # make a smaller scene for play
#         self.scene.num_envs = 50
#         self.scene.env_spacing = 2.5
#         # spawn the robot randomly in the grid (instead of their terrain levels)
#         self.scene.terrain.max_init_terrain_level = None
#         # reduce the number of terrains to save memory
#         if self.scene.terrain.terrain_generator is not None:
#             self.scene.terrain.terrain_generator.num_rows = 5
#             self.scene.terrain.terrain_generator.num_cols = 5
#             self.scene.terrain.terrain_generator.curriculum = False

#         # disable randomization for play
#         self.observations.policy.enable_corruption = False
#         # remove random pushing event
#         self.events.base_external_force_torque = None
#         self.events.push_robot = None






# from isaaclab.assets import ArticulationCfg
# from isaaclab.envs import DirectRLEnvCfg
# from isaaclab.scene import InteractiveSceneCfg
# from isaaclab.sim import SimulationCfg
# from isaaclab.utils import configclass


# @configclass
# class SimpledogEnvCfg(DirectRLEnvCfg):
#     # --- Environment timing ---
#     decimation = 2
#     episode_length_s = 10.0

#     # --- Simulation setup ---
#     sim: SimulationCfg = SimulationCfg(dt=1 / 120, render_interval=decimation)

#     # --- Robot ---
#     robot_cfg: ArticulationCfg = SIMPLEDOG_CFG.replace(
#         prim_path="/World/envs/env_.*/Robot"
#     )

#     # --- Scene ---
#     scene: InteractiveSceneCfg = InteractiveSceneCfg(
#         num_envs=512, env_spacing=3.0, replicate_physics=True
#     )

#     # --- Action/observation spaces ---
#     # 12 joints → 12 actions
#     action_space = 12
#     observation_space = 60  # adjust later
#     state_space = 0

#     # --- Reward scales (locomotion style) ---
#     rew_scale_alive = 1.0          # stay upright
#     rew_scale_forward = 2.0        # encourage forward velocity
#     rew_scale_energy = 0.001      # penalize large torques
#     rew_scale_fall = 5.0          # big penalty if fall
#     rew_scale_jerk = 0.5

#     # --- Termination condition ---
#     min_base_height = 0.2         # terminate if base z < 0.15 m

#     debug_rewards = True          # print reward components for debugging



# # # Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# # # All rights reserved.
# # #
# # # SPDX-License-Identifier: BSD-3-Clause

# # from isaaclab_assets.robots.simple_dog import SIMPLEDOG_CFG

# # from isaaclab.assets import ArticulationCfg
# # from isaaclab.envs import DirectRLEnvCfg
# # from isaaclab.scene import InteractiveSceneCfg
# # from isaaclab.sim import SimulationCfg
# # from isaaclab.utils import configclass


# # @configclass
# # class SimpledogEnvCfg(DirectRLEnvCfg):
# #     # env
# #     decimation = 2
# #     episode_length_s = 5.0
# #     # - spaces definition
# #     action_space = 1
# #     observation_space = 4
# #     state_space = 0

# #     # simulation
# #     sim: SimulationCfg = SimulationCfg(dt=1 / 120, render_interval=decimation)

# #     # robot(s)
# #     robot_cfg: ArticulationCfg = SIMPLEDOG_CFG.replace(prim_path="/World/envs/env_.*/Robot")

# #     # scene
# #     scene: InteractiveSceneCfg = InteractiveSceneCfg(num_envs=4096, env_spacing=4.0, replicate_physics=True)

# #     # custom parameters/scales
# #     # - controllable joint
# #     cart_dof_name = "slider_to_cart"
# #     pole_dof_name = "cart_to_pole"
# #     # - action scale
# #     action_scale = 100.0  # [N]
# #     # - reward scales
# #     rew_scale_alive = 1.0
# #     rew_scale_terminated = -2.0
# #     rew_scale_pole_pos = -1.0
# #     rew_scale_cart_vel = -0.01
# #     rew_scale_pole_vel = -0.005
# #     # - reset states/conditions
# #     initial_pole_angle_range = [-0.25, 0.25]  # pole angle sample range on reset [rad]
# #     max_cart_pos = 3.0  # reset if cart exceeds this position [m]




