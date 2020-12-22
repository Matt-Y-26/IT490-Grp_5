import pika
import time
import os
import psycopg2
import logging
import json


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

#postgres_user = 'postgres'
#postgres_password = 'example'
#conn = psycopg2.connect(
#   host='db, db2',
#    database='users',
#    user=postgres_user,
#    password=postgres_password
#)

#Updated connect with the db
logging.info("Connecting to read only db")
postgres_password = os.environ['POSTGRES_PASSWORD']
conn_r = psycopg2.connect(
    host='db-r',
    database='example',
    user='postgres',
    password='changeme'
    )
    
logging.info("Connecting to read-write db")
postgres_password = os.environ['POSTGRES_PASSWORD']
conn_rw = psycopg2.connect(
    host='db-rw',
    database='example',
    user='postgres',
    password='changeme'
    )
    
print(' [*] Waiting for DB queries.')
print(' [*] Waiting for messages.')




curr_r = conn_r.cursor()
curr_rw = conn_rw.cursor()
#curr = conn.cursor()
channel = connection.channel()

#WORKS!!
username='ex'
hashed='ex'
# THIS WAS FOR MILESTONE 3 EXAMPLE SHOWING IT CAN COMMUNICATE
#curr.execute('INSERT INTO users VALUES (%s, %s);', ('exuser', 'exhash'))
#conn.commit()
#curr.execute('SELECT hashed FROM users WHERE username=%s;', ('exuser',))
#data = curr.fetchone()
#print (data)
#curr.execute('INSERT INTO users VALUES ("exuser", "exhash"))
#curr.execute('SELECT hash FROM users WHERE username="exuser")
#print(' sql statements executed ' )



#get it
#def get_h(data):
#    username = data['username']
#    logging.info(f"GETHASH request for {username} received")
#    cursor.execute('SELECT hashed FROM usersinfo WHERE username=%s;', (username,))
#    datab = cursor.fetchone()
#    if datab is None:
#        response = {'success': False}
#    else:
#        response = {'success': True, 'hashed': row[0]}
#    return response
    
    
    

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
            username = data['username']
            logging.info(f"GETHASH request for {username} received")
            curr_r.execute('SELECT hashed FROM users WHERE username=%s;', (username,))
            row =  curr_r.fetchone()
            if row == None:
                response = {'success': False}
            else:
                response = {'success': True, 'hashed': row[0]}
        elif action == 'REGISTER':
            data = request['data']
            username = data['username']
            hashed = data['hashed']
            logging.info(f"REGISTER request for {username} received")
            curr_r.execute('SELECT * FROM users WHERE username=%s;', (username,))
            if curr_r.fetchone() != None:
                response = {'success': False, 'message': 'User already exists'}
            else:
                curr_rw.execute('INSERT INTO users VALUES (%s, %s);', (username, hashed))
                curr_rw.commit()
                response = {'success': True}
        else:
            response = {'success': False, 'message': "Unknown action"}
    logging.info(response)
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        body=json.dumps(response)
    )
    
channel.queue_declare(queue='request')

channel.basic_consume(queue='request', auto_ack=True,
                      on_message_callback=process_request)

# loops forever consuming from 'request' queue
logging.info("Starting consumption...")
channel.start_consuming()