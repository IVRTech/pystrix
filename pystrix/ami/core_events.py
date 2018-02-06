"""
pystrix.ami.core_events
=======================

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
import re

from pystrix.ami.ami import (_Aggregate, _Event)
from pystrix.ami import generic_transforms

class AGIExec(_Event):
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
        (headers, data) = _Event.process(self)
        
        generic_transforms.to_bool(headers, ('Result',), truth_value='Success')
        generic_transforms.to_int(headers, ('ResultCode',), -1)
        
        return (headers, data)
        
class AsyncAGI(_Event):
    """
    Generated when an AGI request is processed.
    
    - All fields currently unknown
    """
    
class ChannelUpdate(_Event):
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
    
class CoreShowChannel(_Event):
    """
    Provides the definition of an active Asterisk channel.
    
    - 'AccountCode': The account code associated with the channel
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
    - 'UniqueID': An Asterisk-unique value (the timestamp at which the channel was connected?)
    """
    def process(self):
        """
        Translates the 'ChannelState' header's value into an int, setting it to `None` if coercion
        fails.
        
        Replaces the 'Duration' header's value with the number of seconds, as an int, or -1 if
        conversion fails.
        """
        (headers, data) = _Event.process(self)
        
        try:
            (h, m, s) = (int(v) for v in headers['Duration'].split(':'))
            headers['Duration'] = s + m * 60 + h * 60 * 60
        except Exception:
            headers['Duration'] = -1
            
        generic_transforms.to_int(headers, ('ChannelState',), None)
        
        return (headers, data)
        
class CoreShowChannelsComplete(_Event):
    """
    Indicates that all Asterisk channels have been listed.
    
    - 'ListItems' : The number of items returned prior to this event
    """
    def process(self):
        """
        Translates the 'ListItems' header's value into an int, or -1 on failure.
        """
        (headers, data) = _Event.process(self)
        
        generic_transforms.to_int(headers, ('ListItems',), -1)
        
        return (headers, data)
        
class DBGetResponse(_Event):
    """
    Provides the value requested from the database.
    
    - 'Family': The family of the value being provided
    - 'Key': The key of the value being provided
    - 'Val': The value being provided, represented as a string
    """

class DTMF(_Event):
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
        (headers, data) = _Event.process(self)
        
        headers['Received'] = headers.get('Direction') == 'Received'
        generic_transforms.to_bool(headers, ('Begin', 'End',), truth_value='Yes')
        
        return (headers, data)
        
class FullyBooted(_Event):
    """
    Indicates that Asterisk is online.
    
    - 'Status': "Fully Booted"
    """
    
class Hangup(_Event):
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
        (headers, data) = _Event.process(self)
        generic_transforms.to_int(headers, ('Cause',), None)
        return (headers, data)

class HangupRequest(_Event):
    """
    Emitted when a request to terminate the call is received.

    - 'Channel': The channel identifier used by Asterisk
    - 'Uniqueid': An Asterisk unique value
    """

class MonitorStart(_Event):
    """
    Indicates that monitoring has begun.
    
    - 'Channel': The channel being monitored
    - 'Uniqueid': An Asterisk unique value
    """

class MonitorStop(_Event):
    """
    Indicates that monitoring has ceased.
    
    - 'Channel': The channel that was monitored
    - 'Uniqueid': An Asterisk unique value
    """

class NewAccountCode(_Event):
    """
    Indicates that the account-code associated with a channel has changed.
    
    - 'AccountCode': The new account code
    - 'Channel': The channel that was affected.
    - 'OldAccountCode': The old account code
    """

class Newchannel(_Event):
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
        (headers, data) = _Event.process(self)
        generic_transforms.to_int(headers, ('ChannelState',), None)
        return (headers, data)

class Newexten(_Event):
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

class Newstate(_Event):
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
        (headers, data) = _Event.process(self)
        generic_transforms.to_int(headers, ('ChannelState',), None)
        return (headers, data)
        
class OriginateResponse(_Event):
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
        (headers, data) = _Event.process(self)
        generic_transforms.to_int(headers, ('Reason',), -1)
        return (headers, data)
        
class ParkedCall(_Event):
    """
    Describes a parked call.
    
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
        (headers, data) = _Event.process(self)
        if 'Timeout' in headers:
            generic_transforms.to_int(headers, ('Timeout',), None)
        return (headers, data)
        
class ParkedCallsComplete(_Event):
    """
    Indicates that all parked calls have been listed.
    
    - 'Total' : The number of items returned prior to this event
    """
    def process(self):
        """
        Translates the 'Total' header's value into an int, or -1 on failure.
        """
        (headers, data) = _Event.process(self)
        generic_transforms.to_int(headers, ('Total',), -1)
        return (headers, data)

class PeerEntry(_Event):
    """
    Describes a peer.
    
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
    - 'Status': 'Unmonitored', 'OK (\\d+ ms)'
    - 'RealtimeDevice': 'yes' or 'no'
    """
    def process(self):
        """
        Translates the 'Port' header's value into an int, setting it to `None` if coercion
        fails, and leaving it absent if it wasn't present in the original response.
        
        Translates the 'Dynamic', 'Natsupport', 'VideoSupport', 'ACL', and 'RealtimeDevice' headers'
        values into bools.
        
        Translates 'Status' into the number of milliseconds since the peer was last seen or -2 if
        unmonitored. -1 if parsing failed.
        """
        (headers, data) = _Event.process(self)
        
        try:
            if headers['Status'] == 'Unmonitored':
                headers['Status'] = -2
            else:
                headers['Status'] = int(re.match(r'OK \((\d+) ms\)', headers['Status']).group(1))
        except Exception:
            headers['Status'] = -1
            
        if 'IPport' in headers:
            generic_transforms.to_int(headers, ('IPPort',), None)
            
        generic_transforms.to_bool(headers, ('Dynamic', 'Natsupport', 'VideoSupport', 'ACL', 'RealtimeDevice'), truth_value='yes')
        
        return (headers, data)

class PeerlistComplete(_Event):
    """
    Indicates that all peers have been listed.
    
    - 'ListItems' : The number of items returned prior to this event
    """
    def process(self):
        """
        Translates the 'ListItems' header's value into an int, or -1 on failure.
        """
        (headers, data) = _Event.process(self)
        generic_transforms.to_int(headers, ('ListItems',), -1)
        return (headers, data)

class QueueEntry(_Event):
    """
    Indicates that a call is waiting to be answered.
    
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
        (headers, data) = _Event.process(self)
        generic_transforms.to_int(headers, ('Position', 'Wait',), -1)
        return (headers, data)

class QueueMember(_Event):
    """
    Describes a member of a queue.
    
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
        (headers, data) = _Event.process(self)
        generic_transforms.to_bool(headers, ('Paused',), truth_value='1')
        generic_transforms.to_int(headers, ('CallsTaken', 'LastCall', 'Penalty', 'Status',), -1)
        return (headers, data)
        
class QueueMemberAdded(_Event):
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
        (headers, data) = _Event.process(self)
        generic_transforms.to_bool(headers, ('Paused',), truth_value='1')
        generic_transforms.to_int(headers, ('CallsTaken', 'LastCall', 'Penalty', 'Status',), -1)
        return (headers, data)
        
class QueueMemberPaused(_Event):
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
        (headers, data) = _Event.process(self)
        generic_transforms.to_bool(headers, ('Paused',), truth_value='1')
        return (headers, data)

class QueueMemberRemoved(_Event):
    """
    Indicates that a member was removed from a queue.
    
    - 'Location': The interface removed from the queue
    - 'MemberName' (optional): The friendly name of the member
    - 'Queue': The queue from which the member was removed
    """
    
class QueueParams(_Event):
    """
    Describes the attributes of a queue.
    
    - 'Abandoned': The number of calls that have gone unanswered
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
        (headers, data) = _Event.process(self)
        generic_transforms.to_int(headers, ('Abandoned', 'Calls', 'Completed', 'Holdtime', 'Max',), -1)
        generic_transforms.to_float(headers, ('ServiceLevel', 'ServiceLevelPref', 'Weight',), -1)
        return (headers, data)
        
class QueueStatusComplete(_Event):
    """
    Indicates that a QueueStatus request has completed.
    """

class QueueSummary(_Event):
    """
    Describes a Summary of a queue. Example:

        - Event: QueueSummary
        - Queue: default
        - LoggedIn: 0
        - Available: 0
        - Callers: 0
        - HoldTime: 0
        - TalkTime: 0
        - LongestHoldTime: 0
        - Event: QueueSummaryComplete
        - EventList: Complete
        - ListItems: 2
    """

    def process(self):
        """
            Translates the 'LoggedIn', 'Available', 'Callers', 'Holdtime', 'TalkTime' and 'LongestHoldTime' headers'
            values into ints, setting them to -1 on error.
        """
        (headers, data) = _Event.process(self)
        generic_transforms.to_int(headers, ('LoggedIn', 'Available', 'Callers', 'HoldTime', 'TalkTime',
                                            'LongestHoldTime'), -1)
        return (headers, data)


class QueueSummaryComplete(_Event):
    """
    Indicates that a QueueSummary request has completed.
    """


class RegistryEntry(_Event):
    """
    Describes a SIP registration.
    
    - 'Domain': The domain in which the registration took place
    - 'DomainPort': The port in use in the registration domain
    - 'Host': The address of the host
    - 'Port': The port in use on the host
    - 'Refresh': The amount of time remaining until the registration will be renewed
    - 'RegistrationTime': The time at which the registration was made, as a UNIX timestamp
    - 'State': The current status of the registration
    - 'Username': The username used for the registration
    """
    def process(self):
        """
        Translates the 'DomainPort', 'Port', 'Refresh', and 'RegistrationTime' values into ints,
        setting them to -1 on error.
        """
        (headers, data) = _Event.process(self)
        generic_transforms.to_int(headers, ('DomainPort', 'Port', 'Refresh', 'RegistrationTime',), -1)
        return (headers, data)
        
class RegistrationsComplete(_Event):
    """
    Indicates that all registrations have been listed.
    
    - 'ListItems' : The number of items returned prior to this event
    """
    def process(self):
        """
        Translates the 'ListItems' header's value into an int, or -1 on failure.
        """
        (headers, data) = _Event.process(self)
        generic_transforms.to_int(headers, ('ListItems',), -1)
        return (headers, data)
        
class Reload(_Event):
    """
    Indicates that Asterisk's configuration was reloaded.
    
    - 'Message': A human-readable summary
    - 'Module': The affected module
    - 'Status': 'Enabled'
    """
    
class RTCPReceived(_Event):
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
        (headers, data) = _Event.process(self)
        
        _from = headers.get('From')
        if _from and ':' in _from:
            headers['From'] = tuple(_from.rsplit(':', 1))
        else:
            headers['From'] = None
            
        generic_transforms.to_int(headers, ('HighestSequence', 'LastSR', 'PacketsLost', 'ReceptionReports', 'SequenceNumberCycles',), -1)
        headers['DLSR'] = (headers.get('DSLR') or '').split(' ', 1)[0]
        generic_transforms.to_float(headers, ('DLSR', 'FractionLost', 'IAJitter',), -1)
        
        return (headers, data)

class RTCPSent(_Event):
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
        (headers, data) = _Event.process(self)
        
        to = headers.get('To')
        if to and ':' in to:
            headers['To'] = tuple(to.rsplit(':', 1))
        else:
            headers['To'] = None
            
        generic_transforms.to_bool(headers, ('Result',), truth_value='Success')
        generic_transforms.to_int(headers, ('CumulativeLoss', 'SentOctets', 'SentPackets', 'SentRTP', 'TheirLastSR',), -1)
        headers['DLSR'] = (headers.get('DSLR') or '').split(' ', 1)[0]
        generic_transforms.to_float(headers, ('DLSR', 'FractionLost', 'IAJitter', 'SentNTP',), -1)
            
        return (headers, data)

class Shutdown(_Event):
    """
    Emitted when Asterisk shuts down.
    
    - 'Restart': "True" or "False"
    - 'Shutdown': "Cleanly"
    """
    def process(self):
        """
        'Restart' is set to a bool.
        """
        (headers, data) = _Event.process(self)
        generic_transforms.to_bool(headers, ('Restart',), truth_value='True')
        return (headers, data)
        
class SoftHangupRequest(_Event):
    """
    Emitted when a request to terminate the call is exchanged.

    - 'Channel': The channel identifier used by Asterisk
    - 'Cause': The reason for the disconnect, a numeric value as a string:

     - '16': ?
     - '32': ?
     
    - 'Uniqueid': An Asterisk unique value
    """
    
class Status(_Event):
    """
    Describes the current status of a channel.
    
    - 'Account': The billing account associated with the channel; may be empty
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
        (headers, data) = _Event.process(self)
        generic_transforms.to_int(headers, ('Seconds',), -1)
        return (headers, data)
        
class StatusComplete(_Event):
    """
    Indicates that all requested channel information has been provided.
    
    - 'Items': The number of items emitted prior to this event
    """
    def process(self):
        """
        Translates the 'Items' header's value into an int, or -1 on failure.
        """
        (headers, data) = _Event.process(self)
        generic_transforms.to_int(headers, ('Items',), -1)
        return (headers, data)

class UserEvent(_Event):
    """
    Generated in response to the UserEvent request.
    
    - \*: Any key-value pairs supplied with the request, as strings
    """

class VarSet(_Event):
    """
    Emitted when a variable is set, either globally or on a channel.
    
    - 'Channel' (optional): The channel on which the variable was set, if not global
    - 'Uniqueid': An Asterisk unique value
    - 'Value': The value of the variable, as a string
    - 'Variable': The name of the variable that was set
    """

class VoicemailUserEntry(_Event):
    """
    Describes a voicemail user.
    
    - 'AttachMessage': "Yes", "No"
	- 'AttachmentFormat': unknown
	- 'CallOperator': "Yes", "No"
	- 'CanReview': "Yes", "No"
    - 'Callback': unknown
    - 'DeleteMessage': "Yes", "No"
    - 'Dialout': unknown
    - 'Email': unknown
    - 'ExitContext': The context to use when leaving the mailbox
    - 'Fullname': unknown
    - 'IMAPFlags': Any associated IMAP flags (IMAP only)
	- 'IMAPPort': The associated IMAP port (IMAP only)
	- 'IMAPServer': The associated IMAP server (IMAP only)
	- 'IMAPUser': The associated IMAP username (IMAP only)
	- 'Language': The language to use for voicemail prompts
	- 'MailCommand': unknown
	- 'MaxMessageCount': The maximum number of messages that can be stored
	- 'MaxMessageLength': The maximum length of any particular message
	- 'NewMessageCount': The number of unheard messages
	- 'OldMessageCount': The number of previously heard messages (IMAP only)
	- 'Pager': unknown
    - 'SayCID': "Yes", "No"
    - 'SayDurationMinimum': The minumum amount of time a message may be
    - 'SayEnvelope': "Yes", "No"
    - 'ServerEmail': unknown
    - 'TimeZone': The timezone of the mailbox
    - 'UniqueID': unknown
	- 'VMContext': The associated Asterisk context
	- 'VoiceMailbox': The associated mailbox
	- 'VolumeGain': A floating-point value
    """
    def process(self):
        """
        Translates the 'MaxMessageCount', 'MaxMessageLength', 'NewMessageCount', 'OldMessageCount',
        and 'SayDurationMinimum' values into ints, setting them to -1 on error.

        Translates the 'VolumeGain' value into a float, setting it to None on error.
        
        Translates the 'AttachMessage', 'CallOperator', 'CanReview', 'DeleteMessage', 'SayCID', and
        'SayEnvelope' values into booleans.
        """
        (headers, data) = _Event.process(self)
        
        generic_transforms.to_bool(headers, ('AttachMessage', 'CallOperator', 'CanReview', 'DeleteMessage', 'SayCID', 'SayEnvelope',), truth_value='Yes')
        header_list = ['MaxMessageCount', 'MaxMessageLength', 'NewMessageCount', 'SayDurationMinimum']
        if 'OldMessageCount' in headers:
            header_list.append('OldMessageCount')
        generic_transforms.to_int(headers, header_list, -1)
        generic_transforms.to_float(headers, ('VolumeGain',), None)
        
        return (headers, data)
    
class VoicemailUserEntryComplete(_Event):
    """
    Indicates that all requested voicemail user definitions have been provided.
    
    No, its name is not a typo; it's really "Entry" in Asterisk's code.
    """
    
    
#List-aggregation events
####################################################################################################
#These define non-Asterisk-native event-types that collect multiple events (cases where multiple
#events are generated in response to a single action) and emit the bundle as a single message.

class CoreShowChannels_Aggregate(_Aggregate):
    """
    Emitted after all channels have been received in response to a CoreShowChannels request.
    
    Its members consist of CoreShowChannel events.
    
    It is finalised by CoreShowChannelsComplete.
    """
    _name = "CoreShowChannels_Aggregate"
    
    _aggregation_members = (CoreShowChannel,)
    _aggregation_finalisers = (CoreShowChannelsComplete,)
    
    def _finalise(self, event):
        self._check_list_items_count(event, 'ListItems')
        return _Aggregate._finalise(self, event)
        
class ParkedCalls_Aggregate(_Aggregate):
    """
    Emitted after all parked calls have been received in response to a ParkedCalls request.
    
    Its members consist of ParkedCall events.
    
    It is finalised by ParkedCallsComplete.
    """
    _name = "ParkedCalls_Aggregate"
    
    _aggregation_members = (ParkedCall,)
    _aggregation_finalisers = (ParkedCallsComplete,)
    
    def _finalise(self, event):
        self._check_list_items_count(event, 'Total')
        return _Aggregate._finalise(self, event)
        
class QueueStatus_Aggregate(_Aggregate):
    """
    Emitted after all queue properties have been received in response to a QueueStatus request.
    
    Its members consist of QueueParams, QueueMember, and QueueEntry events.
    
    It is finalised by QueueStatusComplete.
    """
    _name = "QueueStatus_Aggregate"
    
    _aggregation_members = (QueueParams, QueueMember, QueueEntry,)
    _aggregation_finalisers = (QueueStatusComplete,)


class QueueSummary_Aggregate(_Aggregate):
    """
    Emitted after all queue properties have been received in response to a QueueSummary request.

    Its members consist of QueueSummary events.

    It is finalised by QueueSummaryComplete.
    """
    _name = "QueueSummary_Aggregate"

    _aggregation_members = (QueueSummary,)
    _aggregation_finalisers = (QueueSummaryComplete,)
	

class SIPpeers_Aggregate(_Aggregate):
    """
    Emitted after all queue properties have been received in response to a SIPpeers request.

    Its members consist of 'PeerEntry' events.
    
    It is finalised by PeerlistComplete.
    """
    _name = "SIPpeers_Aggregate"
    
    _aggregation_members = (PeerEntry,)
    _aggregation_finalisers = (PeerlistComplete,)
    
    def _finalise(self, event):
        self._check_list_items_count(event, 'ListItems')
        return _Aggregate._finalise(self, event)
        
class SIPshowregistry_Aggregate(_Aggregate):
    """
    Emitted after all SIP registrants have been received in response to a SIPshowregistry request.
    
    Its members consist of RegistryEntry events.
    
    It is finalised by RegistrationsComplete.
    """
    _name = "SIPshowregistry_Aggregate"
    
    _aggregation_members = (RegistryEntry,)
    _aggregation_finalisers = (RegistrationsComplete,)
    
    def _finalise(self, event):
        self._check_list_items_count(event, 'ListItems')
        return _Aggregate._finalise(self, event)
        
class Status_Aggregate(_Aggregate):
    """
    Emitted after all statuses have been received in response to a Status request.
    
    Its members consist of Status events.
    
    It is finalised by StatusComplete.
    """
    _name = "Status_Aggregate"
    
    _aggregation_members = (Status,)
    _aggregation_finalisers = (StatusComplete,)
    
    def _finalise(self, event):
        self._check_list_items_count(event, 'Items')
        return _Aggregate._finalise(self, event)
        
class VoicemailUsersList_Aggregate(_Aggregate):
    """
    Emitted after all voicemail users have been received in response to a VoicemailUsersList
    request.
    
    Its members consist of VoicemailUserEntry events.
    
    It is finalised by VoicemailUserEntryComplete.
    """
    _name = "VoicemailUsersList_Aggregate"
    
    _aggregation_members = (VoicemailUserEntry,)
    _aggregation_finalisers = (VoicemailUserEntryComplete,)
    
