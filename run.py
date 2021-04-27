import update_engine
import html_generator
import email_sender
import time
import os
from argparse import ArgumentParser
from random import randint
from setting import *

FILE_DIR = os.path.dirname(os.path.realpath(__file__))

env = os.environ
if 'UID_LIST' in env.keys() and env['UID_LIST']:
    uid_list = env['UID_LIST'].split(';')
else:
    uid_list = UID_LIST

if 'TO_LIST' in env.keys() and env['TO_LIST']:
    to_list = env['TO_LIST'].split(';')
else:
    to_list = TO_LIST

if 'MAIL_USR' in env.keys() and env['MAIL_USR']:
    mail_usr = env['MAIL_USR']
else:
    mail_usr = MAIL_USR

if 'MAIL_AUTH' in env.keys() and env['MAIL_AUTH']:
    mail_auth = env['MAIL_AUTH']
else:
    mail_auth = MAIL_AUTH

if 'SMTP_SERVER' in env.keys() and env['SMTP_SERVER']:
    smtp_server = env['SMTP_SERVER']
else:
    smtp_server = SMTP_SERVER

if 'SMTP_PORT' in env.keys() and env['SMTP_PORT']:
    smtp_port = env['SMTP_PORT']
else:
    smtp_port = int(SMTP_PORT)

arg_parser = ArgumentParser()
arg_parser.add_argument(
    "--run_once",
    help="only run fetch the data once",
    dest="run_once", 
    action='store_true',
    default=False)
args = arg_parser.parse_args()

engine = update_engine.UpdateEngine(uid_list)
while True:
    print("[{}] <<-- check live status -->>".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    meta_diff = engine.update_meta()
    for i in meta_diff.keys():
        contents = ''
        for timestamp in meta_diff[i]['diff'].keys():
            contents += html_generator.generate_one_content(timestamp, meta_diff[i]['diff'][timestamp]['url'], meta_diff[i]['diff'][timestamp]['live_hls_url'], meta_diff[i]['diff'][timestamp]['live_replay_url'])
        html = html_generator.generate_html(os.path.join(FILE_DIR, 'template.html'), os.path.join(FILE_DIR, 'pre_send.html'), meta_diff[i]['uid'], i, contents)
        email = email_sender.Email(mail_usr, mail_auth, smtp_server, smtp_port)
        email.connect()
        email.send(to_list, '{}\'s WeiBo Live is Updated !'.format(i), html)
    if not meta_diff:
        print("[{}] no new live updated".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    print()
    time.sleep(randint(20, 60))
    if args.run_once:
        break
