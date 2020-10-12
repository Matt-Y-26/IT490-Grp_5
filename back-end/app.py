import pika
import time
import os
import psycopg2

# Sleep time for BE to connect


# Connect with Messaging
time.sleep(20)

print("Back end is running now")
credentials = pika.PlainCredentials('guest','guest')
connection = pika.BlockingConnection(
	pika.ConnectionParameters(
		host='messaging',
		credentials=credentials
	)
)

# Connect with DB
print(' [*] Connecting to the database...')
#postgres_user = os.environ['DB_USER']
#postgres_password = os.environ['DB_PASS']
postgres_user = 'postgres'
postgres_password = 'example'
conn = psycopg2.connect(
    host='db',
    database='users',
    user=postgres_user,
    password=postgres_password
)

print(' [*] Waiting for DB queries.')
print(' [*] Waiting for messages.')


def process_request(ch, method, properties, body):
    """
    Gets a request from the queue, acts on it, and returns a response to the
    reply-to queue
    """
    request = json.loads(body)
    if 'action' not in request:
        response = {
            'success': False,
            'message': "Request does not have action"
        }
    else:
        action = request['action']
        if action == 'GETHASH':
            data = request['data']
            email = data['email']
            logging.info(f"GETHASH request for {email} received")
            curr.execute('SELECT hash FROM users WHERE email=%s;', (email,))
            row =  curr.fetchone()
            if row == None:
                response = {'success': False}
            else:
                response = {'success': True, 'hash': row[0]}
        elif action == 'REGISTER':
            data = request['data']
            email = data['email']
            hashed = data['hash']
            logging.info(f"REGISTER request for {email} received")
            curr.execute('SELECT * FROM users WHERE email=%s;', (email,))
            if curr.fetchone() != None:
                response = {'success': False, 'message': 'User already exists'}
            else:
                curr.execute('INSERT INTO users VALUES (%s, %s);', (email, hashed))
                conn.commit()
                response = {'success': True}
        else:
            response = {'success': False, 'message': "Unknown action"}
    logging.info(response)
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        body=json.dumps(response)
    )
