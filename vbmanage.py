from flask import Flask, session, render_template, request, redirect, g, url_for
import os,paramiko
from mysql.connector import connection, errorcode
from fontion import fonction

app = Flask(__name__)
app.secret_key = os.urandom(24)

methods = fonction()
@app.route('/', methods=['GET', 'POST'])
def index():
    if ('user' in session):
        return redirect(url_for('vms'))
    else: 
        return redirect(url_for('register'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if ('user' in session):
        return redirect(url_for('index'))

    if request.method == 'POST':
        if request.form['action'] == 'login':
            session.pop('user', None)
            username = request.form['i_username']
            password = methods.hash(request.form['i_password'])
            if methods.conextion(username,password):
                session['user'] = 'connecter'
                return redirect(url_for('index'))
        elif request.form['action'] == 'sign_in':
            session.pop('user', None)
            password_hash= methods.hash(request.form['c_password'])
            methods.nouveau_compt(request.form['c_user'],password_hash,request.form['c_email'])
            session['user'] = 'connecter'
            return redirect(url_for('index'))

    return render_template('teste.html')

        
@app.route('/logout')#pour dropper la session
def logout():
    session.pop('user', None)
    return redirect(url_for('register'))

@app.route('/apropos')
def apropos():
    return render_template('apropos.html')


@app.route('/vms')
def vms():
    if ('user' in session):
        return render_template('afficher_vms.html',vms=methods.liste_vms(),runningvms=methods.liste_runing_vms())
    else: 
        return redirect(url_for('register'))

    


@app.route('/import_export', methods=['GET', 'POST'])
def import_export():
    if request.method == 'POST':
        if request.form['action'] == 'importer':
            methods.importer_vm(request.form['path'],request.form['nom_vm'])
            return render_template('impor.html',vms=methods.liste_vms(),message="la machine est bien importer")
            
        elif request.form['action'] == 'valider':
            ip=methods.get_ip_pour_ssh(request.form['selected1'])
            if ip =='0':
                return render_template('impor.html',vms=methods.liste_vms(),message="cette Vm n'est pas joignable coté réseau ajouter host only addapter")
            else:                
                methods.ajouter_utilisateur(ip,request.form['username'],request.form['password'])
                return render_template('impor.html',vms=methods.liste_vms(),message="l'utilistaur un bien ajouter")
            

        elif request.form['action'] == 'modifier':
            methods.modifier_config(request.form['selected2'])
            return render_template('impor.html',vms=methods.liste_vms(),message="la machine est bien modifier")
            

        elif request.form['action'] == 'supprimer':
            methods.supprimer_vm(request.form['selected3'])
            return render_template('impor.html',vms=methods.liste_vms(),message="la machine est bien supprimer ")
          
    if ('user' in session):
        return render_template('impor.html',vms=methods.liste_vms())
    else: 
        return redirect(url_for('register'))     

    

@app.route('/manupulation', methods=['GET', 'POST'])
def manupulation():
    if request.method == 'POST':
        if request.form['action'] == 'lancer':
            methods.lancer_vm(request.form['selected1'],False)
            return render_template('manipe_vm.html',vms=methods.liste_vms(),message="la machine est bien lancer",vmsr=methods.liste_runing_vms())
            
        elif request.form['action'] == 'afficher':
            l=methods.get_ip(request.form['selected2'])#il faut que invité addition soit installer dans les vm pour que la methode fonctionne 
            return render_template('manipe_vm.html',vms=methods.liste_vms(),vmsr=methods.liste_runing_vms(),liste=l)
            

        elif request.form['action'] == 'etindre':
            methods.eteindre_vm(request.form['selected3'])
            return render_template('manipe_vm.html',vms=methods.liste_vms(),vmsr=methods.liste_runing_vms(),message="la machine est bien eteint")
            
    if ('user' in session):
        return render_template('manipe_vm.html',vms=methods.liste_vms(),vmsr=methods.liste_runing_vms())
    else: 
        return redirect(url_for('register'))

    

@app.route('/ssh', methods=['GET', 'POST'])
def ssh():
    if request.method == 'POST':
        if request.form['action'] == 'Executer':
            
            m=methods.ssh(request.form['ip'],request.form['username'],request.form['password'],request.form['cmd'])
           
            return render_template('ssh.html',message=m)
    
    if ('user' in session):
        return render_template('ssh.html')
    else: 
        return redirect(url_for('register'))

    

if __name__ == '__main__':
    app.run(debug=True)


        

   