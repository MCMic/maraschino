from flask import jsonify, render_template, json, send_file
from maraschino import app, logger, WEBROOT, RUNDIR
from maraschino.tools import requires_auth, get_setting_value
from threading import Thread
import StringIO
import urllib
import urllib2
import base64
from mpd import MPDClient
import traceback


def mpd_connect():
    password = str(get_setting_value('mpd_password'))
    url = str(get_setting_value('mpd_host'))
    port = int(get_setting_value('mpd_port'))

    client = MPDClient()
    client.timeout = 10                # network timeout in seconds (floats allowed), default: None
    client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
    logger.log('MPD :: CONNECT -- %s %s' % (url, port), 'DEBUG')
    client.connect(url, port)

    return client


def mpd_exception(e):
    logger.log('MPD :: EXCEPTION -- %s' % e, 'DEBUG')
    return render_template('mpd/base.html', mpd=True, message=e)


@app.route('/xhr/mpd/')
@requires_auth
def xhr_mpd():
    return xhr_mpd_playing()


@app.route('/xhr/mpd/playing/')
@requires_auth
def xhr_mpd_playing(mobile=False):
    logger.log('MPD :: Fetching playing', 'INFO')

    try:
        mpd = mpd_connect();
        current = mpd.currentsong();
        status = mpd.status();
        status['progress'] = "%.2f" % (100 * float(status['elapsed'])/float(current['time']))
    except Exception as e:
        return mpd_exception(e)

    return render_template('mpd.html',
        current=current,
        status=status,
        mpd=True,
    )
