from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


# Configure logging
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

EMAIL_USER = 'sportsmsanskar@gmail.com'
EMAIL_PASS = 'manoj@1234'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
RECIPIENTS = ['2006128@kiit.ac.in', 'sanskarm17@gmail.com']

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = ', '.join(RECIPIENTS)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.set_debuglevel(1)  # Enable debug output for SMTP
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, RECIPIENTS, msg.as_string())
        logging.info("Email sent successfully.")
    except smtplib.SMTPException as e:
        logging.error(f"Failed to send email: {e}")

def save_ticket(data):
    file_path = 'tickets.xlsx'
    new_data = pd.DataFrame([data])
    
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        df = pd.concat([df, new_data], ignore_index=True)
    else:
        df = new_data
    
    df.to_excel(file_path, index=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new_ticket')
def new_ticket():
    return render_template('new_ticket.html')

@app.route('/ticket_info', methods=['GET', 'POST'])
def ticket_info():
    if request.method == 'POST':
        ticket_id = request.form.get('ticket_id')
        if ticket_id:
            try:
                ticket_id = int(ticket_id)
                df = pd.read_excel('tickets.xlsx')
                if ticket_id <= len(df):
                    ticket = df.loc[ticket_id - 1].to_dict()
                    return render_template('ticket_details.html', ticket=ticket)
                else:
                    return f'Ticket ID {ticket_id} not found.'
            except Exception as e:
                return str(e)
    return render_template('ticket_info.html')

@app.route('/close_ticket', methods=['GET', 'POST'])
def close_ticket():
    if request.method == 'POST':
        ticket_id = request.form['ticket_id']
        feedback = request.form['feedback']
        closing_time = request.form['closing_time']
        closing_date = request.form['closing_date']

        try:
            ticket_id = int(ticket_id)
            df = pd.read_excel('tickets.xlsx')
            if ticket_id <= len(df):
                df.at[ticket_id - 1, 'Feedback'] = feedback
                df.at[ticket_id - 1, 'Closing Time'] = closing_time
                df.at[ticket_id - 1, 'Closing Date'] = closing_date
                df.at[ticket_id - 1, 'Status'] = 'Closed'
                df.to_excel('tickets.xlsx', index=False)
                return f'Ticket #{ticket_id} closed successfully!'
            else:
                return f'Ticket ID {ticket_id} not found.'
        except Exception as e:
            return str(e)
    return render_template('close_ticket.html')

@app.route('/submit', methods=['POST'])
def submit():
    issue = request.form['issue']
    reporter = request.form['reporter']
    date_of_coming = request.form['date_of_coming']
    reason = request.form['reason']
    phone_number = request.form['phone_number']
    closing_time = request.form['closing_time']
    
    data = {
        'Issue': issue,
        'Reporter': reporter,
        'Date of Coming': date_of_coming,
        'Reason': reason,
        'Phone Number': phone_number,
        'Status': 'Open'
    }
    
    save_ticket(data)
    
    ticket_id = len(pd.read_excel('tickets.xlsx'))
    subject = f'New Issue Raised: Ticket #{ticket_id}'
    body = (
        f'Issue: {issue}\n'
        f'Reporter: {reporter}\n'
        f'Date of Coming: {date_of_coming}\n'
        f'Reason: {reason}\n'
        f'Phone Number: {phone_number}\n'
        f'Closing Time: {closing_time}\n'
        f'Ticket ID: {ticket_id}'
    )
    
    send_email(subject, body)
    
    return f'Ticket #{ticket_id} created successfully!'

@app.route('/ticket_counts')
def ticket_counts():
    if os.path.exists('tickets.xlsx'):
        df = pd.read_excel('tickets.xlsx')
        open_tickets = len(df[df['Status'] == 'Open'])
        closed_tickets = len(df[df['Status'] == 'Closed'])
    else:
        open_tickets = 0
        closed_tickets = 0
    return jsonify(open=open_tickets, closed=closed_tickets)





@app.route('/total_open_time', methods=['POST'])
def average_open_time():
    date = request.form['date']

    try:
        parsed_date = pd.to_datetime(date, format='%Y-%m-%d').date()
        current_datetime = datetime.now()

        # Load the ticket data
        df = pd.read_excel('tickets.xlsx')
        df['Date of Coming'] = pd.to_datetime(df['Date of Coming'], format='%Y-%m-%d', errors='coerce')
        df['Closing Date'] = pd.to_datetime(df['Closing Date'], format='%Y-%m-%d', errors='coerce')

        total_open_time = 0.0
        open_tickets_count = 0

        for _, row in df.iterrows():
            date_of_coming = row['Date of Coming'].date() if pd.notna(row['Date of Coming']) else None
            closing_date = row['Closing Date'].date() if pd.notna(row['Closing Date']) else None

            if date_of_coming is None:
                continue  # Skip if the date of coming is missing

            if pd.isna(row['Closing Date']):
                if date_of_coming <= parsed_date:
                    if parsed_date == current_datetime.date():
                        # Ticket is still open today, calculate from midnight to current time
                        open_duration = (current_datetime - datetime.combine(parsed_date, datetime.min.time())).total_seconds() / 3600
                    else:
                        # Ticket was open the entire selected date
                        open_duration = 24
                else:
                    open_duration = 0  # Ticket opened after the selected date, no time counted
            elif closing_date == parsed_date:
                # Ticket closed on the selected date, calculate time from midnight to closing time
                closing_time_str = row['Closing Time']
                if closing_time_str:
                    closing_datetime = pd.to_datetime(f"{closing_date.strftime('%Y-%m-%d')} {closing_time_str}")
                    open_duration = (closing_datetime - datetime.combine(parsed_date, datetime.min.time())).total_seconds() / 3600
                else:
                    open_duration = 0  # No closing time available
            elif date_of_coming <= parsed_date and closing_date > parsed_date:
                # Ticket was open the entire selected date (before closing on a later date)
                open_duration = 24
            else:
                open_duration = 0  # Ticket was not open on the selected date

            if open_duration > 0:
                total_open_time += open_duration
                open_tickets_count += 1

        if open_tickets_count > 0:
            average_open_time = total_open_time / open_tickets_count
        else:
            average_open_time = 0  # No tickets were open on the selected date

        return f'Average open time per ticket on {parsed_date}: {average_open_time:.2f} hours'
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD."
    except Exception as e:
        return str(e)




if __name__ == '__main__':
    app.run(debug=True)



