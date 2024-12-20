### Python Automations of Daily Life

 Steps to run each of the projects:-  <br>
 You can go inside the project folder you want to run, and there will be an index.py file, which is the main file there. <br>
 You can run the command -> python index.py <br> 
 If it doesn't work, then run -> python3 index.py

### Below are the projects

 1. **CSV extractor project**:- In this I have taken a csv file as input and extracted a new csv with lesser columns and rows. I have also plotted a bar chart with the data from new csv. <br>

 2. **Folder cleaner project**:- In this I have taken a folder path which I want to organize. As a part of the script, we will be creating four new folders:- Images, Docs, Audio and Videos. We will also be running the script in an infinite loop and will be watchdogging for any modifications or adding of new files in the folder path. If it does, then the organizeFiles method is triggered to clean the stuff. <br>
 Don't forget to press Ctrl+C when you want to stop the program. <br>

  3. **Email sender project**:- In this I am using mailgun for sending mails. I have set up the mailgun account, and created an API key and used it here. You also have to register the receiving email address in mailgun. Use an .env file for storing the secret variables used in script, which you have got from mailgun. <br>
