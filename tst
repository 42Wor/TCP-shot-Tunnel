#!/bin/bash

TOOL_NAME="tst"
PYTHON_SCRIPT="tst.py"
INSTALL_DIR="/usr/local/bin"  # Common directory for user executables

usage() {
  echo "Usage: $TOOL_NAME <command> [options]"
  echo ""
  echo "Commands:"
  echo "  install   Install the $TOOL_NAME command-line tool."
  echo "  <port>    Run the tst service, using <port> for TCP connection."
  echo "  help      Show this help message."
  echo ""
  echo "Example:"
  echo "  $TOOL_NAME install"
  echo "  $TOOL_NAME 9999"
}

install_tool() {
  if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found in PATH."
    echo "Please install Python 3 to use $TOOL_NAME."
    return 1
  fi

  if ! [ -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script '$PYTHON_SCRIPT' not found in the current directory."
    echo "Make sure '$PYTHON_SCRIPT' is in the same directory as the '$TOOL_NAME' script."
    return 1
  fi

  echo "Installing $TOOL_NAME to $INSTALL_DIR..."
  sudo cp "$PYTHON_SCRIPT" "$INSTALL_DIR/$TOOL_NAME"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to copy '$PYTHON_SCRIPT' to '$INSTALL_DIR/$TOOL_NAME'."
    echo "Please run the install command with sudo if necessary."
    return 1
  fi
  sudo chmod +x "$INSTALL_DIR/$TOOL_NAME"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to make '$INSTALL_DIR/$TOOL_NAME' executable."
    return 1
  fi

  echo "$TOOL_NAME installed successfully to $INSTALL_DIR"
  return 0
}

run_tst() {
  local tcp_port="$1"

  if [[ -z "$tcp_port" ]] || ! [[ "$tcp_port" =~ ^[0-9]+$ ]]; then
    usage
    echo "Error: You must provide a valid TCP port number."
    return 1
  fi

  if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found in PATH."
    echo "Please install Python 3 to use $TOOL_NAME."
    return 1
  fi

  if ! [ -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python script '$PYTHON_SCRIPT' not found in the current directory."
    echo "Make sure '$PYTHON_SCRIPT' is in the same directory as the '$TOOL_NAME' script."
    return 1
  fi

  echo "Starting $TOOL_NAME service with TCP port: $tcp_port..."
  python3 "$PYTHON_SCRIPT" "$tcp_port"
}

# --- Main Script Logic ---

case "$1" in
  install)
    install_tool
    ;;
  help)
    usage
    ;;
  "")
    usage
    ;;
  *) # Assume it's a port number if not 'install' or 'help'
    run_tst "$1"
    ;;
esac

exit 0