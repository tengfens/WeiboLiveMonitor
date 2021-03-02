CONTENT_TEMPLATE = '''
    <p style="font-size:0.9em; line-height: 1.5; font-family:microsoft yahei;">
        Live Created: %LiveCreated%<br />
        Live URL: <a href="%LiveAddr%" style="color: #6495ED;text-decoration:none;" target="_blank">%LiveAddr%</a><br />
        Live Stream: <a href="%LiveStream%" style="color: #6495ED;text-decoration:none;" target="_blank">%LiveStream%</a><br />
        Replay Stream: <a href="%ReplayStream%" style="color: #6495ED;text-decoration:none;" target="_blank">%ReplayStream%</a><br />
    </p>
    <hr style="height:1px;border:none;border-top:1px dashed #E0E0E0;" />
'''

def generate_one_content(live_create, live_addr, live_stream, replay_stream):
    return CONTENT_TEMPLATE.replace('%LiveCreated%', live_create).replace('%LiveAddr%', live_addr).replace('%LiveStream%', live_stream).replace('%ReplayStream%', replay_stream)

def generate_html(template, output, uid, username, contents):
    f = open(template, 'r')
    html = f.read()
    f.close()
    html = html.replace('%Contents%', contents).replace('%Uid%', uid).replace('%UserName%', username)
    f = open(output, 'w+')
    f.write(html)
    f.close()
    return html