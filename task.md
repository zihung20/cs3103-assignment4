Assignment 4

Objectives: develop an API that for developers to mark the reliability, something like sendpack(is_reliable, bytes[])

underlying protocol: QUIC

Main Direction: provide API such that game layer can utilize it for sending and receiving the data

Task
1. define reliable & unreliable protocol: header, how it works
    a. reliable: retransmission time, buffering, reordering for both sender and receiver
        skip after t ms
        
    b. unreliable: maybe lower the threshold, for both sender and receivere

    c. general: sequence number so that we know how many packets are drop using this, stream for each services
        based on data, decide what is the stream channel id and what protocol

2. quic stream as channel, reliable 1 stream and unreliable another stream

3. calculate metrics, use customized header that help our servers to calculate. (thought) Client may also need to receive echo for RTT

4. setup network real-world simulation