import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Run RoboFactory planner to generate data.")
    parser.add_argument('config', type=str, help="Task config file to use")
    args = parser.parse_args()

    command = (
        f"python -m planner.run "
        f"-c \"{args.config}\" "
        f"--render-mode=\"rgb_array\" "
        f"-b=\"gpu\" "
        f"-n 1"
    )
    print("Running command: ", command)
    os.system(command)

if __name__ == "__main__":
    main()
