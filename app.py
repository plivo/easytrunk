import os
import os.path
import traceback
from flask import Flask, request, make_response, url_for
import plivo, plivoxml

app = Flask(__name__)
app.debug = True

@app.route('/response/sip/route/', methods=['GET','POST'])
def response():
    print "SIP Route %s" % request.values.items()
    _auth = request.values.get('AUTH', None)

    auth = request.values.get('X-PH-auth', "")
    destination = request.values.get('X-PH-destination', "")
    _from = request.values.get('X-PH-clid', "")
    dial_music = request.values.get('X-PH-dial_music', "")
    if dial_music != "real":
        dial_music = ""
    r = plivoxml.Response()
    if auth != _auth or not destination:
        r.addHangup()
    else:
        d = r.addDial(callerId=_from, dialMusic=dial_music)
        d.addNumber(destination)

    response = make_response(r.to_xml())
    response.headers['Content-Type'] = 'text/xml'
    return response

@app.route('/response/sip/inbound/', methods=['GET','POST'])
def inbound():
    _from = request.values.get('CLID', None)
    to = request.values.get('To', None)

    if _from is None:
        _from = request.values.get('From', "")
    dial_music = request.values.get('DialMusic', "")
    destination = request.values.get('DESTINATION', "").strip()

    r = plivoxml.Response()

    if not destination:
        r.addHangup()
    else:
        d = r.addDial(callerId=_from, dialMusic=dial_music)
        if destination.isdigit():
            d.addNumber(destination)
        elif '@' in destination:
            d.addUser(destination)
        else:
            d.addUser('%s@%s' % (to, destination))

    ## Add logic for hostname and IP

    response = make_response(r.to_xml())
    response.headers['Content-Type'] = 'text/xml'
    return response

def get_param(name, defaultvalue=None):
    return request.values.get(name, defaultvalue)

@app.route('/response/sip/inbound_trunk/', methods=['GET','POST'])
def inbound_trunk():
    try:
        failover_destination = ''
        destination = ""
        dial_action = ''
        event = get_param('Event')
        call_uuid = get_param('CallUUID')
        log = "Inbound trunk %s - " % call_uuid
        print "%s%s" % (log, request.values.items())

        hangup_cause = get_param('HangupCause')
        if hangup_cause:
            print "%sHangup %s" % (log, hangup_cause)
            return "Hangup"

        _from = get_param('CLID')
        to = get_param('To')

        if _from is None:
            _from = get_param('From', "")
        
        dial_music = get_param('DialMusic', "")
        
        destination_numbers = get_param('DESTINATION', "").strip()
        number_split = destination_numbers.split(',')
        if len(number_split) > 1:
            # Destination 1
            destination = number_split[0].strip()
            # Destination 2
            failover_destination = number_split[1].strip()
        else:
            # Destination 1
            destination = number_split[0].strip()
            failover_destination = ''

        successful_hangup_causes = get_param('SUCCESSFUL_HANGUP_CAUSES', None)
        if successful_hangup_causes is None:
            successful_hangup_causes = "NORMAL_CLEARING,ORIGINATOR_CANCEL,NO_ANSWER,NORMAL_UNSPECIFIED,NO_USER_RESPONSE,CALL_REJECTED,USER_BUSY,ALLOTTED_TIMEOUT,MEDIA_TIMEOUT,PROGRESS_TIMEOUT"
        successful_dial_status = get_param('SUCCESSFUL_DIAL_STATUS', None)
        if successful_dial_status is None:
            successful_dial_status = "completed,no-answer,busy,timeout"

        dial_action = ''

        r = plivoxml.Response()

        # If Destination is not set
        if not destination:
            print "%shangup" % log
            r.addHangup(reason="rejected")
            response = make_response(r.to_xml())
            response.headers['Content-Type'] = 'text/xml'
            return response

        if event == 'Redirect':
            hangup_causes = successful_hangup_causes.split(',')
            dial_status_causes = successful_dial_status.split(',')
            dial_hangup_cause = get_param('DialHangupCause')
            dial_status = get_param('DialStatus')
            if dial_hangup_cause in hangup_causes and dial_status in dial_status_causes:
                print "%sDialHangupCause %s and DialStatus %s match, no failover, hangup now" \
                                % (log, dial_hangup_cause, dial_status) 
                r.addHangup()
                response = make_response(r.to_xml())
                response.headers['Content-Type'] = 'text/xml'
                return response

        if event == "StartApp" and failover_destination:
            print "%sset failover destination found %s" % (log, failover_destination)
            dial_action = url_for('inbound_trunk', _external=True) + "?DESTINATION=%s&SUCCESSFUL_DIAL_STATUS=%s&SUCCESSFUL_HANGUP_CAUSES=%s&CLID=%s&DialMusic=%s" \
                                    % (failover_destination, successful_dial_status, successful_hangup_causes, _from, dial_music)
        else:
            print "%sno failover destination" % log
            dial_action = ''

        # Dial
        if dial_action:
            d = r.addDial(callerId=_from, dialMusic=dial_music, action=dial_action, method="GET")
        else:
            d = r.addDial(callerId=_from, dialMusic=dial_music)
        if destination.isdigit():
            d.addNumber(destination)
        elif '@' in destination:
            d.addUser(destination)
        else:
            d.addUser('%s@%s' % (to, destination))
        r.addHangup()
        print "%sDial %s" % (log, str(r.to_xml()))
        response = make_response(r.to_xml())
        response.headers['Content-Type'] = 'text/xml'
        return response
    except Exception, e:
        print str(e)
        print str(traceback.format_exc())
        return "ERROR %s" % str(e)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
