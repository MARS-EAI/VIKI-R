from typing import Union
import h5py
import numpy as np
from torch.utils.data import Dataset
from tqdm import tqdm
import os
import pdb
import pickle

from mani_skill.utils.io_utils import load_json
from mani_skill.utils import sapien_utils
from mani_skill.utils import common

# loads h5 data into memory for faster access
def load_h5_data(data):
    out = dict()
    for k in data.keys():
        if isinstance(data[k], h5py.Dataset):
            out[k] = data[k][:]
        else:
            out[k] = load_h5_data(data[k])
    return out

class ManiSkillTrajectoryDataset(Dataset):
    """
    A general torch Dataset you can drop in and use immediately with just about any trajectory .h5 data generated from ManiSkill.
    This class simply is a simple starter code to load trajectory data easily, but does not do any data transformation or anything
    advanced. We recommend you to copy this code directly and modify it for more advanced use cases

    Args:
        dataset_file (str): path to the .h5 file containing the data you want to load
        load_count (int): the number of trajectories from the dataset to load into memory. If -1, will load all into memory
        success_only (bool): whether to skip trajectories that are not successful in the end. Default is false
        device: The location to save data to. If None will store as numpy (the default), otherwise will move data to that device
    """

    def __init__(self, dataset_file: str, load_count=-1, success_only: bool = False, device = None) -> None:
        self.dataset_file = dataset_file
        self.device = device
        self.data = h5py.File(dataset_file, "r")
        json_path = dataset_file.replace(".h5", ".json")
        self.json_data = load_json(json_path)
        self.episodes = self.json_data["episodes"]
        self.env_info = self.json_data["env_info"]
        self.env_id = self.env_info["env_id"]
        self.env_kwargs = self.env_info["env_kwargs"]

        self.obs = []
        self.actions = []
        self.terminated = []
        self.truncated = []
        self.success, self.fail, self.rewards = None, None, None
        if load_count == -1:
            load_count = len(self.episodes)

        for eps_id in tqdm(range(load_count)):
            eps = self.episodes[eps_id]
            if success_only: 
                assert "success" in eps, "episodes in this dataset do not have the success attribute, cannot load dataset with success_only=True"
                if not eps["success"]:
                    continue

            # pdb.set_trace()
            trajectory = self.data[f"traj_{eps['episode_id']}"]
            trajectory = load_h5_data(trajectory)
            eps_len = len(trajectory["actions"])
            
            # exclude the final observation as most learning workflows do not use it
            obs = common.index_dict_array(trajectory["obs"], slice(eps_len))
            self.obs = common.append_dict_array(self.obs, [obs])

            self.actions.append(trajectory["actions"])
            self.terminated.append(trajectory["terminated"])
            self.truncated.append(trajectory["truncated"])

            # handle data that might optionally be in the trajectory
            if "rewards" in trajectory:
                if self.rewards is None:
                    self.rewards = [trajectory["rewards"]]
                else:
                    self.rewards.append(trajectory["rewards"])
            if "success" in trajectory:
                if self.success is None:
                    self.success = [trajectory["success"]]
                else:
                    self.success.append(trajectory["success"])
            if "fail" in trajectory:
                if self.fail is None:
                    self.fail = [trajectory["fail"]]
                else:
                    self.fail.append(trajectory["fail"])

        # Specially, we maintain the gap between different episodes, which is useful for some learning algorithms
        # self.actions = np.vstack(self.actions)
        # self.terminated = np.concatenate(self.terminated)
        # self.truncated = np.concatenate(self.truncated)
        
        # if self.rewards is not None:
        #     self.rewards = np.concatenate(self.rewards)
        # if self.success is not None:
        #     self.success = np.concatenate(self.success)
        # if self.fail is not None:
        #     self.fail = np.concatenate(self.fail)

        def remove_np_uint16(x: Union[np.ndarray, dict]):
            if isinstance(x, dict):
                for k in x.keys():
                    x[k] = remove_np_uint16(x[k])
                return x
            else:
                if x.dtype == np.uint16:
                    return x.astype(np.int32)
                return x
        
        # uint16 dtype is used to conserve disk space and memory
        # you can optimize this dataset code to keep it as uint16 and process that
        # dtype of data yourself. for simplicity we simply cast to a int32 so
        # it can automatically be converted to torch tensors without complaint
        # self.obs = remove_np_uint16(self.obs)

        if device is not None:
            self.actions = sapien_utils.to_tensor(self.actions, device=device)
            self.obs = sapien_utils.to_tensor(self.obs, device=device)
            self.terminated = sapien_utils.to_tensor(self.terminated, device=device)
            self.truncated = sapien_utils.to_tensor(self.truncated, device=device)
            if self.rewards is not None:
                self.rewards = sapien_utils.to_tensor(self.rewards, device=device)
            if self.success is not None:
                self.success = sapien_utils.to_tensor(self.terminated, device=device)
            if self.fail is not None:
                self.fail = sapien_utils.to_tensor(self.truncated, device=device)

    def __len__(self):
        return len(self.actions)

    def __getitem__(self, idx):

        # pdb.set_trace()
        action = self.actions[idx]
        obs = common.index_dict_array(self.obs, idx, inplace=False)
        # print("trajectory", obs["sensor_data"]["base_camera"]["rgb"].shape)

        res = dict(
            obs=obs,
            action=action,
            terminated=self.terminated[idx],
            truncated=self.truncated[idx],
        )
        if self.rewards is not None:
            res.update(reward=self.rewards[idx])
        if self.success is not None:
            res.update(success=self.success[idx][-1])
        if self.fail is not None:
            res.update(fail=self.fail[idx][-1])
        if isinstance(action, dict):
           for k in action.keys():
                res.update({f"len_of_action_{k}": len(action[k])})
        else:
            res.update(len_of_action=len(action))
        res.update(
            len_of_success=len(self.success),
        )
        return res

if __name__ == "__main__":
    load_num = 10
    dataset = ManiSkillTrajectoryDataset(dataset_file="/home/ubuntu/kl_workspace/data/StrikeCube.h5", load_count=load_num)
    print("--DEBUG--")
    tot = 0
    camera_name = ['head_camera']
    for i in range(load_num):
        res = dataset.__getitem__(i)
        if load_num < 10:
            print(res.keys())
            print(res["obs"].keys())
            print("len of action", len(res["action"]))
            # pdb.set_trace()
            # print("action example", res["action"][0], res["action"][1], res["action"][2], res["action"][3], res["action"][4], res["action"][5])
            # print("obs sensor param keys", res["obs"]["sensor_param"].keys())
            # print("obs sensor base camera param keys", res["obs"]["sensor_param"]["base_camera"].keys())
            # print("obs sensor base camera intrinsic", res["obs"]["sensor_param"]["base_camera"]["intrinsic_cv"][0])
            # print("obs sensor base camera extrinsic", res["obs"]["sensor_param"]["base_camera"]["extrinsic_cv"][0])
            # print("obs sensor base camera cam2world", res["obs"]["sensor_param"]["base_camera"]["cam2world_gl"][0])
            # print("obs sensor data keys-data", res["obs"]["sensor_data"].keys())
            # print("obs Camera_BEV sensor data keys-data", res["obs"]["sensor_data"]["Camera_BEV"].keys())
            # print("obs sensor data keys-agent", res["obs"]["agent"].keys())
            # print("obs sensor data keys-extra", res["obs"]["extra"].keys())
            # print("obs Camera_BEV sensor data rgb size", res["obs"]["sensor_data"]["head_camera"]["rgb"].shape)
            # print("obs Camera_BEV sensor data depth size", res["obs"]["sensor_data"]["Camera_BEV"]["depth"].shape)
            # print("obs Camera_BEV sensor data depth example:", res["obs"]["sensor_data"]["Camera_BEV"]["depth"][0])
            # print("obs Camera_BEV sensor data segmentation size", res["obs"]["sensor_data"]["Camera_BEV"]["segmentation"].shape)
            # print("obs Camera_BEV sensor data segmentation th example:", res["obs"]["sensor_data"]["Camera_BEV"]["segmentation"][0])
            # print("obs sensor data rgb length", len(res["obs"]["sensor_data"]["base_camera"]["rgb"]))
            # tot += len(res["action"])
            continue
        # make .pkl file for every step
        base_dir = "/home/ubuntu/kl_workspace/data/StrikeCube"
        # for every episode, make a dir to save the episode data
        episode_dir = f"{base_dir}/episode{i}"
        os.makedirs(episode_dir, exist_ok=True)
        for j in range(len(res["action"])):
            obs_dict = {}
            obs_dict["head_camera"] = {}
            obs_dict["head_camera"]["rgb"] = res["obs"]["sensor_data"]["head_camera"]["rgb"][j]
            obs_dict["head_camera"]["intrinsic_cv"] = res["obs"]["sensor_param"]["head_camera"]["intrinsic_cv"][j]
            obs_dict["head_camera"]["extrinsic_cv"] = res["obs"]["sensor_param"]["head_camera"]["extrinsic_cv"][j]
            obs_dict["head_camera"]["cam2world_gl"] = res["obs"]["sensor_param"]["head_camera"]["cam2world_gl"][j]
            step_data = dict(
                pointcloud=None,
                joint_action=res["action"][j],
                endpose=res["action"][j],
                observation=obs_dict,
            )
            with open(f"{episode_dir}/{j}.pkl", "wb") as f:
                pickle.dump(step_data, f)
    # print("total action length", tot)
