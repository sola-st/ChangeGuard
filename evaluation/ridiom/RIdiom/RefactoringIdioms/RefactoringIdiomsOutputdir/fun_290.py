def requestTunnel(self, protocol):
    tunnelReq = (
        b'CONNECT ' +
        to_bytes(self._tunneledHost, encoding='ascii') + b':' +
        to_bytes(str(self._tunneledPort)) +
        b' HTTP/1.1\r\n')
    if self._proxyAuthHeader:
        tunnelReq += \
                b'Proxy-Authorization: ' + self._proxyAuthHeader + b'\r\n'
    tunnelReq += b'\r\n'
    protocol.transport.write(tunnelReq)
    self._protocolDataReceived , protocol.dataReceived  = protocol.dataReceived, self.processProxyResponse
    self._protocol = protocol
    return protocol
