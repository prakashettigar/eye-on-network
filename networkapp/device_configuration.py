import paramiko
import os.path
import time
import sys
import re

#Open SSHv2 connection to the device
device_output={}
def ssh_connection(ip,username,password,command):
    #Creating SSH CONNECTION
    global device_output
    try:  
        #Logging into device
        session = paramiko.SSHClient()
        
        #For testing purposes, this allows auto-accepting unknown host keys
        #Do not use in production! The default would be RejectPolicy
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        #Connect to the device using username and password          
        session.connect(ip, username = username, password = password)
        
        #Start an interactive shell session on the router
        connection = session.invoke_shell()	
        
        #Setting terminal length for entire output - disable pagination
        connection.send("enable\n")
        connection.send("terminal length 0\n")
        time.sleep(1)
        
        #Entering global config mode
        connection.send("\n")
        connection.send("configure terminal\n")
        time.sleep(1)
        

        
        #Writing each line in the file to the device
        #for each_line in selected_cmd_file.readlines():
               #Writing each line in the file to the device
        #for each_line in selected_cmd_file.readlines():
        #    connection.send(each_line + '\n')
        #    time.sleep(2)

        #Closing the user file
        #selected_user_file.close()
        
        #Closing the command file
        #selected_cmd_file.close()
        
        #Checking command output for IOS syntax errors
        router_output = connection.recv(65535)
        
        if re.search(b"% Invalid input", router_output):
            print("* There was at least one IOS syntax error on device {} :(".format(ip))
            
        else:
            print("\nDONE for device {} :)\n".format(ip))
            
        #Test for reading command output
        print(str(router_output) + "\n")
        
        #Closing the connection
        session.close()


        connection.send(command + '\n')
        time.sleep(2)
        
        #Checking command output for IOS syntax errors
        router_output = connection.recv(65535)
        
        if re.search(b"% Invalid input", router_output):
            print("* There was at least one IOS syntax error on device {} :(".format(ip))
        else:
            router_output = str(router_output).replace('\\r\\n', '<br>')
            index=router_output.index(command)
            device_output.update({ip: router_output[index+len(command):len(router_output)]})
            print("\nDONE for device {} :)\n".format(ip))
            
        #Test for reading command output
        print(str(router_output) + "\n")
        
        #Closing the connection
        session.close()
     
    except paramiko.AuthenticationException:
        print("* Invalid username or password :( \n* Please check the username/password file or the device configuration.")
        print("* Closing program... Bye!")
