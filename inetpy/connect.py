"""Resolves name and connects socket with IPv4/IPv6 portability"""


import logging
import socket



g_log = logging.getLogger(__name__)



def connect_tcp(host, port):
  """Establish a TCP/IP connection

  :returns: A successfully-connected socket
  :rtype: socket.socket

  :raises socket.gaierror: address resolution error
  :raises socket.error: socket connection error
  """
  infos = socket.getaddrinfo(host,
                             port,
                             0, # family
                             0, # socktype
                             socket.IPPROTO_TCP,
                             0) # flags
  return connect_from_addr_infos(infos)



def connect_from_addr_infos(infos):
  """Given a sequence of elements generated by `socket.getaddrinfo`, attempt
  connection to each one of them in the given order.

  :param infos: sequence of tuples that are compatible with the results returned
    by `socket.getaddrinfo`

  :returns: A successfully-connected socket; None if given an empty sequence
  :rtype: socket.socket or None

  :socket.error:
  """
  if not infos:
    return None

  for count, res in enumerate(infos, 1):
    family, socktype, proto, _canonname, address = res

    # Attempt to create a socket
    try:
      sock = socket.socket(family, socktype, proto)
    except socket.error:
      if count < len(infos):
        g_log.debug("socket.socket(%r, %r, %r) failed", family, socktype, proto,
                    exc_info=True)
        continue
      else:
        raise

    # Attempt to connect
    try:
      sock.connect(address)
    except socket.error:
      sock.close()
      sock = None

      if count < len(infos):
        g_log.debug("sock.connect(%r) failed", address, exc_info=True)
        continue
      else:
        raise
    else:
      return sock


  # Should never get here!
  raise RuntimeError("Failed to connect, but didn't raise; infos: %r"
                     % (infos,))
