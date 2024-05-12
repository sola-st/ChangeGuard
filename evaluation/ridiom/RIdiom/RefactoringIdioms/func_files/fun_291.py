def requestTunnel(self, protocol):
    tunnelReq = to_bytes(
        'CONNECT %s:%s HTTP/1.1\r\n' % (
            self._tunneledHost, self._tunneledPort), encoding='ascii')
    if self._proxyAuthHeader:
        tunnelReq += \
                b'Proxy-Authorization: ' + self._proxyAuthHeader + b'\r\n'
    tunnelReq += b'\r\n'
    protocol.transport.write(tunnelReq)
    self._protocolDataReceived = protocol.dataReceived
    protocol.dataReceived = self.processProxyResponse
    self._protocol = protocol
    return protocol
