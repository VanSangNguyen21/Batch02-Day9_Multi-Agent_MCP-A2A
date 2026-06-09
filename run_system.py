import subprocess
import time
import os
import sys

def main():
    env = os.environ.copy()
    # Ensure UTF-8 output encoding for standard streams
    env["PYTHONIOENCODING"] = "utf-8"
    
    # Read the .env values if .env exists
    dotenv_vars = {}
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        k, v = line.split("=", 1)
                        dotenv_vars[k.strip()] = v.strip()
    
    for k, v in dotenv_vars.items():
        env[k] = v

    python_executable = sys.executable
    processes = []
    
    try:
        print("Starting Registry service on port 10000...")
        p_reg = subprocess.Popen([python_executable, "-m", "registry"], env=env)
        processes.append(p_reg)
        time.sleep(4)
        
        print("Starting Tax Agent on port 10102...")
        p_tax = subprocess.Popen([python_executable, "-m", "tax_agent"], env=env)
        processes.append(p_tax)
        
        print("Starting Compliance Agent on port 10103...")
        p_comp = subprocess.Popen([python_executable, "-m", "compliance_agent"], env=env)
        processes.append(p_comp)
        time.sleep(4)
        
        print("Starting Law Agent on port 10101...")
        p_law = subprocess.Popen([python_executable, "-m", "law_agent"], env=env)
        processes.append(p_law)
        time.sleep(4)
        
        print("Starting Customer Agent on port 10100...")
        p_cust = subprocess.Popen([python_executable, "-m", "customer_agent"], env=env)
        processes.append(p_cust)
        time.sleep(10)
        
        print("\nAll services started. Running test_client.py...")
        start_time = time.time()
        
        # Run test_client.py
        result = subprocess.run([python_executable, "test_client.py"], env=env, capture_output=True, text=True, encoding="utf-8")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print("\n" + "="*60)
        print("TEST CLIENT OUTPUT:")
        print("="*60)
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print("="*60)
        print(f"Total latency: {elapsed_time:.2f} seconds")
        print("="*60)
        
    finally:
        print("\nShutting down all processes...")
        for p in processes:
            try:
                p.terminate()
            except Exception as e:
                print(f"Error terminating process: {e}")
        time.sleep(1)
        for p in processes:
            try:
                p.kill()
            except Exception:
                pass
        print("All processes terminated.")

if __name__ == "__main__":
    main()
