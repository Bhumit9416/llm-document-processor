import os
import sys
import subprocess
import time

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import dotenv
        import fastapi
        import uvicorn
        import openai
        import pinecone
        import sentence_transformers
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install all dependencies: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not os.path.exists(".env"):
        print(".env file not found. Creating from .env.example...")
        if os.path.exists(".env.example"):
            with open(".env.example", 'r') as example_file:
                example_content = example_file.read()
            
            with open(".env", 'w') as env_file:
                env_file.write(example_content)
            
            print(".env file created. Please update it with your API keys.")
            return False
        else:
            print(".env.example file not found. Please create a .env file with your API keys.")
            return False
    
    # Check for required variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with these variables.")
        return False
    
    return True

def run_app():
    """Run the FastAPI application"""
    try:
        # Check if src/main.py exists
        if not os.path.exists("src/main.py"):
            print("src/main.py not found. Please make sure the application files are in place.")
            return False
        
        # Run the application
        print("Starting the application...")
        subprocess.run([sys.executable, "src/main.py"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running the application: {e}")
        return False
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
        return True

def main():
    """Main function to run the application"""
    print("=== LLM Document Processing System ===")
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check .env file
    if not check_env_file():
        return
    
    # Initialize project structure if needed
    if not os.path.exists("src") or not os.path.exists("src/main.py"):
        print("Project structure not found. Initializing...")
        subprocess.run([sys.executable, "init_project.py"], check=True)
    
    # Run the application
    run_app()

if __name__ == "__main__":
    main()