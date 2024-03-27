import requests
import os
import logging
import base64
import json
import pymysql

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


def send_email(event, context):

    logger.debug('Received request to send email')

    data = base64.b64decode(event['data']).decode('utf-8')

    json_data = json.loads(data)

    logger.info(json_data)

    post_email_url = f"https://api.mailgun.net/v3/saicheb.me/messages"
    authentication = ("api", os.environ['API_KEY'])
    from_email     = "Cloud Webapp <webapp@saicheb.me>"
    to_email       = json_data.get('email')
    subject        = "Verify your account"
    content        = "please verify your email by clicking this link"
    token          = json_data.get('token')

    try:

        response = requests.post(
            post_email_url,
            auth=authentication,
            data={
                "template":"verify",
                "from":from_email,
                "to": to_email,
                "subject": subject,
                "text": content,
                "h:X-Mailgun-Variables": json.dumps({"first_name": "Cloud Webapp User", "token": token})
            }
        )

        response.raise_for_status()

    except Exception as errorMessage:

        print("Could not send email")
        print(errorMessage)
    
    logger.info('Sent verification email')

    # Connect and modify

    db_user     = os.environ['DB_USER']
    db_password = os.environ['DB_PASSWORD']
    db_host     = os.environ['DB_HOST']
    db_name     = os.environ['DB_NAME']


    try:
        db = pymysql.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            database=db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        logger.info("Database connection Successful")

        cursor = db.cursor()
        update_query = f"UPDATE token SET status='SENT' WHERE token='{token}'"
        cursor.execute(update_query)
        db.commit()
        logger.info('Token status updated to SENT')


    except Exception as e:
        logger.error(f'Error connecting to DB: {e}')
        return