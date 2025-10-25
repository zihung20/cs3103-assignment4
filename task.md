Assignment 4

Objectives: develop an API that for developers to mark the reliability, something like sendpack(is_reliable, bytes[])

underlying protocol: QUIC

Task
1. define reliable & unreliable protocol: header, how it works
    a. reliable: retransmission time, buffering, reordering for both sender and receiver

    b. unreliable: maybe lower the threshold, for both sender and receivere

2. quic stream as channel, reliable 1 stream and unreliable another stream

3. setup network real-world simulation