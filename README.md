Doxie Automator


This python service automatically retrieves scans on your Doxie Go or Doxie Q, converts them to OCR-enabled PDF, and uploads them to your python storage endpoint.

This application is just a prototype at this point, and doesn't have any GUI. But you *can* run this application through a terminal if helpful. 

Feel free to add bugs or feature suggestions in the "issues" section.

To run:

0) Ensure you have virtualenv and pip installed

1) Clone this repository

3) Rename example.env to .env and update the DOXIE_USERNAME, DOXIE_PASSWORD and DOXIE_FOLDER

4) Create a virtual environment and install requirements with pip

5) Run "python main.py" 


TODO:
1. Determine if given an image, it is a document, photo or drawing.
2. Determine if given two or more sequential images, if they should be grouped together as a PDF
3. Detect text on an image:
3a. Given a whole set of documents, suggest the file keywords
3b. Given a whole set of documents, suggest categories for them to be grouped in
3c. Make a best guess at what the filename should be

 