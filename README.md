Doxie Automator

This python script automatically retrieves scans on your Doxie Go or Doxie Q, places them in a directory on your computer.

This application is just a command-line prototype at this point, and doesn't have any GUI. To run this application, you will need to manually run it through the command line. (See instructions below)

Feel free to add bugs or feature suggestions in the "issues" section.

To run:

0) Ensure you have virtualenv and pip installed

1) Clone this repository

3) Rename example.env to .env and update the DOXIE_USERNAME, DOXIE_PASSWORD and DOXIE_FOLDER

4) Create a virtual environment and install requirements with pip

	virtualenv venv
    source venv/bin/activate
    curl https://bootstrap.pypa.io/get-pip.py | python
    pip install -r requirements.txt

5) Run "python main.py" 
