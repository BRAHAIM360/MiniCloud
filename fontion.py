import os ,re, subprocess,shlex,re,random,paramiko,crypt
from pexpect import pxssh
import getpass
import hashlib
from mysql.connector import connection, errorcode

class fonction:
    def __init__(self):
        pass

    def liste_vms(self):#cette fonction regroupe tout les vms dans une liste
        proc = subprocess.Popen(shlex.split("VBoxManage list vms"),stdout=subprocess.PIPE)
        output=proc.stdout.readlines()
        liste_vm=[]
        for i in output:
            
            i = str(i)
            i = re.sub('[\'"]', '', i)
            i = i[:-2]
            i = i[1:]
            l=i.split(' ', 1)
            l[1]=l[1][1:]
            l[1]=l[1][:-1]
            liste_vm.append(l)
        return liste_vm


    def liste_runing_vms(self):#cette fonction regroupe les vms lancer dans une liste
        proc = subprocess.Popen(shlex.split("VBoxManage list runningvms"),stdout=subprocess.PIPE)
        output=proc.stdout.readlines()
        liste_vm=[]
        for i in output:
            i = str(i)
            i = re.sub('[\'"]', '', i)
            i = i[:-2]
            i = i[1:]
            l=i.split(' ', 1)
            l[1]=l[1][1:]
            l[1]=l[1][:-1]
            liste_vm.append(l)
        return liste_vm


    def get_ip(self,nom_vm): #pour que cette fonction fonctionne il faut que l'addittion invité soit installer
        s="VBoxManage guestproperty enumerate "+ nom_vm +"| grep '/VirtualBox/GuestInfo/Net/' | grep 'V4/IP'"
        f=os.popen(s)
        liste = []
        for i in f.readlines():
            ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', i )
            liste.append(ip[0])
        return liste


    def importer_vm(self,chemain_vm,nom_vm):#pour importer une vm
        ss="vboxmanage import "+ chemain_vm +" --vsys 0 --vmname "+nom_vm
        process = subprocess.Popen(ss, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        process.wait()
        

    def modifer_user(self,nom_vm,username,password):
        ss="VBoxManage setextradata "+ nom_vm +" VBoxAuthSimple/users/"+username+" "+password 
        process = subprocess.Popen(ss, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        process.wait()

    def supprimer_vm(self,nom_vm):#pour supprimer une vm
        ss="VBoxManage unregistervm "+nom_vm+" --delete"
        process = subprocess.Popen(ss, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        process.wait()

    def modifier_config(self,nom_vm):#modifier la configuration vers host only
        ss="vboxmanage modifyvm "+nom_vm+" --hostonlyadapter1 vboxnet0"
        process = subprocess.Popen(ss, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        process.wait()
        ss="vboxmanage modifyvm "+nom_vm+" --nic1 hostonly"
        process = subprocess.Popen(ss, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        process.wait()
        
    

    def lancer_vm(self,nom_vm,arier_plan):#pour lancer une machine
        ss=""
        if arier_plan:
            ss= "VBoxManage startvm "+ nom_vm +" --type headless"
        else:
            ss= "VBoxManage startvm "+ nom_vm
        process = subprocess.Popen(ss, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        process.wait()
        
        
    def eteindre_vm(self,nom_vm): #pour eteindre une machine
        ss="VBoxManage controlvm "+nom_vm+" poweroff"
        process = subprocess.Popen(ss, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        process.wait()
    

    def ssh(self,hostname,username,password,cmd): #cette fonction exécute une cmd a travers une cnx SSH
        try:
            s = pxssh.pxssh()
            s.login (hostname, username, password)
            s.sendline (cmd)   
            s.prompt()             
            g=s.before          
            g=g.decode("utf-8")
            s.logout()
            return g
        except pxssh.ExceptionPxssh :
            return "conexion échoué."

    def hash(self,password): #pour crypter le mot de passe utilisteur en MD5
        h = hashlib.md5(password.encode())
        return h.hexdigest()

    def conextion(self,username,password):#pour la connexion au compte 
        val=(username,password)
        cnx =connection.MySQLConnection(user='brahim', password='brahim',host='127.0.0.1',
                                        database='tp_grid')
        mycursor = cnx.cursor()
        mycursor.execute("SELECT * FROM user where username= %s and password=%s",val)
        myresult = mycursor.fetchone()
        if myresult  == None:
            return False
        else:
            return True
        
    def nouveau_compt(self,username,password,emai):
        cnx =connection.MySQLConnection(user='brahim', password='brahim',host='127.0.0.1',
                                    database='tp_grid')
        mycursor = cnx.cursor()
        val=(username,password,emai)
        mycursor.execute("INSERT INTO user (username,password,email) VALUES ( %s,%s,%s)",val)
        cnx.commit()
    

    def hash_mot_pass(self,password): #cette fonction crypte le mot de passe pour l'utiliser plus tart pour ajouter une utilisateur
        encPass = crypt.crypt(password,"22")
        return encPass


    def ajouter_utilisateur(self,hostname,new_user,new_password):
        try:
            s = pxssh.pxssh()
            username = 'root'  # on configure le root mot de passe de tout les vm  'toor'
            password = 'toor'  # pour qu'on puisse ajouter un utilisateur 
            s.login (hostname, username, password)
            s.sendline ('useradd -p '+ self.hash_mot_pass(new_password) +' '+new_user)  
            s.prompt()             
            s.sendline ('usermod -aG wheel '+new_user)#pour Redhat distrubution 
            s.prompt() 
            s.sendline ('usermod -aG sudo '+new_user) #pour debian distrubution
            s.prompt() 
            s.logout()
            return True
        except pxssh.ExceptionPxssh :
            print ("l'authentification est échoué.")
            return False


    def get_ip_pour_ssh(self,nom_vm):   #cette fonction retourne l'adresse ip pour etablire une connexion ssh
        liste_ip=self.get_ip(nom_vm) #elle prend l'addresse ip dans le résau 192.168.56.0 qui'est le réseau 
        for ip in liste_ip :    #host only
            if '192.168.56' in ip:
                return ip
        return '0'
        
