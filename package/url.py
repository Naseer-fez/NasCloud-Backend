import os
import json

def update_frontend_url(workspace_dir):
    config_path = os.path.join(workspace_dir, "config.json")
    env_path = os.path.join(workspace_dir, "Codexplan", ".env")

    if not os.path.exists(config_path):
        print("config.json not found.")
        return

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    except Exception as e:
        print(f"Error reading config.json: {e}")
        return

    frontend_url = config_data.get("URL", "").strip()
    if not frontend_url:
        print("Frontend URL not set in config.")
        return

    # Update .env file
    env_lines = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            env_lines = f.readlines()

    new_env_lines = []
    found_frontend_url = False
    for line in env_lines:
        if line.startswith("VITE_FRONTEND_URL="):
            new_env_lines.append(f"VITE_FRONTEND_URL={frontend_url}\n")
            found_frontend_url = True
        else:
            new_env_lines.append(line)

    if not found_frontend_url:
        new_env_lines.append(f"VITE_FRONTEND_URL={frontend_url}\n")

    try:
        os.makedirs(os.path.dirname(env_path), exist_ok=True)
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(new_env_lines)
        print(f"Successfully updated {env_path} with VITE_FRONTEND_URL={frontend_url}")
    except Exception as e:
        print(f"Error writing to .env: {e}")

if __name__ == "__main__":
    # If run standalone, use parent directory as workspace
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.dirname(current_dir)
    update_frontend_url(workspace_dir)
