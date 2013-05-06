"""Wrapper to call Phabricator's users Conduit API"""

import collections
import unittest

import phldef_conduit
import phlsys_conduit


def _makeNT(name, *fields):
    return collections.namedtuple('phlcon_user__' + name, fields)


QueryResponse = _makeNT(
    'QueryResponse',
    'phid', 'userName', 'realName', 'image', 'uri', 'roles')


def isNoSuchUserError(e):
    """Return True if the supplied ConduitException is due to unrecognised user

    :e: a ConduitException
    :returns: True if the supplied ConduitException is due to unrecognised user

    """
    errConduitCore = "ERR-CONDUIT-CORE"
    noSuchEmail = ""
    noSuchEmail += "Array for %Ls conversion is empty. "
    noSuchEmail += "Query: SELECT * FROM %s WHERE userPHID IN (%Ls) "
    noSuchEmail += "AND UNIX_TIMESTAMP() BETWEEN dateFrom AND dateTo %Q"
    return e.error == errConduitCore and e.errormsg == noSuchEmail


def queryUserFromEmail(conduit, email):
    """Return a QueryResponse based on the provided emails.

    If the email does not correspond to a username then return None.

    :conduit: must support 'call()' like phlsys_conduit
    :email: an email address as a string
    :returns: a QueryResponse or None

    """
    d = {"emails": [email]}
    response = None
    try:
        response = conduit.call("user.query", d)
    except phlsys_conduit.ConduitException as e:
        if not isNoSuchUserError(e):
            raise

    if response:
        if len(response) != 1:
            raise Exception("unexpected number of entries")
        return QueryResponse(**response[0])
    else:
        return None


def queryUsersFromEmails(conduit, emails):
    """Return a list of username strings based on the provided emails.

    If an email does not correspond to a username then None is inserted in
    its place.

    :conduit: must support 'call()' like phlsys_conduit
    :emails: a list of strings corresponding to user email addresses
    :returns: a list of strings corresponding to Phabricator usernames

    """
    users = []
    for e in emails:
        u = queryUserFromEmail(conduit, e)
        if u is not None:
            users.append(u.userName)
        else:
            users.append(None)
    return users


def queryUsersFromPhids(conduit, phids):
    """Return a list of QueryResponse based on the provided phids.

    If a phid does not correspond to a username then raise ValueError.

    :conduit: must support 'call()' like phlsys_conduit
    :phids: a list of strings corresponding to user phids
    :returns: a list of QueryResponse

    """
    if not isinstance(phids, list):
        raise ValueError("phids must be a list")
    d = {"phids": phids}
    response = conduit.call("user.query", d)

    if len(response) != len(phids):
        raise Exception("unexpected number of entries")

    return [QueryResponse(**u) for u in response]


def queryUsersFromUsernames(conduit, usernames):
    """Return a list of QueryResponse based on the provided usernames.

    Return None if any of 'usernames' is invalid.

    :conduit: must support 'call()' like phlsys_conduit
    :usernames: a list of strings corresponding to usernames
    :returns: a list of QueryResponse

    """
    assert isinstance(usernames, list)
    d = {"usernames": usernames}

    response = None
    try:
        response = conduit.call("user.query", d)
    except phlsys_conduit.ConduitException as e:
        if not isNoSuchUserError(e):
            raise

    if response is None:
        return None

    if len(response) != len(usernames):
        raise Exception("unexpected number of entries")

    return [QueryResponse(**u) for u in response]


def queryUsernamesFromPhids(conduit, phids):
    """Return a list of username strings based on the provided phids.

    If a phid does not correspond to a username then raise.

    :conduit: must support 'call()' like phlsys_conduit
    :phids: a list of strings corresponding to user phids
    :returns: a list of strings corresponding to Phabricator usernames

    """
    users = queryUsersFromPhids(conduit, phids)
    return [u.userName for u in users]


def makeUsernamePhidDict(conduit, usernames):
    """Return a dictionary of usernames to phids.

    Return None if any of 'usernames' is invalid.

    :conduit: must support 'call()' like phlsys_conduit
    :usernames: a list of strings corresponding to Phabricator usernames
    :returns: a dictionary of usernames to corresponding phids

    """
    users = queryUsersFromUsernames(conduit, usernames)
    if users is None:
        return None
    else:
        return {u.userName: u.phid for u in users}


class TestUser(unittest.TestCase):

    def setUp(self):
        test_data = phldef_conduit
        self.conduit = phlsys_conduit.Conduit(
            test_data.test_uri,
            test_data.alice.user,
            test_data.alice.certificate)
        self.test_user = phldef_conduit.alice.user
        self.test_email = phldef_conduit.alice.email

    def testAliceEmail(self):
        users = queryUsersFromEmails(self.conduit, [self.test_email])
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], self.test_user)

        user = queryUserFromEmail(self.conduit, self.test_email)
        self.assertEqual(user.userName, self.test_user)

        phidUsers = queryUsersFromPhids(self.conduit, [user.phid])
        self.assertEqual(phidUsers[0].userName, self.test_user)

        phidUsernames = queryUsernamesFromPhids(self.conduit, [user.phid])
        self.assertEqual(phidUsernames[0], self.test_user)

    def testAliceAndNooneEmail(self):
        emails = [self.test_email, "noone@server.invalid", "a@server.invalid"]
        users = queryUsersFromEmails(self.conduit, emails)
        self.assertEqual(len(users), 3)
        self.assertListEqual(users, [self.test_user, None, None])

    def testAliceUsername(self):
        users = queryUsersFromUsernames(self.conduit, [self.test_user])
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].userName, self.test_user)

        userDict = makeUsernamePhidDict(self.conduit, [self.test_user])
        self.assertEqual(len(userDict), 1)
        self.assertEqual(userDict[self.test_user], users[0].phid)

    def testBadUsername(self):
        bad_username = "#@)4308f:"
        users = queryUsersFromUsernames(self.conduit, [bad_username])
        self.assertIsNone(users)

        userDict = makeUsernamePhidDict(self.conduit, [bad_username])
        self.assertIsNone(userDict)


if __name__ == "__main__":
    unittest.main()

#------------------------------------------------------------------------------
# Copyright (C) 2012 Bloomberg L.P.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#------------------------------- END-OF-FILE ----------------------------------