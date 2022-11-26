import sys
import socket
import threading


port = 5500                              #Assign the Port number
print('Enter username: ',end="")         #taking the useranme as input
username = input()
print('Enter server_IP: ',end="")        #taking the server IP as input
server_IP = input()
Client_send = socket.socket()            #Creating the send socket
Client_send.connect((server_IP,port))
Client_recv = socket.socket()            #Creating the receive socket
Client_recv.connect((server_IP,port))


if username == 'ALL':
    print('ALL is reserved keyword')
    sys.exit()

#Function for server Acknowledgement
def svr_acknd(svr_respns,recvr,error102):
    p = svr_respns
     
    if p == error102:
        print('ERROR 102  Unable to Send')  
    elif p == 'SEND {}\n\n'.format(recvr):
        print('Message successfully sent to {}'.format(recvr))  
    return
    

if username == 'ALL':
    print('ALL is reserved keyword')
    sys.exit()

#function for send socket thread execution
def msg_send(sock):
    while 1:
        msg = input()
        Invld_frm = 0
        i = msg[0]
        j = msg.find(':')
        message =""
        recvr = ""
        
        if i == '@':                     #checking for given format
            recvr = msg[1:j]             #splitting the msg
            message = msg[j+1:]
            if j == -1:
              Invld_frm = 1
            if recvr == '' or message=='':
                Invld_frm = 1
        else:
            Invld_frm = 1

        if recvr == username:                        #check for same username and receiver
            print('Receiver and Username are same person')
            continue

        if Invld_frm:                                 #check for correct format
            print('Invalid format, please use following format:')
            print('@[RECIPIENT NAME]: Message\n')
            continue  
      
        msg_toSnd = 'Send {}\nContent-length: {}\n\n{}'.format(recvr,len(message),message)    #adding header to message
        sock.send(bytes(msg_toSnd,'utf-8'))                                               #sending message to server
        svr_respns = sock.recv(2048).decode() 
        error102 = 'ERROR 102 Unable to send\n\n'                                         #receiving the response from server
        error103 = 'ERROR 103 Header Incomplete\n\n'
       
        svr_acknd(svr_respns,recvr,error102)                                                           #server acknowledgement

        if svr_respns == error103:
            print('ERROR 103 : Incomplete Header : Message not delivered to {}'.format(recvr))
            print('Connection closed by server')
            break
       
    sock.close()
 
#function for receive socket thread execution       
def msg_receive(sock):
    while 1:
        #parsing the message forwarded by the server
        msg = sock.recv(2048).decode() 
        temp = msg.split('\n')
        mg = temp
        Invld_frm = 0
        mg_0 = temp[0].split(' ')
        svr_snd = mg_0[1]
        message = mg[3]
       
        if svr_snd == '' or message == '':
            Invld_frm = 1

     
        if Invld_frm==0:
            response = 'RECEIVED {}\n\n'.format(svr_snd)
            print('{}: {}'.format(svr_snd,message))
                      
        else:
            response = 'ERROR 103 Header Incomplete\n\n'
           
        sock.send(bytes(response,'utf-8'))         #sending response to the server as per the forwarded message
  
    sock.close()

#Function for registration of client
def send_reg_message(username):
    send_reg_message = 'REGISTER TOSEND ' + username + '\n\n'
    try:
        Client_send.send(bytes(send_reg_message,'utf-8'))
    except:
        print('Server is not active')
        sys.exit()
    return

#function for socket generation
def snd_sock_generated(rcv_ack_msg, username):
    p = rcv_ack_msg
    if p == 'REGISTERED TOSEND {}\n\n'.format(username): 
        send_th = threading.Thread(target=msg_send,args=(Client_send,))
        send_th.start()
        print('{} : REGISTERED TOSEND'.format(username))

    elif p == 'ERROR 101 : No user registered\n\n':      #check for error101
        print('ERROR 101 : No user registered')
        print('Exiting...')
        sys.exit()

    else:   
        print('ERROR 100: Malformed Username')           #check for username is malformed
        sys.exit()
    return

#Function for receive socket generation
def rcv_sock_generated(svr_ack_rcv, username):
    p = svr_ack_rcv
    if p == 'ERROR 100 Malformed username\n\n':
        print('ERROR 100 : Malformed Username')
        sys.exit()
        
    elif p =='REGISTERED TORECV {}\n\n'.format(username):
        recv_th = threading.Thread(target=msg_receive,args=(Client_recv,))
        recv_th.start()
        print('{} : REGISTERED TORECV'.format(username))

    else:
        print('ERROR 101')
        sys.exit()


send_reg_message(username)                         #Registration of client to send
rcv_ack_msg = Client_send.recv(2048).decode()      #Acknowledgement message from server
snd_sock_generated(rcv_ack_msg, username)          #socket generated if usename is in correct form

get_reg_msg = 'REGISTER TORECV {}\n\n'.format(username) #Registration of client to receive
Client_recv.send(bytes(get_reg_msg,'utf-8'))           #Request for registration msg send to server  
svr_ack_rcv = Client_recv.recv(2048).decode()          #If acknowledge by server, receive the msg
rcv_sock_generated(svr_ack_rcv, username)              #receive socket generated
