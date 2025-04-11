# Curious Context Companion

This project appears to be a machine learning/NLP application with a Flask backend.

## Installation

There are two ways to install the dependencies:

### Option 1: Using Conda (Recommended)

This is the recommended approach as it avoids compilation issues with packages like `hnswlib` and `tokenizers`:

```bash
# Navigate to the src directory
cd src

# Create the conda environment
conda env create -f environment.yml

# Activate the environment
conda activate curious-context
```

### Option 2: Using pip

If you prefer using pip, you'll need to install build dependencies first:

#### For Mac users:

1. Install Xcode Command Line Tools:
```bash
xcode-select --install
```

2. Install Homebrew if not already installed:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

3. Install C++ development tools for hnswlib:
```bash
brew install libomp
```

4. Install Rust compiler for tokenizers:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

5. Install the requirements:
```bash
cd backend
pip install -r requirements.txt
```

#### For Linux users:

1. Install C++ development tools:
```bash
sudo apt-get update
sudo apt-get install build-essential
```

2. Install Rust compiler:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

3. Install the requirements:
```bash
cd backend
pip install -r requirements.txt
```

## Alternatively: Using pip with pre-built wheels

To avoid building from source, you can try installing the problematic packages separately:

```bash
pip install --only-binary=:all: hnswlib tokenizers
pip install -r requirements.txt
```

## Running the Application

To start the backend server:

```bash
# Make sure you're in the backend directory
cd backend

# Run the Flask application
python app.py
```

## Troubleshooting

If you encounter build errors with:
- `hnswlib`: The error `'iostream' file not found` indicates missing C++ headers
- `tokenizers`: The error `can't find Rust compiler` means you need to install Rust

If you've followed the setup instructions and still encounter issues, please follow Option 1 (Conda) as it manages the build environment automatically. 