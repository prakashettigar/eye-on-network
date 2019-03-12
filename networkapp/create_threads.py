import threading

#Creating threads
def create_threads(ip_list,username_list,password_list,command,function):

    threads = []
    i=0
    for ip in ip_list:
        th = threading.Thread(target = function, args = (ip,username_list[i],password_list[i],command))   #args is a tuple with a single element
        th.start()
        threads.append(th)
        i=i+1
        
    for th in threads:
        th.join()