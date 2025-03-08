# TCP-shot-Tunnel
tst command-line tool



Step 3: Make Scripts Executable

In your terminal, navigate to the directory where you saved tst.py and tst, and run the following commands:

chmod +x tst.py
chmod +x tst
Use code with caution.
Bash
This makes both the Python script and the Bash script executable.

Step 4: Install the tst Tool

In the same directory, run the install command:

./tst install
Use code with caution.
Bash
You will likely be prompted for your sudo password because the installation script tries to copy the tst.py script to /usr/local/bin.

Step 5: Run the tst Tool

After successful installation, you should be able to run tst from anywhere in your terminal. Try running it with a port number:

tst 9999
Use code with caution.
Bash
This should start the Python script, and you'll see the logging output as it attempts to connect to a TCP server on port 9999 and starts the HTTP server on port 8000.


chmod +x tst.py
chmod +x tst
./tst install
tst 9999


chmod +x tst
./tst install