import update_engine
import html_generator
import email_sender
import time
import os
from random import randint
from setting import *

FILE_DIR = os.path.dirname(os.path.realpath(__file__))

engine = update_engine.UpdateEngine(UID_LIST)
while True:
    print("[{}] <<-- check live status -->>".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    meta_diff = engine.update_meta()
    for i in meta_diff.keys():
        contents = ''
        for timestamp in meta_diff[i]['diff'].keys():
            contents += html_generator.generate_one_content(timestamp, meta_diff[i]['diff'][timestamp]['url'], meta_diff[i]['diff'][timestamp]['live_hls_url'], meta_diff[i]['diff'][timestamp]['live_replay_url'])
        html = html_generator.generate_html(os.path.join(FILE_DIR, 'template.html'), os.path.join(FILE_DIR, 'pre_send.html'), meta_diff[i]['uid'], i, contents)
        email = email_sender.Email(MAIL_USR, MAIL_AUTH)
        email.connect()
        email.send(TO_LIST, '{}\'s WeiBo Live is Updated !'.format(i), html)
    if not meta_diff:
        print("[{}] no new live updated".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    print()
    time.sleep(randint(20, 60))
