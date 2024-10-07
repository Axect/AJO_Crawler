import subprocess
import sys

def run_script(script_name):
    print(f"Running {script_name}...")
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running {script_name}:")
        print(result.stderr)
        sys.exit(1)
    else:
        print(f"{script_name} completed successfully.")
        print(result.stdout)

def main():
    scripts = ["crawling.py", "post_process.py", "render.py"]
    
    for script in scripts:
        run_script(script)
        print("\n" + "="*50 + "\n")

    print("All scripts have been executed successfully.")

if __name__ == "__main__":
    main()
