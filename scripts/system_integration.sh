#!/bin/bash

# Install system dependencies
install_dependencies() {
    # Rust
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    
    # Go
    wget https://golang.org/dl/go1.21.0.linux-amd64.tar.gz
    sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
    
    # C++ dependencies
    sudo pacman -S gcc cmake openssl
    
    # Python dependencies
    sudo pacman -S python-pyqt6 python-cryptography python-tqdm
}

# Build components
build_components() {
    # Build Rust library
    cd src/core && cargo build --release
    
    # Build Go binary
    cd src/filesystem && go build -o ../../bin/fs_manager
    
    # Build C++ library
    cd src/hardware && cmake . && make
} 