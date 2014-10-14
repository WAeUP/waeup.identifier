#
#    waeup.identifier - identifiy WAeUP Kofa students biometrically
#    Copyright (C) 2014  Uli Fouquet, WAeUP Germany
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""Connect to WAeUP kofa via webservices.
"""
import urllib.parse
import xmlrpc.client


def get_url(netlocation, username, password):
    """Create a valid URL from the given parts.

    The username and password are inserted into the netlocation to
    build a valid URL. The `netlocation` should be a valid URL w/o any
    username/password.

    If no scheme is given in netlocation, ``https://`` is returned.

    Example:

       >>> get_url('localhost:8080', 'bob', 'secret')
       'https://bob:secret@localhost:8080'
    """
    parts = urllib.parse.urlparse(netlocation, scheme="https")
    parts_list = [x for x in tuple(parts)]
    if parts_list[1] == '':
        del parts_list[1]
        parts_list += ['',]
        parts_list = [x for x in parts_list]
    parts_list[1] = "%s:%s@" % (username, password) + parts_list[1]
    return urllib.parse.urlunparse(parts_list)


def get_url_from_config(config):
    """Construct a valid XMLRPC URL from `config`.

    `config` is expected to be an instance of ConfigParser as used,
    for instance, in the main application.

    Returns a valid URL usable to do XMLRPC requests.
    """
    netloc = config.get("DEFAULT", "waeup_url")
    username = config.get("DEFAULT", "waeup_user")
    password = config.get("DEFAULT", "waeup_passwd")
    return get_url(netloc, username, password)


def store_fingerprint(url, student_id, finger_num, data_file_path):
    """Store a fingerprint on a Kofa server.

    Returns `None` on success or some message otherwise.

    `url` is the Kofa server to connect to. It must contain a scheme
    (``http://`` or ``https://``), a username, password, and of course
    the hostname and port. Something like
    ``http://myname:secret@localhost:8080``, for instance.

    `student_id` must be a student identifier existing on the server.

    `finger_num` is the number of finger that was scanned.

    `data_file_path` is the path to a file that contains the
    fingerprint minutiae, i.e. the fingerprint data as produced by
    libfprint.
    """
    server_proxy = xmlrpc.client.ServerProxy(url)
    data_to_store = xmlrpc.client.Binary(open(data_file_path, 'rb').read())
    #import pdb; pdb.set_trace()
    fingerprint = {str(finger_num): data_to_store}
    result = None
    try:
        result = server_proxy.put_student_fingerprints(
            student_id, fingerprint)
    except xmlrpc.client.Fault:
        print("FAULT")
        import sys
        e = sys.exc_info()
        print(e, dir(e))
        result = "Error %s: %s" % (e[1].faultCode, e[1].faultString)
    #import pdb; pdb.set_trace
    print("AFTER EXCEPT")
    print(result)
    return result
