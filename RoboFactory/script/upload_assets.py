from huggingface_hub import HfApi

api = HfApi()

repo_id = "FACEONG/VIKI-Assets"

# Create the dataset repo (no-op if already exists)
api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True)

# Upload assets folder
api.upload_folder(
    folder_path="assets",
    repo_id=repo_id,
    repo_type="dataset",
)

print(f"Done! Assets uploaded to https://huggingface.co/datasets/{repo_id}")
