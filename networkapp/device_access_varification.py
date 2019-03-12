import threading
import paramiko

class DEVICE_ACCESS_VERIFICATION:
    dav_res={}

    def dav(self,ip,username,password):
        #Creating SSH CONNECTION
        try:  
            #Logging into device
            session = paramiko.SSHClient()
            #For testing purposes, this allows auto-accepting unknown host keys
            #Do not use in production! The default would be RejectPolicy
            session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #Connect to the device using username and password          
            session.connect(ip, username = username, password = password)
            self.dav_res.update({ip: "success"})
            #Closing the connection
            session.close()
        except paramiko.AuthenticationException:
            print("* Invalid username or password :( \n* Please check the username/password file or the device configuration.",ip)
            self.dav_res.update({ip: "failed"})

    def verifydav(self,ip_list,username_list,password_list):
        dav_threads = []
        i=0
        for ip in ip_list:
            davth = threading.Thread(target = self.dav, args = (ip,username_list[i],password_list[i]))   #args is a tuple with a single element
            davth.start()
            dav_threads.append(davth)
            i=i+1
            
        for davth in dav_threads:
            davth.join()
