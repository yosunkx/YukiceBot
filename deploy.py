import os
import shutil
import subprocess


def delete_pycache(dir_path):
    for root, dirs, files in os.walk(dir_path):
        if "__pycache__" in dirs:
            shutil.rmtree(os.path.join(root, "__pycache__"))


def copy_project_files(src, dest):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dest, item)
        if os.path.isdir(s):
            if item not in ["current", "memory", ".git", ".vs"]:
                shutil.copytree(s, d, ignore=shutil.ignore_patterns("__pycache__"))
        elif os.path.isfile(s) and item not in ["deploy.py"]:
            shutil.copy2(s, d)


def delete_contents_except_memory(folder):
    for item in os.listdir(folder):
        path = os.path.join(folder, item)
        if item != "memory":
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)


def main():
    project_root = os.path.dirname(os.path.realpath(__file__))
    current_folder = os.path.join(project_root, "current")
    memory_folder = os.path.join(current_folder, "memory")

    # Delete all __pycache__ folders
    delete_pycache(project_root)

    # Delete everything inside 'current' folder except 'memory' folder
    delete_contents_except_memory(current_folder)

    # Copy project files to 'current' folder excluding the memory folder, current folder, and deploy.py
    copy_project_files(project_root, current_folder)

    # Run MeiBotMain.py inside the 'current' folder
    meibot_main = os.path.join(current_folder, "MeiBotMain.py")
    os.chdir(current_folder)  # Change the working directory to the 'current' folder
    subprocess.run(["python", meibot_main])


if __name__ == "__main__":
    main()
