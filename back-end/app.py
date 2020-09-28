import pika
import time

time.sleep(20)

print("Back end is running now")
#credentials = pika.PlainCredentials('guest','guest')
#connection = pika.BlockingConnection(
#	pika.ConnectionParameters(
#		host='messaging',
#		credentials=credentials
#	)
#)