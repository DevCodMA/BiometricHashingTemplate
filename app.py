import os
import otp_generator
import main
import sqlite3
from flask import Flask, render_template, request, jsonify
import secrets

otp = []
setcount = 0
emailid = ""
fullname = ""
app = Flask(__name__, static_url_path='/static')
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/loginpage')
def loginpage():
    return render_template('face-recognition.html')

@app.route('/registerpage')
def registerpage():
    return render_template('Registration.html')

@app.route('/submit', methods=['POST'])
def submit():
    global otp
    global emailid
    global fullname
    global setcount
    if request.method == 'POST':
        phone_number = request.form['phoneno']
        image_data = request.form['image_data']
        if setcount == 0:
            resd = main.recognize_face(image_data, phone_number)
            if resd[0]:
                conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "user_information.db"))
                res = conn.execute(f"SELECT FULLNAME, EMAILID FROM USER_INFORMATION WHERE PHONENO='{phone_number}'").fetchone()
                fullname = res[0]
                emailid = res[1]
                otp.append(str(otp_generator.generate(phone_number)))
                setcount = 1
                return render_template('otp_validate.html')
            elif resd[1] == 2:
                return render_template('face-recognition.html', message="Multiple Face Detected!")
            elif resd[1] == 3:
                return render_template('face-recognition.html', message="No Face Detected!")
            elif resd[0] == False:
                return render_template('face-recognition.html', message="No such a user!")
    else:
        return jsonify({'success': False, 'message': 'Invalid HTTP method!'})

@app.route('/verifyOTP', methods=['POST'])
def verifyotp():
    if request.method == 'POST':
        global setcount
        setcount = 0
        totp = request.form['totp']
        val = request.form['valx']
        if (int(val) == 1) and (str(totp) in otp):
            return render_template("success.html", name=fullname)
        else:
            return jsonify({'success': False, 'message': 'Login Failed!'})

@app.route('/registeruser', methods=['POST'])
def registeruser():
    if request.method == 'POST':
        name = request.form['fullname']
        emailid = request.form['emailid']
        phoneno = request.form['phoneno']
        accno = request.form['accno']
        img = request.form['image-data']
        retval = main.register(name, emailid, accno, phoneno, img)
        return render_template('Registration.html', message=f"{retval}")

if __name__ == '__main__':
    app.run(debug=True)