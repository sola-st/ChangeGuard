def _identityVerifyingInfoCallback(self, connection, where, ret):
    if where & SSL.SSL_CB_HANDSHAKE_START:
        set_tlsext_host_name(connection, self._hostnameBytes)
    elif where & SSL.SSL_CB_HANDSHAKE_DONE:
        if self.verbose_logging:
            logger.debug('SSL connection to %s using protocol %s, cipher %s',
                         self._hostnameASCII,
                         connection.get_protocol_version_name(),
                         connection.get_cipher_name(),
                         )
            server_cert = connection.get_peer_certificate()
            logger.debug('SSL connection certificate: issuer "%s", subject "%s"',
                         x509name_to_string(server_cert.get_issuer()),
                         x509name_to_string(server_cert.get_subject()),
                         )
            key_info = get_temp_key_info(connection._ssl)
            if key_info:
                logger.debug('SSL temp key: %s', key_info)
        try:
            verifyHostname(connection, self._hostnameASCII)
        except (CertificateError, VerificationError) as e:
            logger.warning(
                'Remote certificate is not valid for hostname "{}"; {}'.format(
                    self._hostnameASCII, e))
        except ValueError as e:
            logger.warning(
                'Ignoring error while verifying certificate '
                'from host "{}" (exception: {})'.format(
                    self._hostnameASCII, repr(e)))
