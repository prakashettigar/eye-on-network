from django.shortcuts import render
from networkapp.forms import UserForm, UserProfileInfoForm, DeviceCredentialForm, DeviceCommandForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from networkapp.models import DeviceCommandInfo, DeviceCredentialDetail,CollectionInfo
import numpy as np
import json
import datetime
import os

import networkapp.ssh_connection as sshcon
from networkapp.device_discovery import DEVICEDISCOVERY
from networkapp.ssh_connection import ssh_connection
from networkapp.create_threads import create_threads
from networkapp.device_access_varification import DEVICE_ACCESS_VERIFICATION
# Create your views here.


def index(request):
    urllink=''
    if request.user.is_authenticated:
        urllink='networkapp/home.html'
    else:
        urllink='networkapp/index.html'
    return render(request,urllink)

@login_required(login_url='/accounts/login/')
def dashboard(request):
    return render(request, 'networkapp/dashboard.html')

def getDashboardDetails(request):
    inactivecount=0
    activecount=0
    devicelist=[]
    devicelistArray=[]
    if request.method == 'GET': 
        d = DEVICEDISCOVERY()
        devicelist = DeviceCredentialDetail.objects.values('device_ip')
        for deviceip in devicelist:
            devicelistArray.append(deviceip.get('device_ip'))
        print("requet from ajax : ",devicelistArray)
        d.ping_range(devicelistArray)
        for ip,value in d.ping_res.items():
            print(value)
            if value == "active":
                activecount=activecount+1
            else:
                inactivecount=inactivecount+1
    data = {'inactivecount':inactivecount,'activecount':activecount}
    print(data)
    return HttpResponse(json.dumps(data), content_type="application/json")

@login_required(login_url='/accounts/login/')
def home(request):
    return render(request, 'networkapp/home.html')


@login_required(login_url='/accounts/login/')
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

@login_required(login_url='/accounts/login/')
def register(request):
    registered = False
    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']

            profile.save()
            registered = True
        #else:
            #print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()

    return render(request, 'networkapp/registration.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))
            else:
                return HttpResponse("ACCOUNT NOT ACTIVE")
        else:
             #print("Someone tried to login and failes !")
             #print("Username: {} and password {}".format(username, password))
            return HttpResponse("Invalid Login Details")
    else:
        return render(request, 'networkapp/index.html', {})


@login_required(login_url='/accounts/login/')
def device_discovery(request):
    D = DEVICEDISCOVERY()
    D.ping_res.clear()
    list = []
    if request.method == 'POST':
        fromip = request.POST.get('fromip')
        toip = request.POST.get('toip')
        if fromip == toip:
            list.append(fromip)
        else:
            list = D.ips(fromip, toip)
            list.append(toip)

        print("List of ip : ",list)
        D.ping_range(list)
         #print(D.ping_res)
    return render(request, 'networkapp/device_discovery.html', {'new_dict': D.ping_res, 'activedevice_count': D.activedevice_count, 'inactivedevice_count': D.inactivedevice_count})


@login_required(login_url='/accounts/login/')
def fetch_device_configuration(request):
    sshcon.device_output.clear()
    ip_list = []
    password_list=[]
    username_list=[]
    unrechable_device_list=[]
    rechable_ip_list=[]
    invalid_cred_device_list=[]
    d = DEVICEDISCOVERY()
    dav = DEVICE_ACCESS_VERIFICATION()  

    commandlist = DeviceCommandInfo.objects.all()
    devicelist = DeviceCredentialDetail.objects.values('device_ip')

    if request.method == "POST":
        command = request.POST.get('selcommand')
        deviceip = request.POST.get('seldeviceip')
         
        if deviceip == "all" :
            device_cred_query = DeviceCredentialDetail.objects.all()
             #print(device_cred_query)
            for device_cred in device_cred_query:
                username = device_cred.device_username
                 #print(username)
                username_list.append(username)
                password = device_cred.device_password
                password_list.append(password)
                deviceip = device_cred.device_ip
                ip_list.append(deviceip)
        else:
            ip_list.append(deviceip)
            usernames = DeviceCredentialDetail.objects.values('device_username').filter(device_ip=deviceip)
            passwords = DeviceCredentialDetail.objects.values('device_password').filter(device_ip=deviceip)
            for user in usernames:
                username = user.get('device_username')
                username_list.append(username)
            for user in passwords:
                password = user.get('device_password')
                password_list.append(password)
        
        rechable_ip_list = list(ip_list)
        d.ping_range(ip_list)
        index_list=[]
        for device, value in d.ping_res.items():
            if value == "inactive":
                unrechable_device_list.append(device)
                index_list.append(ip_list.index(device))

        username_list=np.delete(username_list, index_list).tolist()
        password_list=np.delete(password_list, index_list).tolist()
        rechable_ip_list=np.delete(rechable_ip_list, index_list).tolist()

        if len(rechable_ip_list) > 0 :
            dav.verifydav(rechable_ip_list,username_list,password_list)

        dav_index_list=[]
        for device, value in dav.dav_res.items():
            if value == "failed":
                invalid_cred_device_list.append(device)
                dav_index_list.append(ip_list.index(device))

        if len(rechable_ip_list) > 0 :
            username_list=np.delete(username_list, dav_index_list).tolist()
            password_list=np.delete(password_list, dav_index_list).tolist()
            rechable_ip_list=np.delete(rechable_ip_list, dav_index_list).tolist()        
            
            create_threads(rechable_ip_list,username_list,password_list,command,ssh_connection)

        ts = datetime.datetime.now().timestamp()

        try:  
            os.mkdir("data/"+command)
        except OSError:  
            print ("Creation of the directory %s failed")

        for ip,output in sshcon.device_output.items():
            filepath="data/"+command+"/"+ip+"-"+str(ts)+".txt"
            with open(filepath, 'w+') as f:
                f.write(output+'')
                f.flush()
                f.close()
            collection=CollectionInfo(filepath=filepath,created_on=datetime.datetime.now().time())
            collection.save()
            
         #print("invalid cred list :",invalid_cred_device_list)
         #print("unrechable cred list :",unrechable_device_list)

    return render(request, 'networkapp/fetch_device_configuration.html', {'commandlist': commandlist, 'devicelist': devicelist,'commandoutput' : sshcon.device_output,'invalidcredential':invalid_cred_device_list,'unreachabledevice':unrechable_device_list})


@login_required(login_url='/accounts/login/')
def add_device_credential(request):
    result = False
    if request.method == "POST":
        device_credential_form = DeviceCredentialForm(data=request.POST)
        if device_credential_form.is_valid():
            device_details = device_credential_form.save()
            device_details.save()
            result = True
        else:
             #print(device_credential_form.errors)
            result = False
    else:
        device_credential_form = DeviceCredentialForm()
    return render(request, 'networkapp/add_credential.html', {'device_credential_form': device_credential_form, 'result': result})

@login_required(login_url='/accounts/login/')
def add_device_commands(request):
    result = False
    if request.method == "POST":
        device_command_form = DeviceCommandForm(data=request.POST)
        if device_command_form.is_valid():
            device_command = device_command_form.save()
            device_command.save()
            result = True
        else:
             #print(device_command_form.errors)
            result = False
    else:
        device_command_form = DeviceCommandForm()
    return render(request, 'networkapp/add_commands.html', {'device_command_form': device_command_form, 'result': result})

@login_required(login_url='/accounts/login/')
def device_configuration(request):
    sshcon.device_output.clear()
    ip_list = []
    password_list=[]
    username_list=[]
    unrechable_device_list=[]
    rechable_ip_list=[]
    invalid_cred_device_list=[]
    d = DEVICEDISCOVERY()
    dav = DEVICE_ACCESS_VERIFICATION()
    devicelist = DeviceCredentialDetail.objects.values('device_ip')

    if request.method == "POST":
        commandlist = request.POST.get('commands')
        deviceip = request.POST.get('seldeviceip')
        

        if deviceip == "all" :
            device_cred_query = DeviceCredentialDetail.objects.all()
             #print(device_cred_query)
            for device_cred in device_cred_query:
                username = device_cred.device_username
                 #print(username)
                username_list.append(username)
                password = device_cred.device_password
                password_list.append(password)
                deviceip = device_cred.device_ip
                ip_list.append(deviceip)
        else:
            ip_list.append(deviceip)
            usernames = DeviceCredentialDetail.objects.values('device_username').filter(device_ip=deviceip)
            passwords = DeviceCredentialDetail.objects.values('device_password').filter(device_ip=deviceip)
            for user in usernames:
                username = user.get('device_username')
                username_list.append(username)
            for user in passwords:
                password = user.get('device_password')
                password_list.append(password)
        
        rechable_ip_list = list(ip_list)
        d.ping_range(ip_list)
        index_list=[]
        for device, value in d.ping_res.items():
            if value == "inactive":
                unrechable_device_list.append(device)
                index_list.append(ip_list.index(device))

        username_list=np.delete(username_list, index_list).tolist()
        password_list=np.delete(password_list, index_list).tolist()
        rechable_ip_list=np.delete(rechable_ip_list, index_list).tolist()

        if len(rechable_ip_list) > 0 :
            dav.verifydav(rechable_ip_list,username_list,password_list)

        dav_index_list=[]
        for device, value in dav.dav_res.items():
            if value == "failed":
                invalid_cred_device_list.append(device)
                dav_index_list.append(ip_list.index(device))

        if len(rechable_ip_list) > 0 :
            username_list=np.delete(username_list, dav_index_list).tolist()
            password_list=np.delete(password_list, dav_index_list).tolist()
            rechable_ip_list=np.delete(rechable_ip_list, dav_index_list).tolist()        
            
             #print("commandlist "+ commandlist)

            create_threads(rechable_ip_list,username_list,password_list,commandlist,ssh_connection)
             #print("device out : ?????????? " ,sshcon.device_output)
         #print("invalid cred list :",invalid_cred_device_list)
         #print("unrechable cred list :",unrechable_device_list)

    return render(request, 'networkapp/device_configuration.html', {'devicelist':devicelist,'commandoutput' : sshcon.device_output,'invalidcredential':invalid_cred_device_list,'unreachabledevice':unrechable_device_list})

@login_required(login_url='/accounts/login/')
def device_access(request):
    sshcon.device_output.clear()
    ip_list = []
    password_list=[]
    username_list=[]
    unrechable_device_list=[]
    rechable_ip_list=[]
    invalid_cred_device_list=[]
    valid_cred_device_list=[]
    d = DEVICEDISCOVERY()
    dav = DEVICE_ACCESS_VERIFICATION()  

    devicelist = DeviceCredentialDetail.objects.values('device_ip')

    if request.method == "POST":
        deviceip = request.POST.get('seldeviceip')
         
        if deviceip == "all" :
            device_cred_query = DeviceCredentialDetail.objects.all()
             #print(device_cred_query)
            for device_cred in device_cred_query:
                username = device_cred.device_username
                 #print(username)
                username_list.append(username)
                password = device_cred.device_password
                password_list.append(password)
                deviceip = device_cred.device_ip
                ip_list.append(deviceip)
        else:
            ip_list.append(deviceip)
            usernames = DeviceCredentialDetail.objects.values('device_username').filter(device_ip=deviceip)
            passwords = DeviceCredentialDetail.objects.values('device_password').filter(device_ip=deviceip)
            for user in usernames:
                username = user.get('device_username')
                username_list.append(username)
            for user in passwords:
                password = user.get('device_password')
                password_list.append(password)
        
        rechable_ip_list = list(ip_list)
        d.ping_range(ip_list)
        index_list=[]
        for device, value in d.ping_res.items():
            if value == "inactive":
                unrechable_device_list.append(device)
                index_list.append(ip_list.index(device))

        username_list=np.delete(username_list, index_list).tolist()
        password_list=np.delete(password_list, index_list).tolist()
        rechable_ip_list=np.delete(rechable_ip_list, index_list).tolist()

        if len(rechable_ip_list) > 0 :
            dav.verifydav(rechable_ip_list,username_list,password_list)

        for device, value in dav.dav_res.items():
            print(device,value)
            if value == "failed":
                invalid_cred_device_list.append(device)
            else:
                valid_cred_device_list.append(device)
            

        for dev in invalid_cred_device_list:
            print("invalid cred list :",dev)
        #print("unrechable cred list :",unrechable_device_list)
        #Testing Demo

    return render(request, 'networkapp/dav.html', {'devicelist': devicelist,'invalidcredential':invalid_cred_device_list,'unreachabledevice':unrechable_device_list,'validcredlist':valid_cred_device_list})
