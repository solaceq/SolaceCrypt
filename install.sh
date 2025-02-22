#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="SolaceCrypt"
VERSION="1.0"
INSTALL_DIR="/opt/solacecrypt"
BIN_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/share/applications"
ICON_DIR="/usr/share/icons/hicolor"
CONFIG_DIR="/etc/solacecrypt"
DATA_DIR="/usr/share/solacecrypt"

# Function to print status messages
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_error() {
    echo -e "${RED}[-]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root"
    exit 1
fi

# Create necessary directories
print_status "Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$DATA_DIR"
mkdir -p "$DATA_DIR/locale"

# Install system dependencies
print_status "Installing dependencies..."
if command -v pacman &> /dev/null; then
    # Arch Linux
    pacman -S --needed --noconfirm \
        python python-pip python-pyqt6 python-cryptography python-tqdm
elif command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    apt-get update
    apt-get install -y \
        python3 python3-pip python3-pyqt6 python3-cryptography python3-tqdm
elif command -v dnf &> /dev/null; then
    # Fedora
    dnf install -y \
        python3 python3-pip python3-pyqt6 python3-cryptography python3-tqdm
fi

# Install Python dependencies
print_status "Installing Python packages..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Copy application files
print_status "Installing application files..."
cp src/file_encryptor.py "$INSTALL_DIR/"
cp src/file_encryptor_gui.py "$INSTALL_DIR/solacecrypt.py"
cp -r locale "$DATA_DIR/"

# Create main executable
cat > "$BIN_DIR/solacecrypt" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
python3 solacecrypt.py "\$@"
EOF
chmod +x "$BIN_DIR/solacecrypt"

# Generate and install icons
print_status "Installing icons..."
for size in 16 24 32 48 64 96 128 256; do
    mkdir -p "$ICON_DIR/${size}x${size}/apps"
    python3 create_icon.py "$size" "$ICON_DIR/${size}x${size}/apps/solacecrypt.png"
done

# Install desktop entry
print_status "Creating desktop entry..."
cat > "$DESKTOP_DIR/solacecrypt.desktop" << EOF
[Desktop Entry]
Version=$VERSION
Type=Application
Name=SolaceCrypt
GenericName=File Encryption Tool
Comment=Secure File Encryption Tool
Exec=solacecrypt
Icon=solacecrypt
Terminal=false
Categories=Utility;Security;
Keywords=encryption;security;crypto;privacy;
StartupWMClass=SolaceCrypt
EOF

# Set permissions
print_status "Setting permissions..."
chmod 755 "$INSTALL_DIR"
chmod 755 "$BIN_DIR/solacecrypt"
chmod 644 "$DESKTOP_DIR/solacecrypt.desktop"
chmod -R 755 "$DATA_DIR"

# Create uninstall script
cat > "$INSTALL_DIR/uninstall.sh" << EOF
#!/bin/bash
# Uninstall SolaceCrypt
rm -rf "$INSTALL_DIR"
rm -f "$BIN_DIR/solacecrypt"
rm -f "$DESKTOP_DIR/solacecrypt.desktop"
rm -rf "$CONFIG_DIR"
rm -rf "$DATA_DIR"
for size in 16 24 32 48 64 96 128 256; do
    rm -f "$ICON_DIR/\${size}x\${size}/apps/solacecrypt.png"
done
EOF
chmod +x "$INSTALL_DIR/uninstall.sh"

# Update icon cache
print_status "Updating icon cache..."
gtk-update-icon-cache -f -t "$ICON_DIR"

# Create requirements.txt
cat > requirements.txt << EOF
PyQt6>=6.4.0
cryptography>=3.4.7
tqdm>=4.61.0
EOF

print_success "Installation complete!"
echo -e "\nYou can now:"
echo "1. Run 'solacecrypt' from terminal"
echo "2. Launch from application menu"
echo "3. To uninstall, run: sudo $INSTALL_DIR/uninstall.sh"

# Optional: Create first run configuration
if [ ! -f "$CONFIG_DIR/config.json" ]; then
    print_status "Creating initial configuration..."
    mkdir -p "$CONFIG_DIR"
    cat > "$CONFIG_DIR/config.json" << EOF
{
    "version": "$VERSION",
    "first_run": true,
    "theme": "Dark Blue",
    "language": "English (US)",
    "default_output_dir": "~/Encrypted"
}
EOF
fi 