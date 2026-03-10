from huggingface_hub import snapshot_download
import os

snapshot_download(repo_id='FACEONG/VIKI-Assets',
                  local_dir='./assets',
                  repo_type='dataset',
                  resume_download=True)