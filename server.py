import threading                   #import
import socket


Client_list = {}                   #Creating the list of registered clients
port = 5500                        #Assign the Port number
server = socket.socket()           #Creating the socket
server.bind(('localhost',port))
server.listen()                    
print('Server is waiting...')

#Function to forward msgs to receiver
def fwd_svr(rcvr_snd, message,username,Client_list,sock):         
    msg_fwd = 'Send {}\nContent-length: {}\n\n{}'.format(username,len(message),message)
    frwd_sock = Client_list[rcvr_snd]
    error103='ERROR 103 Header Incomplete\n\n'


    try:
        frwd_sock.send(bytes(msg_fwd,'utf-8'))        #Forwarding to the receiver 
    except:
        response = 'ERROR 102 Unable to send\n\n'
        sock.send(bytes(response,'utf-8'))
        print('ERROR 102  Unable to Send  Message')

    try:
        recv_resp = frwd_sock.recv(2048).decode()     #receving the response from receiver
    except:
        response = 'ERROR 102 Unable to send\n\n'
        sock.send(bytes(response,'utf-8'))
        print('ERROR 102  Unable to Send')


    if recv_resp == 'RECEIVED {}\n\n'.format(username):  #checking received msg for transfering to other client
        sock.send(bytes('SEND '+rcvr_snd+'\n\n','utf-8'))
        print('Message successfully forwarded from {} to {}'.format(username,rcvr_snd))
        return recv_resp


    elif recv_resp == error103:           #checking for Error 103 
        response = error103
        sock.send(bytes(response,'utf-8'))
        sock.close()
        print('ERROR 103  Incomplete Header')
        del Client_list[username]
        return recv_resp

#Function for registering the Clients
def Register(head,sock):
    temp = head.split('\n')         #splitting the message as per \n 
    m = temp         
    m = m[0].split(' ')             #splitting by spaces
    reg = m[0]
    to = m[1]
    username = m[2]                 # storing username
    numalp = m[2].isalnum()
    leng = len(m)
    check = 0 
    
    if reg == 'REGISTER' and to=='TOSEND' and numalp:
        username = m[2]
        cli_response = 'REGISTERED TOSEND {}\n\n'.format(username)
        print('{} : REGISTERED TOSEND '.format(username))
        check = 1
          

    elif reg=='REGISTER' and to=='TORECV' and numalp:
        Client_list[username] = sock
        cli_response = 'REGISTERED TORECV {}\n\n'.format(username)
        print('{} : REGISTERED TORECV '.format(username)) 
      

    elif leng>2 and not numalp:
        cli_response = 'ERROR 100 Malformed username\n\n'
        print('ERROR 100 : Malformed username : ' + username )

    else:
        cli_response = 'ERROR 101 No user registered\n\n'
        print('ERROR 101 : No user registered')
    return check, username, cli_response



#Function for forwarding to receiver for broadcast messages
def brd_svr(rcvr_snd,clint, message,username,Client_list,sock):

    msg_fwd = 'Send {}\nContent-length: {}\n\n{}'.format(username,len(message),message)
    error='ERROR 103 Header Incomplete\n\n'
    frwd_sock = Client_list[clint]
    p = 'RECEIVED {}\n\n'.format(username)
                                        

    try:
        frwd_sock.send(bytes(msg_fwd,'utf-8'))             #forward to receiver
    except:
        response = 'ERROR 102 Unable to send\n\n'
        sock.send(bytes(response,'utf-8'))
        print('ERROR 102 : Unable to Send : Message not delivered from {} to {}'.format(username,clint))
                        

    try:
        recv_resp = frwd_sock.recv(2048).decode()           #response from receiver
    except:                 
        response = 'ERROR 102 Unable to send\n\n'
        sock.send(bytes(response,'utf-8'))
        print('ERROR 102 Unable to Send')
                

    if recv_resp == p:                                     #storing the response
        response = 'SEND '+rcvr_snd+'\n\n'
        
                        

    elif recv_resp == error:                                #checking for error
            response = error
            sock.send(bytes(response,'utf-8'))
            sock.close()
            print('ERROR 103  Incomplete Header')
            del Client_list[username]
    return response
                            



def Implementation(sock):
    try:
        head = sock.recv(2048).decode()
    except:

        sock.close()
        print('Client is not active')
        return 

    check, username, cli_response = Register(head,sock)   #Registering the clients
    
    sock.send(bytes(cli_response,'utf-8'))    #sending the respose for registration to client
    
    if not check:
        return
    
    while 1:
        try:
            mess = sock.recv(2048).decode()     #Server receiving the message
        except:
            print('Client Inactive')
            break

        temp = mess.split('\n')
        mg = temp
        Invld_frm = 0
        mg_0 = temp[0].split(' ')
        rcvr_snd = mg_0[1]
        message = mg[3]

        if  rcvr_snd == '' or message == '':
            Invld_frm = 1

        #Server parsing the messages sent by clients

        if Invld_frm == 1:                            #checking for correct format of message
            response = 'ERROR 103 Header Incomplete\n\n'
            sock.send(bytes(response,'utf-8'))
            print('ERROR 103 : Incomplete Header')
            sock.close()
            del Client_list[username]
            break
        
        else:
            if rcvr_snd in Client_list.keys():                                  #checking if client is in the list
                recv_resp = fwd_svr(rcvr_snd, message,username,Client_list,sock)
                if recv_resp == 'ERROR 103 Header Incomplete\n\n':
                    break
                
            elif rcvr_snd == 'ALL' and len(Client_list)>1:    #checking for broadcast msgs
                for clint in Client_list:
                    if clint != username:
                        response = brd_svr(rcvr_snd,clint, message,username,Client_list,sock)

                        if response == 'ERROR 103 Header Incomplete\n\n':
                            break
                            
                
                if response == 'SEND {}\n\n'.format(rcvr_snd):            
                    sock.send(bytes(response,'utf-8'))                      #sending the response to client
                    print('Message forwarded from {} to {}'.format(username,'ALL'))

            else:
                response = 'ERROR 102 Unable to send\n\n'
                sock.send(bytes(response,'utf-8'))                          #sending the response to client
                print('ERROR 102 Unable to Send')                         

while 1:
    client,adrs = server.accept()
    thrd = threading.Thread(target=Implementation,args=(client,))
    thrd.start()





























