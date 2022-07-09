import socket
import select
import sys
import  os
import time
from termios import tcflush, TCIFLUSH

client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST="127.0.0.1"
PORT=9999

client.connect((HOST,PORT))

welcome_msg=client.recv(1024).decode()
print(welcome_msg)

StartMsg=client.recv(1024).decode()
print(StartMsg)
time.sleep(3.0)
os.system('clear')

for i in range(50):

	acknowledgement=client.recv(1024).decode()
	if acknowledgement=="D":
		break

	tcflush(sys.stdin, TCIFLUSH)
	ques=client.recv(1024).decode()
	print(ques)
	print("\nYou Have 10 seconds to Press BUZZER. Press 'ENTER' key as a BUZZER.\n")

	read_socket,_,_=select.select([sys.stdin,client],[],[])


	if read_socket[0]==sys.stdin:

		bzr=bytes(sys.stdin.readline(),'utf-8')
		client.send(bzr)
		
		tcflush(sys.stdin, TCIFLUSH)

		resp = input("You Pressed the buzzer first. Please Select the Option Code as Your Answer :  ")

		if resp not in ["1","2","3","4"]:
			while True:
				resp=input("Please Enter a valid choice :  ")
				if resp in ["1","2","3","4"]:
					break

		client.send(bytes(resp,'utf-8'))

		result=client.recv(1024).decode()
		print(result)

	elif read_socket[0]==client:

		acknowledgement=client.recv(1024).decode()
		if acknowledgement == "Y":

			print("TOO LATE! Other Player Has already buzzed. Waiting for his response...")
			result=client.recv(1024).decode()
			print(result)
			tcflush(sys.stdin, TCIFLUSH)

		elif acknowledgement == "N":
			print("\nTIME UP! You got 0 points\n")

	scores=client.recv(1024).decode()
	print(scores)
	time.sleep(2.0)
	os.system('clear')


print(client.recv(1024).decode())

client.close()
