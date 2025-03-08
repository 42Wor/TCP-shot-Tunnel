# TCP-shot-Tunnel
tst command-line tool

# tst-cli (or your chosen repository name)

**tst-cli** is a command-line tool that acts as an HTTP to TCP forwarder. It receives HTTP requests and forwards them to a backend TCP server.

## Features

*   Simple command-line interface.
*   Forwards HTTP requests to a specified TCP port.
*   Provides basic status and error output in color (optional).

## Installation

**Prerequisites:**

*   Python 3 must be installed on your system.
*   `curl` (or a similar HTTP client) is useful for testing the HTTP service.

**Installation Steps:**

1.  **Download the `tst` script and `tst.py` files:**
    You can download these files directly from this GitHub repository.

2.  **Make the `tst` script executable:**
    Open your terminal and navigate to the directory where you saved `tst` and `tst.py`.
    Run the command:
    ```bash
    chmod +x tst
    chmod +x tst.py
    ```

3.  **Run the install command:**
    Execute the following command from the same directory to install `tst` system-wide:
    ```bash
    ./tst install
    ```
    You might be prompted for your password as this command installs `tst` to `/usr/local/bin`.

    Alternatively, if you want to install it locally (without `sudo`) you can copy `tst` and `tst.py` to a directory in your `$PATH`, like `~/bin`, and ensure `~/bin` is in your `PATH` environment variable.

## Usage

**Basic Command:**

```bash
tst <TCP_PORT>
```

**Create the Zip File:**
```bash
zip tst-tool.zip tst tst.py
```