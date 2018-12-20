import os

from crontab import CronTab

cron  = CronTab(user=True)

cwd = os.getcwd()
command = f"cd {cwd}"

job  = cron.new(command=f'{command} && sh cron.sh')
cron.write()
