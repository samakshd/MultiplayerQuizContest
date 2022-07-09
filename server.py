from database import *
import socket
import select
import time
import random

#Creating a server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#Binding the socket to the given host and port
HOST = "127.0.0.1"
PORT=9999

server_socket.bind((HOST,PORT))

print("Server Started At IP '127.0.0.1' and Port number " + str(PORT))
print("Waiting For Client Connections........")
#Listening for Connections...
server_socket.listen(3)	

client_list=[]	#List to store all Client Objects
address_list=[]	#List to store all Client IP Addresses and Port Numbers

score=[0,0,0]	#List to maintain Scores of each player

#Funtion To Generate Random Sequence of Numbers
def Question_Seq_Generator():

	list=[]
	for i in range(50):
		r=random.randint(0,49)
		if r not in list:
			list.append(r)

	return list

#Function to keep Check of scores of players which returns '1' if Any player is at or above 5 points to end Quiz
def CheckScore():

	for s in score:
		if s >= 5:
			return 1

	return 0

#Function to Get Player ID of a Client Object
def get_client_id(client):

	for i,c in enumerate(client_list):
		if c==client:
			return i

#Function To Broadcast Message to every Client
def broadcast(msg):

	for client in client_list:
		client.send(bytes(msg,'utf-8'))

#Function to Broadcast Message to Selective Clients
def custom_broadcast(who_buzzed,msg1,msg2):

	for client in client_list:

			if(client != who_buzzed):
				client.send(bytes(msg1,'utf-8'))
			else:
				client.send(bytes(msg2,'utf-8'))

#Function To Broadcast Player's Score
def send_scores():

	msg="SCORES :\n\n"

	for i,s in enumerate(score):
		msg += "Player " + str(i+1) + "= " + str(s) +"\n" 

	broadcast(msg)
	time.sleep(2.0)

#Main Function To Ask Question To Player
def ask_question(ques,ans):

	broadcast(ques)
	time.sleep(0.1)

	print("Waiting For Response From Players")
	read_socket,_,_ = select.select(client_list,[],[],10)


	if len(read_socket):

		who_buzzed=read_socket[0]
		bzr=who_buzzed.recv(1024)
		who_buzzed_id=get_client_id(who_buzzed)

		acknowledgement=bytes("Y",'utf-8')
		for client in client_list:
			if(client != who_buzzed):
				client.send(acknowledgement)
		time.sleep(0.1)


		response=who_buzzed.recv(1024).decode()

		if(response==ans):


			msg1="\nPlayer gave correct answer. He got 1 point\n"
			msg2="\nCorrect answer. You got 1 point\n"
			custom_broadcast(who_buzzed,msg1,msg2)
			time.sleep(0.1)
			score[who_buzzed_id]+=1.0
			print(msg1)

		else:

			msg1="\nPlayer gave wrong answer. He lost 0.5 points\n"
			msg2="\nOOPS, Wrong answer. You lost 0.5 points\n"
			custom_broadcast(who_buzzed,msg1,msg2)
			time.sleep(0.1)
			score[who_buzzed_id]-=0.5
			print(msg1)


	else:

		acknowledgement="N"
		broadcast(acknowledgement)
		time.sleep(0.1)
		print("Time Limit Exceeded. No One Answered")

	send_scores()

#Function to Start The Quiz that returns Client Object Of Winner
def start_quiz():

	QuestionIndex=Question_Seq_Generator()
	for i in range(50):

		if CheckScore():
			acknowledgement="D"
			broadcast(acknowledgement)
			time.sleep(0.1)
			break
		else:
			acknowledgement="C"
			broadcast(acknowledgement)
			time.sleep(0.1)

		ques = str(i+1) + ". " + QuestionList[QuestionIndex[i]] 
		ans = AnswerList[QuestionIndex[i]]
		
		print("\nDisplaying Question " + str(i+1) + " on client's screen.")
		print("Answer = " + ans)

		ask_question(ques,ans)

	for i in range(len(score)):
		if(score[i]>=5):
			return i+1

#Function To Show Final Results and End all Connections
def end_quiz(player_id):

	if player_id is not None:
		final_result="GAME OVER\nPlayer " + str(player_id) +" won"
	else:
		final_result="GAME OVER\nIt's A TIE"
	broadcast(final_result)
	time.sleep(0.1)
	for client in client_list:
		client.close()


#Accepting Connections from Clients
def Accept_Connections():

	for i in range(3):
			
		client,addr = server_socket.accept()
		print( "CONNECTED WITH IP " + str(addr[0]) + " AND PORT " + str(addr[1]) )
		print("Waiting for " + str(2-i) + " more Players\n" )
		client.send(bytes("\n-----------------WELCOME TO QUIZ CONTEST-----------------------\n\nYou are Player " + str(i+1) + " of 3",'utf-8'))

		client_list.append(client)
		address_list.append(addr)

	time.sleep(0.1)
	print("All Players Are Connected. The Quiz Starts in 3 seconds\n")
	StartMsg="All Players Are Connected. The Quiz Starts in 3 seconds\n\n"
	broadcast(StartMsg)
	time.sleep(3)


if __name__ == '__main__':

	Accept_Connections()
	player_id=start_quiz()
	end_quiz(player_id)
	print("QUIZ OVER !!  Player " + str(player_id) +" Won")

	server_socket.close()









