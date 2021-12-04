import paramiko



ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("172.20.4.29","22","jhala","Tigerandzues")
stdin, stdout, stderr = ssh.exec_command('python autorun/openProcess.py "sublime"')
