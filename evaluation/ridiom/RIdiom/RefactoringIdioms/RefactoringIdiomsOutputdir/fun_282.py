def handshakeCompleted(self):
    protocol = self.transport.negotiatedProtocol
    if None is not protocol != b'h2':
        self._lose_connection_with_error([InvalidNegotiatedProtocol(protocol.decode("utf-8"))])
