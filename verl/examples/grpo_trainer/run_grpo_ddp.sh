#!/bin/bash

set -x

ENGINE=${1:-vllm}
NODE_RANK=${2:-0}
MASTER_ADDR=192.18.134.158
MASTER_PORT=29500
NGPUS=8
NNODES=2
WORLD_SIZE=$((NGPUS * NNODES))

export VLLM_ATTENTION_BACKEND=XFORMERS
export MASTER_ADDR=${MASTER_ADDR}
export MASTER_PORT=${MASTER_PORT}
export WORLD_SIZE=${WORLD_SIZE}
export RANK=$((NODE_RANK * NGPUS))

python3 -m verl.trainer.main_ppo \
    algorithm.adv_estimator=grpo \
    data.train_files=path/train.parquet \
    data.val_files=path/test.parquet \
    data.train_batch_size=256 \
    data.max_prompt_length=4096 \
    data.max_response_length=2048 \
    data.filter_overlong_prompts=True \
    data.truncation='error' \
    data.image_key=images \
    actor_rollout_ref.model.path=path/Qwen2.5-VL-7B-Instruct \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=128 \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=5 \
    actor_rollout_ref.actor.use_kl_loss=True \
    actor_rollout_ref.actor.kl_loss_coef=0.01 \
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \
    actor_rollout_ref.actor.entropy_coeff=0 \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.fsdp_config.param_offload=False \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=False \
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=10 \
    actor_rollout_ref.rollout.tensor_model_parallel_size=2 \
    actor_rollout_ref.rollout.name=$ENGINE \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.6 \
    actor_rollout_ref.rollout.enable_chunked_prefill=False \
    actor_rollout_ref.rollout.enforce_eager=False \
    actor_rollout_ref.rollout.free_cache_engine=False \
    actor_rollout_ref.rollout.n=5 \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=10 \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    algorithm.use_kl_in_reward=False \
    trainer.critic_warmup=0 \
    trainer.logger=['console','wandb'] \
    trainer.project_name='verl_grpo_example_viki_1' \
    trainer.experiment_name='qwen2_5_vl_7b_function_rm' \
    trainer.default_local_dir='path/checkpoints/verl_grpo_example_viki_1/qwen2_5_vl_7b_function_rm' \
    trainer.n_gpus_per_node=8 \
    trainer.nnodes=2 \
    trainer.save_freq=5 \
    trainer.test_freq=5 \
    trainer.total_epochs=15
