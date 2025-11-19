

# # SPDX-License-Identifier: BSD-3-Clause
# from __future__ import annotations
# from collections.abc import Sequence
# import math
# import torch

# import isaaclab.sim as sim_utils
# from isaaclab.assets import Articulation
# from isaaclab.envs import DirectRLEnv
# from isaaclab.sim.spawners.from_files import GroundPlaneCfg, spawn_ground_plane

# from .simpledog_env_cfg import SimpledogEnvCfg  # note: class name matches your cfg file
# from isaaclab.sensors import ContactSensor, ContactSensorCfg


# class SimpledogEnv(DirectRLEnv):
#     cfg: SimpledogEnvCfg

#     def __init__(self, cfg: SimpledogEnvCfg, render_mode: str | None = None, **kwargs):
#         super().__init__(cfg, render_mode, **kwargs)

#         # self.contact_sensor = ContactSensor(
#         #     ContactSensorCfg(
#         #         prim_path="/World/envs/env_.*/Robot",  # path to robot root prim
#         #         filter_prim_paths_expr=["Lower_Leg.*"],  # foot link names
#         #         track_air_time=True,
#         #         history_length=3,
#         #     )
#         # )

#         # self.contact_sensor._timestamp = 0.0
#         # self.contact_sensor._timestamp_last_update = 0.0
#         # self.contact_sensor._is_outdated = False


#         # cache
#         self.joint_pos = self.robot.data.joint_pos
#         self.joint_vel = self.robot.data.joint_vel
#         self._dof_ids = torch.arange(self.robot.num_joints, device=self.device)
#         self._q0 = self.robot.data.default_joint_pos[0].clone()  # nominal pose
#         self._action_scale = 0.1  # rad per joint command
#         self._torque_scale = 1.0  # for effort mode if you switch
#         names = self.robot.data.body_names                     # list[str]
#         name_to_idx = {n: i for i, n in enumerate(names)}
#         lower_leg_names = ["Lower_Leg", "Lower_Leg_01", "Lower_Leg_02", "Lower_Leg_03"]
#         self.allowed_contact_ids = torch.tensor(
#             [name_to_idx[n] for n in lower_leg_names if n in name_to_idx],
#             device=self.device, dtype=torch.long,
#         )

#     # --- scene setup ---
#     def _setup_scene(self):
#         self.robot = Articulation(self.cfg.robot_cfg)

#         # spawn_ground_plane(prim_path="/World/ground", cfg=GroundPlaneCfg())
#         self.scene.clone_environments(copy_from_source=False)
#         if self.device == "cpu":
#             self.scene.filter_collisions(global_prim_paths=[])
#         self.scene.articulations["robot"] = self.robot
        
#         light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
#         light_cfg.func("/World/Light", light_cfg)

#         # self.allowed_contact_ids, _ = self.robot.find_bodies([
#         #     "Lower_Leg", "Lower_Leg_01", "Lower_Leg_02", "Lower_Leg_03"
#         # ])

#     # --- RL hooks ---
#     def _pre_physics_step(self, actions: torch.Tensor) -> None:

#         # clip to [-1, 1]
#         self.actions = torch.clamp(actions, -1.0, 1.0)

#     def _apply_action(self) -> None:
#         # Smooth actions across steps to limit angular acceleration
#         if not hasattr(self, "prev_actions"):
#             self.prev_actions = torch.zeros_like(self.actions)

#         self.actions = 0.7 * self.prev_actions + 0.3 * self.actions
#         self.prev_actions = self.actions.clone()

#         # Position targets around nominal pose
#         q_des = self._q0.unsqueeze(0) + self._action_scale * self.actions

#         # PD position + velocity targets for smoother control
#         self.robot.set_joint_position_target(q_des, joint_ids=self._dof_ids)
#         # self.robot.set_joint_velocity_target(torch.zeros_like(q_des), joint_ids=self._dof_ids)

#         # q_des = self._q0.unsqueeze(0) + self._action_scale * self.actions
#         # self.robot.set_joint_position_target(q_des, joint_ids=self._dof_ids)
#         # if you prefer torque control instead, use:
#         # self.robot.set_joint_effort_target(self.actions * self._torque_scale, joint_ids=self._dof_ids)

#     def _get_observations(self) -> dict:
#         # minimal obs: joint pos/vel and commanded action
#         root_lin = self.robot.data.root_lin_vel_b
#         root_ang = self.robot.data.root_ang_vel_b
#         obs = torch.cat([self.joint_pos, self.joint_vel, root_lin, root_ang], dim=-1)
#         return {"policy": obs}

#     def _get_rewards(self) -> torch.Tensor:
#         # forward velocity (world x), alive bonus, action penalty, fall penalty
#         base_lin_vel = -self.robot.data.root_lin_vel_w[:, 1]  # vx
#         base_height = self.robot.data.root_pos_w[:, 2]
#         alive = self.cfg.rew_scale_alive * torch.ones_like(base_lin_vel)
#         forward = self.cfg.rew_scale_forward * base_lin_vel
#         energy_penalty = self.cfg.rew_scale_energy * torch.sum(self.actions ** 2, dim=1)
#         fell_mask = base_height < self.cfg.min_base_height
#         fall_penalty = self.cfg.rew_scale_fall * fell_mask.float()

#         # base_quat = self.robot.data.root_quat_w
#         # up = sim_utils.quat_apply(base_quat, torch.tensor([0, 0, 1], device=self.device))
#         # upright = up[:, 2]                  # 1 when upright
#         # upright_reward = 2.0 * upright      # penalize tilt
#         # Penalize non-flat base orientation (xy projected gravity vector)
#         base_orientation_penalty = torch.linalg.norm(
#             self.robot.data.projected_gravity_b[:, :2], dim=1
#         )  # 0 when upright

#         # Penalize vertical and roll/pitch velocity
#         base_motion_penalty = (
#             0.8 * torch.square(self.robot.data.root_lin_vel_b[:, 2]) +
#             0.2 * torch.sum(torch.abs(self.robot.data.root_ang_vel_b), dim=1)
#         )

#         base_height = self.robot.data.root_pos_w[:, 2]
#         height_target = 1
#         height_reward = 6.0 * torch.exp(-((base_height - height_target) ** 2) / 0.01)

#         # Penalize all body velocities (both linear and angular)
#         vel_penalty = 0.2 * torch.sum(torch.square(self.robot.data.root_lin_vel_w), dim=1)
#         ang_penalty = 0.1 * torch.sum(torch.square(self.robot.data.root_ang_vel_w), dim=1)

#         # optional: scale down Z linear and yaw angular velocity less harshly if you want walking
#         vel_penalty = vel_penalty + 0.05 * torch.square(self.robot.data.root_ang_vel_w[:, 2])
#         # forces = self.contact_sensor.data.net_forces_w   # shape [num_envs, num_bodies, 3]
#         # contacts = torch.norm(forces, dim=-1) > 1.0
#         # Extract quaternion (w, x, y, z)
#         # quat = self.robot.data.root_quat_w  # [num_envs, 4]
#         # yaw = torch.atan2(
#         #     2.0 * (quat[:, 0] * quat[:, 3] + quat[:, 1] * quat[:, 2]),
#         #     1.0 - 2.0 * (quat[:, 2] ** 2 + quat[:, 3] ** 2)
#         # )

#         # if not hasattr(self, "initial_yaw"):
#         #     self.initial_yaw = yaw.clone()

#         # yaw_deviation = torch.remainder(yaw - self.initial_yaw + math.pi, 2 * math.pi) - math.pi
#         # yaw_penalty = 2.0 * torch.abs(yaw_deviation)
#         # yaw_penalty = yaw_penalty.flatten()  # force [num_envs]

#         # bad_contact = contacts
#         # bad_contact[:, self.allowed_contact_ids] = False
#         # contact_penalty = 5.0 * bad_contact.any(dim=1).float()

                
#         if not hasattr(self, "prev_actions_for_jerk"):
#             self.prev_actions_for_jerk = torch.zeros_like(self.actions)

#         jerk_penalty = self.cfg.rew_scale_jerk * torch.norm(self.actions - self.prev_actions_for_jerk, dim=1)
#         self.prev_actions_for_jerk = self.actions.clone()
#         # ---- Ground-contact penalty (force-based, per link) ----
#         # shape: [num_envs, num_links]
#         # contact_f = torch.norm(self.robot.data.net_contact_forces_w, dim=-1)

#         # bad = contact_f > 1.0                    # threshold in N; tune
#         # if self.allowed_contact_ids.numel() > 0:
#         #     bad[:, self.allowed_contact_ids] = False   # allow lower legs
#         if self.cfg.debug_rewards:
#             print({
#                 "alive": alive.mean().item(),
#                 "forward": forward.mean().item(),
#                 "energy_penalty": energy_penalty.mean().item(),
#                 "motion_penalty": base_motion_penalty.mean().item(),
#                 "orient_penalty": base_orientation_penalty.mean().item(),
#                 "height": height_reward.mean().item(),
#                 "jerk": jerk_penalty.mean().item(),
#             })
#         # bad_any = bad.any(dim=1).float()         # per-env
#         # contact_penalty = -2.0 * bad_any         # weight; tune
#         # return alive + forward + energy + fall + upright_reward + height_reward + contact_penalty
#         return alive - energy_penalty - fall_penalty - base_orientation_penalty - base_motion_penalty + height_reward - jerk_penalty - vel_penalty - ang_penalty

#     def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
#         base_height = self.robot.data.root_pos_w[:, 2]
#         time_out = self.episode_length_buf >= self.max_episode_length - 1
#         fell = base_height < self.cfg.min_base_height
#         return fell, time_out

#     def _reset_idx(self, env_ids: Sequence[int] | None):
#         if env_ids is None:
#             env_ids = self.robot._ALL_INDICES
#         super()._reset_idx(env_ids)

#         # reset root
#         root_state = self.robot.data.default_root_state[env_ids].clone()
#         root_state[:, :3] += self.scene.env_origins[env_ids]
#         root_state[:, 2] += 0.02  # small lift

#         # reset joints near nominal
#         q = self.robot.data.default_joint_pos[env_ids].clone()
#         dq = torch.zeros_like(self.robot.data.default_joint_vel[env_ids])
#         noise = 0.05 * torch.randn_like(q)
#         q = q + noise
#         # write to sim
#         self.joint_pos[env_ids] = q
#         self.joint_vel[env_ids] = dq
#         self.robot.write_root_pose_to_sim(root_state[:, :7], env_ids)
#         self.robot.write_root_velocity_to_sim(root_state[:, 7:], env_ids)
#         self.robot.write_joint_state_to_sim(q, dq, None, env_ids)



# # # Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# # # All rights reserved.
# # #
# # # SPDX-License-Identifier: BSD-3-Clause

# # from __future__ import annotations

# # import math
# # import torch
# # from collections.abc import Sequence

# # import isaaclab.sim as sim_utils
# # from isaaclab.assets import Articulation
# # from isaaclab.envs import DirectRLEnv
# # from isaaclab.sim.spawners.from_files import GroundPlaneCfg, spawn_ground_plane
# # from isaaclab.utils.math import sample_uniform

# # from .simpledog_env_cfg import SimpledogEnvCfg


# # class SimpledogEnv(DirectRLEnv):
# #     cfg: SimpledogEnvCfg

# #     def __init__(self, cfg: SimpledogEnvCfg, render_mode: str | None = None, **kwargs):
# #         super().__init__(cfg, render_mode, **kwargs)

# #         self._cart_dof_idx, _ = self.robot.find_joints(self.cfg.cart_dof_name)
# #         self._pole_dof_idx, _ = self.robot.find_joints(self.cfg.pole_dof_name)

# #         self.joint_pos = self.robot.data.joint_pos
# #         self.joint_vel = self.robot.data.joint_vel

# #     def _setup_scene(self):
# #         self.robot = Articulation(self.cfg.robot_cfg)
# #         # add ground plane
# #         spawn_ground_plane(prim_path="/World/ground", cfg=GroundPlaneCfg())
# #         # clone and replicate
# #         self.scene.clone_environments(copy_from_source=False)
# #         # we need to explicitly filter collisions for CPU simulation
# #         if self.device == "cpu":
# #             self.scene.filter_collisions(global_prim_paths=[])
# #         # add articulation to scene
# #         self.scene.articulations["robot"] = self.robot
# #         # add lights
# #         light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
# #         light_cfg.func("/World/Light", light_cfg)

# #     def _pre_physics_step(self, actions: torch.Tensor) -> None:
# #         self.actions = actions.clone()

# #     def _apply_action(self) -> None:
# #         self.robot.set_joint_effort_target(self.actions * self.cfg.action_scale, joint_ids=self._cart_dof_idx)

# #     def _get_observations(self) -> dict:
# #         obs = torch.cat(
# #             (
# #                 self.joint_pos[:, self._pole_dof_idx[0]].unsqueeze(dim=1),
# #                 self.joint_vel[:, self._pole_dof_idx[0]].unsqueeze(dim=1),
# #                 self.joint_pos[:, self._cart_dof_idx[0]].unsqueeze(dim=1),
# #                 self.joint_vel[:, self._cart_dof_idx[0]].unsqueeze(dim=1),
# #             ),
# #             dim=-1,
# #         )
# #         observations = {"policy": obs}
# #         return observations

# #     def _get_rewards(self) -> torch.Tensor:
# #         total_reward = compute_rewards(
# #             self.cfg.rew_scale_alive,
# #             self.cfg.rew_scale_terminated,
# #             self.cfg.rew_scale_pole_pos,
# #             self.cfg.rew_scale_cart_vel,
# #             self.cfg.rew_scale_pole_vel,
# #             self.joint_pos[:, self._pole_dof_idx[0]],
# #             self.joint_vel[:, self._pole_dof_idx[0]],
# #             self.joint_pos[:, self._cart_dof_idx[0]],
# #             self.joint_vel[:, self._cart_dof_idx[0]],
# #             self.reset_terminated,
# #         )
# #         return total_reward

# #     def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
# #         self.joint_pos = self.robot.data.joint_pos
# #         self.joint_vel = self.robot.data.joint_vel

# #         time_out = self.episode_length_buf >= self.max_episode_length - 1
# #         out_of_bounds = torch.any(torch.abs(self.joint_pos[:, self._cart_dof_idx]) > self.cfg.max_cart_pos, dim=1)
# #         out_of_bounds = out_of_bounds | torch.any(torch.abs(self.joint_pos[:, self._pole_dof_idx]) > math.pi / 2, dim=1)
# #         return out_of_bounds, time_out

# #     def _reset_idx(self, env_ids: Sequence[int] | None):
# #         if env_ids is None:
# #             env_ids = self.robot._ALL_INDICES
# #         super()._reset_idx(env_ids)

# #         joint_pos = self.robot.data.default_joint_pos[env_ids]
# #         joint_pos[:, self._pole_dof_idx] += sample_uniform(
# #             self.cfg.initial_pole_angle_range[0] * math.pi,
# #             self.cfg.initial_pole_angle_range[1] * math.pi,
# #             joint_pos[:, self._pole_dof_idx].shape,
# #             joint_pos.device,
# #         )
# #         joint_vel = self.robot.data.default_joint_vel[env_ids]

# #         default_root_state = self.robot.data.default_root_state[env_ids]
# #         default_root_state[:, :3] += self.scene.env_origins[env_ids]

# #         self.joint_pos[env_ids] = joint_pos
# #         self.joint_vel[env_ids] = joint_vel

# #         self.robot.write_root_pose_to_sim(default_root_state[:, :7], env_ids)
# #         self.robot.write_root_velocity_to_sim(default_root_state[:, 7:], env_ids)
# #         self.robot.write_joint_state_to_sim(joint_pos, joint_vel, None, env_ids)


# # @torch.jit.script
# # def compute_rewards(
# #     rew_scale_alive: float,
# #     rew_scale_terminated: float,
# #     rew_scale_pole_pos: float,
# #     rew_scale_cart_vel: float,
# #     rew_scale_pole_vel: float,
# #     pole_pos: torch.Tensor,
# #     pole_vel: torch.Tensor,
# #     cart_pos: torch.Tensor,
# #     cart_vel: torch.Tensor,
# #     reset_terminated: torch.Tensor,
# # ):
# #     rew_alive = rew_scale_alive * (1.0 - reset_terminated.float())
# #     rew_termination = rew_scale_terminated * reset_terminated.float()
# #     rew_pole_pos = rew_scale_pole_pos * torch.sum(torch.square(pole_pos).unsqueeze(dim=1), dim=-1)
# #     rew_cart_vel = rew_scale_cart_vel * torch.sum(torch.abs(cart_vel).unsqueeze(dim=1), dim=-1)
# #     rew_pole_vel = rew_scale_pole_vel * torch.sum(torch.abs(pole_vel).unsqueeze(dim=1), dim=-1)
# #     total_reward = rew_alive + rew_termination + rew_pole_pos + rew_cart_vel + rew_pole_vel
# #     return total_reward