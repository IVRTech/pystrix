"""
pystrix.ami.core_events
=======

Provides defnitions and filtering rules for events that may be raised by Asterisk.

Legal
-----

This file is part of pystrix.
pystrix is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU General Public License and
GNU Lesser General Public License along with this program. If not, see
<http://www.gnu.org/licenses/>.

(C) Ivrnet, inc., 2011

Authors:

- Neil Tallim <n.tallim@ivrnet.com>

The events implemented by this module follow the definitions provided by
http://www.asteriskdocs.org/ and https://wiki.asterisk.org/
"""
from ami import _Message

class AGIExec(_Message):
    """
    Generated when an AGI script executes an arbitrary application.
    
    - 'Channel': The channel in use
    - 'Command': The command that was issued
    - 'CommandId': The command's identifier, used to track events from start to finish
    - 'SubEvent': "Start", "End"
    - 'Result': Only present when 'SubEvent' is "End": "Success" (and "Failure"?)
    - 'ResultCode': Only present when 'SubEvent' is "End": the result-code from Asterisk
    """
    def process(self):
        """
        Translates the 'Result' header's value into a bool.
        
        Translates the 'ResultCode' header's value into an int, setting it to `-1` if coercion
        fails.
        """
        (headers, data) = _Message.process(self)
        
        try:
            headers['ResultCode'] = int(headers['ResultCode'])
        except Exception:
            headers['ResultCode'] = -1
            
        headers['Result'] = headers.get('Result') == 'Success'
        
        return (headers, data)
        
class ChannelUpdate(_Message):
    """
    Describes a change in a channel.
    
    Some fields are type-dependent and will appear as children of that type in the list.
    
    - 'Channel': The channel being described
    - 'Channeltype': One of the following types
    
     - 'SIP': SIP channels have the following fields
     
      - 'SIPcallid': 'DB45B1B5-1EAD11E1-B979D0B6-32548E42@10.13.38.201', the CallID negotiated with
        the endpoint; this should be present in any CDRs generated
      - 'SIPfullcontact': 'sip:flan@uguu.ca', the address of the SIP contact field, if any (observed
        during a REFER)
    
    - 'UniqueID': An Asterisk-unique value
    """
    
class CoreShowChannel(_Message):
    """
    Provides the definition of an active Asterisk channel.
    
    - 'AccountCode': The account code associated with the channel
    - 'ActionID': The ID associated with the original request
    - 'Application': The application currently being executed by the channel
    - 'ApplicationData': The arguments provided to the application
    - 'BridgedChannel': The channel to which this channel is connected, if any
    - 'BridgedUniqueID': ?
    - 'CallerIDnum': The (often) numeric address of the caller
    - 'CallerIDname': The (optional, media-specific) name of the caller
    - 'Channel': The channel being described
    - 'ChannelState': One of the following numeric values, as a string:

     - '0': Not connected
     - '4': Alerting
     - '6': Connected
     
    - 'ChannelStateDesc': A lexical description of the channel's current state
    - 'ConnectedLineNum': The (often) numeric address of the called party (may be nil)
    - 'ConnectedLineName': The (optional, media-specific) name of the called party (may be nil)
    - 'Context': The dialplan context in which the channel is executing
    - 'Duration': The client's connection time in "hh:mm:ss" form
    - 'Extension': The dialplan context in which the channel is executing
    - 'Priority': The dialplan priority in which the channel is executing
    - 'UniqueID': An Asterisk-unique value
    """
    def process(self):
        """
        Translates the 'ChannelState' header's value into an int, setting it to `None` if coercion
        fails.
        
        Replaces the 'Duration' header's value with the number of seconds, as an int, or -1 if
        conversion fails.
        """
        (headers, data) = _Message.process(self)
        
        try:
            headers['ChannelState'] = int(headers['ChannelState'])
        except Exception:
            headers['ChannelState'] = None
            
        try:
            (h, m, s) = (int(v) for v in headers['Duration'].split(':'))
            headers['Duration'] = s + m * 60 + h * 60 * 60
        except Exception:
            headers['Duration'] = -1
            
        return (headers, data)
        
class CoreShowChannelsComplete(_Message):
    """
    Indicates that all Asterisk channels have been listed.
    
    - 'ActionID': The ID associated with the original request
    - 'ListItems' : The number of items returned prior to this event
    """
    def process(self):
        """
        Translates the 'ListItems' header's value into an int, or -1 on failure.
        """
        (headers, data) = _Message.process(self)
        
        try:
            headers['ListItems'] = int(headers['ListItems'])
        except Exception:
            headers['ListItems'] = -1
            
        return (headers, data)
        
class DBGetResponse(_Message):
    """
    Provides the value requested from the database.
    
    - 'Family': The family of the value being provided
    - 'Key': The key of the value being provided
    - 'Val': The value being provided, represented as a string
    """

class DTMF(_Message):
    """
    - 'Begin': 'Yes' or 'No', indicating whether this started or ended the DTMF press
    - 'Channel': The channel being described
    - 'Digit': The DTMF digit that was pressed
    - 'Direction': 'Received' or 'Sent'
    - 'End': 'Yes' or 'No', indicating whether this started or ended the DTMF press (inverse of
      `Begin`, though both may be `Yes` if the event has no duration)
    - 'UniqueID': An Asterisk-unique value
    """
    def process(self):
        """
        Translates 'Begin' and 'End' into booleans, and adds a 'Received':bool header.
        """
        (headers, data) = _Message.process(self)
        
        for header in ('Begin', 'End'):
            headers[header] = headers.get(header) == 'Yes'
        headers['Received'] = headers.get('Direction') == 'Received'
        
        return (headers, data)
        
class FullyBooted(_Message):
    """
    Indicates that Asterisk is online.
    
    - 'Status': "Fully Booted"
    """
    
class Hangup(_Message):
    """
    Indicates that a channel has been hung up.
    
    - 'Cause': One of the following numeric values, as a string:
    
     - '0': Hung up
     - '16': Normal clearing
     
    - 'Cause-txt': Additional information related to the hangup
    - 'Channel': The channel hung-up
    - 'Uniqueid': An Asterisk unique value
    """
    def process(self):
        """
        Translates the 'Cause' header's value into an int, setting it to `None` if coercion fails.
        """
        (headers, data) = _Message.process(self)
        try:
            headers['Cause'] = int(headers['Cause'])
        except Exception:
            headers['Cause'] = None
        return (headers, data)

class HangupRequest(_Message):
    """
    Emitted when a request to terminate the call is received.

    - 'Channel': The channel identifier used by Asterisk
    - 'Uniqueid': An Asterisk unique value
    """

class MonitorStart(_Message):
    """
    Indicates that monitoring has begun.
    
    - 'Channel': The channel being monitored
    - 'Uniqueid': An Asterisk unique value
    """

class MonitorStop(_Message):
    """
    Indicates that monitoring has ceased.
    
    - 'Channel': The channel that was monitored
    - 'Uniqueid': An Asterisk unique value
    """

class NewAccountCode(_Message):
    """
    Indicates that the account-code associated with a channel has changed.
    
    - 'AccountCode': The new account code
    - 'Channel': The channel that was affected.
    - 'OldAccountCode': The old account code
    """

class Newchannel(_Message):
    """
    Indicates that a new channel has been created.

    - 'AccountCode': The billing account associated with the channel; may be empty
    - 'CallerIDNum': The (often) numeric identifier of the caller
    - 'CallerIDName': The caller's name, on supporting channels
    - 'Channel': The channel identifier used by Asterisk
    - 'ChannelState': One of the following numeric values, as a string:

     - '0': Not connected
     - '4': Alerting
     - '6': Connected

    - 'ChannelStateDesc': A lexical description of the channel's current state
    - 'Context': The context that the channel is currently operating in
    - 'Exten': The extension the channel is currently operating in
    - 'Uniqueid': An Asterisk unique value
    """
    def process(self):
        """
        Translates the 'ChannelState' header's value into an int, setting it to `None` if coercion
        fails.
        """
        (headers, data) = _Message.process(self)
        try:
            headers['ChannelState'] = int(headers['ChannelState'])
        except Exception:
            headers['ChannelState'] = None
        return (headers, data)

class Newexten(_Message):
    """
    Emitted when a channel switches executing extensions.

    - 'AppData': The argument passed to the application
    - 'Application': The application being invoked
    - 'Channel': The channel identifier used by Asterisk
    - 'Context': The context the channel is currently operating in
    - 'Extension': The extension the channel is currently operating in
    - 'Priority': The priority the channel is currently operating in
    - 'Uniqueid': An Asterisk unique value
    """

class Newstate(_Message):
    """
    Indicates that a channel's state has changed.

    - 'CallerIDNum': The (often) numeric identifier of the caller
    - 'CallerIDName': The caller's name, on supporting channels
    - 'Channel': The channel identifier used by Asterisk
    - 'ChannelStateDesc': A lexical description of the channel's current state
    - 'ChannelState': One of the following numeric values, as a string:

     - '0': Not connected
     - '4': Alerting
     - '6': Connected

    - 'ConnectedLineNum': ?
    - 'ConnectedLineName': ?
    - 'Uniqueid': An Asterisk unique value
    """
    def process(self):
        """
        Translates the 'ChannelState' header's value into an int, setting it to `None` if coercion
        fails.
        """
        (headers, data) = _Message.process(self)
        try:
            headers['ChannelState'] = int(headers['ChannelState'])
        except Exception:
            headers['ChannelState'] = None
        return (headers, data)
        
class OriginateResponse(_Message):
    """
    Describes the result of an Originate request.
    
    * 'CallerIDName': The supplied source name
    * 'CallerIDNum': The supplied source address
    * 'Channel': The Asterisk channel used for the call
    * 'Context': The dialplan context into which the call was placed, as a string; unused for applications
    * 'Exten': The dialplan extension into which the call was placed, as a string; unused for applications
    * 'Reason': An integer as a string, ostensibly one of the `ORIGINATE_RESULT` constants; undefined integers may exist
    """
    def process(self):
        """
        Sets the 'Reason' values to an int, one of the `ORIGINATE_RESULT` constants, with -1
        indicating failure.
        """
        (headers, data) = _Message.process(self)
        try:
            headers['Reason'] = int(headers.get('Reason'))
        except Exception:
            headers['Reason'] = -1
        return (headers, data)
        
class ParkedCall(_Message):
    """
    Describes a parked call.
    
    - 'ActionID': The ID associated with the original request
    - 'CallerID': The ID of the caller, ".+?" <.+?>
    - 'CallerIDName' (optional): The name of the caller, on supporting channels
    - 'Channel': The channel of the parked call
    - 'Exten': The extension associated with the parked call
    - 'From': The callback channel associated with the call
    - 'Timeout' (optional): The time remaining before the call is reconnected with the callback
      channel
    """
    def process(self):
        """
        Translates the 'Timeout' header's value into an int, setting it to `None` if coercion
        fails, and leaving it absent if it wasn't present in the original response.
        """
        (headers, data) = _Message.process(self)
        timeout = headers.get('Timeout')
        if not timeout is None:
            try:
                headers['Timeout'] = int(timeout)
            except Exception:
                headers['Timeout'] = None
        return (headers, data)
        
class ParkedCallsComplete(_Message):
    """
    Indicates that all parked calls have been listed.
    
    - 'ActionID': The ID associated with the original request
    """

class PeerEntry(_Message):
    """
    Describes a peer.
    
    - 'ActionID': The ID associated with the original request
    - 'ChannelType': The type of channel being described.
    
     - 'SIP'
     
    - 'ObjectName': The internal name by which this peer is known
    - 'ChanObjectType': The type of object
    
     - 'peer'
     
    - 'IPaddress' (optional): The IP of the peer
    - 'IPport' (optional): The port of the peer
    - 'Dynamic': 'yes' or 'no', depending on whether the peer is resolved by IP or authentication
    - 'Natsupport': 'yes' or 'no', depending on whether the peer's messages' content should be
      trusted for routing purposes. If not, packets are sent back to the last hop
    - 'VideoSupport': 'yes' or 'no'
    - 'ACL': 'yes' or 'no'
    - 'Status': 'Unmonitored', 'OK (\d+ ms)'
    - 'RealtimeDevice': 'yes' or 'no'
    """
    def process(self):
        """
        Translates the 'Port' header's value into an int, setting it to `None` if coercion
        fails, and leaving it absent if it wasn't present in the original response.
        
        Translates the 'Dynamic', 'Natsupport', 'VideoSupport', 'ACL', and 'RealtimeDevice' headers'
        values into bools.
        """
        (headers, data) = _Message.process(self)
        
        ip_port = headers.get('IPport')
        if not ip_port is None:
            try:
                headers['IPport'] = int(ip_port)
            except Exception:
                headers['IPport'] = None
                
        for header in ('Dynamic', 'Natsupport', 'VideoSupport', 'ACL', 'RealtimeDevice'):
            headers[header] = headers.get(header) == 'yes'
            
        return (headers, data)

class PeerlistComplete(_Message):
    """
    Indicates that all peers have been listed.
    
    - 'ActionID': The ID associated with the original request
    """

class QueueEntry(_Message):
    """
    Indicates that a call is waiting to be answered.
    
    - 'ActionID' (optional): The ID associated with the original request, if a response
    - 'Channel': The channel of the inbound call
    - 'CallerID': The (often) numeric ID of the caller
    - 'CallerIDName' (optional): The friendly name of the caller on supporting channels
    - 'Position': The numeric position of the caller in the queue
    - 'Queue': The queue in which the caller is waiting
    - 'Wait': The number of seconds the caller has been waiting
    """
    def process(self):
        """
        Translates the 'Position' and 'Wait' headers' values into ints, setting them to -1 on error.
        """
        (headers, data) = _Message.process(self)
        for header in ('Position', 'Wait'):
            try:
                headers[header] = int(headers.get(header))
            except Exception:
                headers[header] = -1
        return (headers, data)

class QueueMember(_Message):
    """
    Describes a member of a queue.
    
    - 'ActionID' (optional): The ID associated with the original request, if a response
    - 'CallsTaken': The number of calls received by this member
    - 'LastCall': The UNIX timestamp of the last call taken, or 0 if none
    - 'Location': The interface in the queue
    - 'MemberName' (optional): The friendly name of the member
    - 'Membership': "dynamic" ("static", too?)
    - 'Paused': '1' or '0' for 'true' and 'false', respectively
    - 'Penalty': The selection penalty to apply to this member (higher numbers mean later selection)
    - 'Queue': The queue to which the member belongs
    - 'Status': One of the following, as a string:
    
     - '0': Idle
     - '1': In use
     - '2': Busy
    """
    def process(self):
        """
        Translates the 'CallsTaken', 'LastCall', 'Penalty', and 'Status' headers' values into ints,
        setting them to -1 on error.
        
        'Paused' is set to a bool.
        """
        (headers, data) = _Message.process(self)
        
        for header in ('CallsTaken', 'LastCall', 'Penalty', 'Status'):
            try:
                headers[header] = int(headers.get(header))
            except Exception:
                headers[header] = -1
                
        paused = headers.get('Paused')
        headers['Paused'] = paused and paused == '1'
        
        return (headers, data)
        
class QueueMemberAdded(_Message):
    """
    Indicates that a member was added to a queue.
    
    - 'CallsTaken': The number of calls received by this member
    - 'LastCall': The UNIX timestamp of the last call taken, or 0 if none
    - 'Location': The interface added to the queue
    - 'MemberName' (optional): The friendly name of the member
    - 'Membership': "dynamic" ("static", too?)
    - 'Paused': '1' or '0' for 'true' and 'false', respectively
    - 'Penalty': The selection penalty to apply to this member (higher numbers mean later selection)
    - 'Queue': The queue to which the member was added
    - 'Status': One of the following, as a string:
    
     - '0': Idle
     - '1': In use
     - '2': Busy
    """
    def process(self):
        """
        Translates the 'CallsTaken', 'LastCall', 'Penalty', and 'Status' headers' values into ints,
        setting them to -1 on error.
        
        'Paused' is set to a bool.
        """
        (headers, data) = _Message.process(self)
        
        for header in ('CallsTaken', 'LastCall', 'Penalty', 'Status'):
            try:
                headers[header] = int(headers.get(header))
            except Exception:
                headers[header] = -1
                
        paused = headers.get('Paused')
        headers['Paused'] = paused and paused == '1'
        
        return (headers, data)
        
class QueueMemberPaused(_Message):
    """
    Indicates that the pause-state of a queue member was changed.
    
    - 'Location': The interface added to the queue
    - 'MemberName' (optional): The friendly name of the member
    - 'Paused': '1' or '0' for 'true' and 'false', respectively
    - 'Queue': The queue in which the member was paused
    """
    def process(self):
        """
        'Paused' is set to a bool.
        """
        (headers, data) = _Message.process(self)
        paused = headers.get('Paused')
        headers['Paused'] = paused and paused == '1'
        return (headers, data)

class QueueMemberRemoved(_Message):
    """
    Indicates that a member was removed from a queue.
    
    - 'Location': The interface removed from the queue
    - 'MemberName' (optional): The friendly name of the member
    - 'Queue': The queue from which the member was removed
    """
    
class QueueParams(_Message):
    """
    Describes the attributes of a queue.
    
    - 'Abandoned': The number of calls that have gone unanswered
    - 'ActionID' (optional): The ID associated with the original request, if a response
    - 'Calls': The number of current calls in the queue
    - 'Completed': The number of completed calls
    - 'Holdtime': ?
    - 'Max': ?
    - 'Queue': The queue being described
    - 'ServiceLevel': ?
    - 'ServiceLevelPerf': ?
    - 'Weight': ?
    """
    def process(self):
        """
        Translates the 'Abandoned', 'Calls', 'Completed', 'Holdtime', and 'Max' headers' values into
        ints, setting them to -1 on error.
        
        Translates the 'ServiceLevel', 'ServiceLevelPerf', and 'Weight' values into
        floats, setting them to -1 on error.
        """
        (headers, data) = _Message.process(self)
        
        for header in ('Abandoned', 'Calls', 'Completed', 'Holdtime', 'Max'):
            try:
                headers[header] = int(headers.get(header))
            except Exception:
                headers[header] = -1
                
        for header in ('ServiceLevel', 'ServiceLevelPerf', 'Weight'):
            try:
                headers[header] = float(headers.get(header))
            except Exception:
                headers[header] = -1
        
        return (headers, data)
        
class QueueStatusComplete(_Message):
    """
    Indicates that a QueueStatus request has completed.
    
    - 'ActionID': The ID associated with the original request
    """

class Reload(_Message):
    """
    Indicates that Asterisk's configuration was reloaded.
    
    - 'Message': A human-readable summary
    - 'Module': The affected module
    - 'Status': 'Enabled'
    """
    
class RTCPReceived(_Message):
    """
    A Real Time Control Protocol message emitted by Asterisk when using an RTP-based channel,
    providing statistics on the quality of a connection, for the receiving leg.

    - 'DLSR': ? (float as a string, followed by '(sec)')
    - 'FractionLost': The percentage of lost packets, a float as a string
    - 'From': The IP and port of the source, separated by a colon
    - 'HighestSequence': ? (int as string)
    - 'IAJitter': ? (float as a string)
    - 'LastSR': ? (int as string)
    - 'PacketsLost': The number of lost packets, as a string
    - 'PT': ?
    - 'ReceptionReports': The number of reports used to compile this event, as a string
    - 'SenderSSRC': Session source
    - 'SequenceNumberCycles': ?
    """
    def process(self):
        """
        Translates the 'HighestSequence', 'LastSR', 'PacketsLost', 'ReceptionReports,
        and 'SequenceNumbercycles' values into ints, setting them to -1 on error.

        Translates the 'DLSR', 'FractionLost', 'IAJitter', and 'SentNTP' values into floats, setting
        them to -1 on error.

        Splits 'From' into a tuple of IP:str and port:int, or sets it to `None` if the format is
        unknown.
        """
        (headers, data) = _Message.process(self)
        
        for header in ('HighestSequence', 'LastSR', 'PacketsLost', 'ReceptionReports', 'SequenceNumbercycles'):
            try:
                headers[header] = int(headers.get(header))
            except Exception:
                headers[header] = -1

        headers['DLSR'] = (headers.get('DSLR') or '').split(' ', 1)[0]
        for header in ('DLSR', 'FractionLost', 'IAJitter'):
            try:
                headers[header] = float(headers.get(header))
            except Exception:
                headers[header] = -1

        to = headers.get('From')
        if to and ':' in to:
            headers['From'] = tuple(to.rsplit(':', 1))
        else:
            headers['From'] = None
            
        return (headers, data)

class RTCPSent(_Message):
    """
    A Real Time Control Protocol message emitted by Asterisk when using an an RTP-based channel,
    providing statistics on the quality of a connection, for the sending leg.

    - 'CumulativeLoss': The number of lost packets, as a string
    - 'DLSR': ? (float as a string, followed by '(sec)')
    - 'FractionLost': The percentage of lost packets, a float as a string
    - 'IAJitter': ? (float as a string)
    - 'OurSSRC': Session source
    - 'ReportBlock': ?
    - 'SentNTP': The NTP value, a float as a string
    - 'SentOctets': The number of bytes sent, as a string
    - 'SentPackets': The number of packets sent, as a string
    - 'SentRTP': The number of RTP events sent, as a string
    - 'TheirLastSR': ? (int as string)
    - 'To': The IP and port of the recipient, separated by a colon
    """
    def process(self):
        """
        Translates the 'CumulativeLoss', 'SentOctets', 'SentPackets', 'SentRTP', and
        'TheirLastSR' values into ints, setting them to -1 on error.

        Translates the 'DLSR', 'FractionLost', 'IAJitter', and 'SentNTP' values into floats, setting
        them to -1 on error.

        Splits 'To' into a tuple of IP:str and port:int, or sets it to `None` if the format is
        unknown.
        """
        (headers, data) = _Message.process(self)
        
        for header in ('CumulativeLoss', 'SentOctets', 'SentPackets', 'SentRTP', 'TheirLastSR'):
            try:
                headers[header] = int(headers.get(header))
            except Exception:
                headers[header] = -1

        headers['DLSR'] = (headers.get('DSLR') or '').split(' ', 1)[0]
        for header in ('DLSR', 'FractionLost', 'IAJitter', 'SentNTP'):
            try:
                headers[header] = float(headers.get(header))
            except Exception:
                headers[header] = -1

        to = headers.get('To')
        if to and ':' in to:
            headers['To'] = tuple(to.rsplit(':', 1))
        else:
            headers['To'] = None
            
        return (headers, data)

class Shutdown(_Message):
    """
    Emitted when Asterisk shuts down.
    
    - 'Restart': "True" or "False"
    - 'Shutdown': "Cleanly"
    """
    def process(self):
        """
        'Restart' is set to a bool.
        """
        (headers, data) = _Message.process(self)
        
        restart = headers.get('Restart')
        headers['Restart'] = restart and restart == 'True'
        
        return (headers, data)
        
class SoftHangupRequest(_Message):
    """
    Emitted when a request to terminate the call is exchanged.

    - 'Channel': The channel identifier used by Asterisk
    - 'Cause': The reason for the disconnect, a numeric value as a string:

     - '16': ?
     - '32': ?
     
    - 'Uniqueid': An Asterisk unique value
    """
    
class Status(_Message):
    """
    Describes the current status of a channel.
    
    - 'Account': The billing account associated with the channel; may be empty
    - 'ActionID': The ID associated with the original request
    - 'Channel': The channel being described
    - 'CallerID': The ID of the caller, ".+?" <.+?>
    - 'CallerIDNum': The (often) numeric component of the CallerID
    - 'CallerIDName' (optional): The, on suporting channels, name of the caller, enclosed in quotes
    - 'Context': The context of the directive the channel is executing
    - 'Extension': The extension of the directive the channel is executing
    - 'Link': ?
    - 'Priority': The priority of the directive the channel is executing
    - 'Seconds': The number of seconds the channel has been active
    - 'State': "Up"
    - 'Uniqueid': An Asterisk unique value
    """
    def process(self):
        """
        Translates the 'Seconds' header's value into an int, setting it to -1 on error.
        """
        (headers, data) = _Message.process(self)
        try:
            headers['Seconds'] = int(headers.get('Seconds'))
        except Exception:
            headers['Seconds'] = -1
        return (headers, data)
        
class StatusComplete(_Message):
    """
    Indicates that all requested channel information has been provided.
    
    - 'ActionID': The ID associated with the original request
    """

class UserEvent(_Message):
    """
    Generated in response to the UserEvent request.
    
    - 'ActionID': The ID associated with the original request
    - \*: Any key-value pairs supplied with the request, as strings
    """

class VarSet(_Message):
    """
    Emitted when a variable is set, either globally or on a channel.
    
    - 'Channel' (optional): The channel on which the variable was set, if not global
    - 'Uniqueid': An Asterisk unique value
    - 'Value': The value of the variable, as a string
    - 'Variable': The name of the variable that was set
    """

