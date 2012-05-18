Asterisk Gateway Interface (AGI)
================================

A simple AGI implementation is provided below, demonstrating how to handle requests from Asterisk,
like, as illustrated, answering a call, playing a message, and hanging up::

    #!/usr/bin/env python
    import pystrix
    
    if __name__ == '__main__':
        agi = pystrix.agi.AGI()
        
        agi.execute(pystrix.agi.core.Answer()) #Answer the call
        
        response = agi.execute(pystrix.agi.core.StreamFile('demo-thanks', escape_digits=('1', '2'))) #Play a file; allow DTMF '1' or '2' to interrupt
        if response: #Playback was interrupted; if you don't care, you don't need to catch this
            (dtmf_character, offset) = response #The key pressed by the user and the playback time
            
        agi.execute(pystrix.agi.core.Hangup()) #Hang up the call
        
