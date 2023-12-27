# A library for 433MHz remote control

Remote controlled wall sockets provide a convenient way to control power to
electrical equipment.

### Examples

Receiver: copy the `rx` directory and contents to the target's filesystem. Then import it as:

    from rx import RX

    recv = RX(23)

    while True:
        res = recv.read(999)
        print(res)

Transmitter: copy the `tx` directory and contents to the target's filesystem. Then import it as:

    from tx import TX
    import time

    trans = TX(23)

    while True:
        trans.send("Hola Mundo")
        time.sleep(0.5)

Named arguments:
- baud_rate: Default is 2400. Less than that proved to be unreliable in most devices.
- parity: Default is 0. Options: `None | 0 | 1`

Example: `recv = RX(23, baud_rate=3200, parity=None)`
