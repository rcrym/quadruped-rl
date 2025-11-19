# # Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# # All rights reserved.
# #
# # SPDX-License-Identifier: BSD-3-Clause

import gymnasium as gym

from . import agents

# ##
# # Register Gym environments.
# ##


# gym.register(
#     id="Simpledog-Direct-v0",
#     entry_point=f"{__name__}.simpledog_env:SimpledogEnv",
#     disable_env_checker=True,
#     kwargs={
#         "env_cfg_entry_point": f"{__name__}.simpledog_env_cfg:SimpledogEnvCfg",
#         "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:PPORunnerCfg",
        # "skrl_amp_cfg_entry_point": f"{agents.__name__}:skrl_amp_cfg.yaml",
        # "skrl_cfg_entry_point": f"{agents.__name__}:skrl_ppo_cfg.yaml",
#     },
# )




# import gymnasium as gym
# from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env import LocomotionVelocityRoughEnv
# from .simpledog_env_cfg import SimpledogRoughEnvCfg

# gym.register(
#     id="Simpledog-Rough-v0",
#     entry_point="isaaclab_tasks.manager_based.locomotion.velocity.velocity_env:LocomotionVelocityRoughEnv",
#     disable_env_checker=True,
#     kwargs={
#         "env_cfg_entry_point": f"{__name__}.simpledog_env_cfg:SimpledogRoughEnvCfg",
#     },
# )


gym.register(
    id="Isaac-Velocity-Rough-Simpledog-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.simpledog_env_cfg:SimpledogRoughEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:SimpledogRoughPPORunnerCfg",
        "skrl_cfg_entry_point": f"{agents.__name__}:skrl_rough_ppo_cfg.yaml",
    },
)
