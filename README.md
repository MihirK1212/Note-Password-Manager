# Note-Password-Manager
Submission for Programming Club Recruitment 2.0 Dev
Name: Mihir Karandikar
Roll No: 200001044
Branch: Computer Science and Engineering
Year: Second Year

Usage Details:

1) Create a .env file in the Project folder and it should have the following content:<br />

    SENDER_EMAIL = ""<br />
    SENDER_PASSWORD = ""<br />
    VERIFICATION_KEY = ""<br />
    
    These are developer-specific settings for sending 'Confirmation' and 'Recovery' emails. SENDER_EMAIL should contain the email address which will be used to send the emails mentioned. SENDER_PASSWORD stores the password for SENDER_EMAIL. VERIFICATION_KEY is used for email-id confirmation and can be any string of your choice.
    
2) Install all requirements using: ' pip install -r requirements.txt '

3) Run the python script 'app.py'. Now the Flask app can be accessed at http://127.0.0.1:8000/

4) The initial landing page is for Login or Sign Up purposes. For Sign Up, we require UserName and Password. After Signing up, make sure to login and set up a recovery email.

5) After logging in successfully, user can Add and Delete notes. User can also update their recovery email

6) In case user forgets their password, they can click on the 'Forgot Password' button. Then the user will be asked to enter their UserName after whcih the password will be sent to their recovery email.
