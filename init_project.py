import os
import sys

def create_directory(path):
    """Create a directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")

def create_file(path, content=""):
    """Create a file with content if it doesn't exist"""
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(content)
        print(f"Created file: {path}")
    else:
        print(f"File already exists: {path}")

def init_project():
    """Initialize the project structure"""
    # Create main directories
    create_directory("src")
    create_directory("src/document_processor")
    create_directory("src/query_parser")
    create_directory("src/retrieval")
    create_directory("src/decision_engine")
    create_directory("src/api")
    create_directory("data")
    create_directory("tests")
    
    # Create __init__.py files
    create_file("src/__init__.py")
    create_file("src/document_processor/__init__.py")
    create_file("src/query_parser/__init__.py")
    create_file("src/retrieval/__init__.py")
    create_file("src/decision_engine/__init__.py")
    create_file("src/api/__init__.py")
    create_file("tests/__init__.py")
    
    # Create .env file from example if it doesn't exist
    if os.path.exists(".env.example") and not os.path.exists(".env"):
        with open(".env.example", 'r') as example_file:
            example_content = example_file.read()
        
        create_file(".env", example_content)
        print("Created .env file from .env.example. Please update it with your API keys.")
    
    print("\nProject initialization complete!")
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Update .env file with your API keys")
    print("3. Run the application: python src/main.py")

if __name__ == "__main__":
    init_project()