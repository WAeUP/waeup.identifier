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
import xmlrpc.client


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
    result = server_proxy.put_student_fingerprints(
        student_id, {str(finger_num): data_to_store})
    return result
