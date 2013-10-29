Spammy
======

Overview
--------
This app is designed to detect spam / unwanted posts in web forms.  This
includes comment sections, contact forms and general web based form
submissions.

This is done by using a scoring system similar to how spamassassin detects spam
in e-mail systems.  The rules and scores are configurable and the entire system
works over HTTP in a RESTful style.


Rules
-----

The following rules and scores are installed by default:


| Rule                                                       |         Score |
| ---------------------------------------------------------- | -------------:|
| Contact number contains something other than /[0-9] - ( )/ |         + 1.0 |
| Message portion contains hyperlinks                        |         + 1.0 |
| Field contains an empty string (score is per empty field)  |         + 0.2 |
| No contact details exist at all                            |         + 1.0 |
| Message contains a hyperlink that is on the URLBL          |         + 1.5 |
| Remote IP is on a realtime blacklist                       |         + 0.5 |
| No rDNS (PTR) record for remote IP                         |         + 0.5 |
| No valid MX record for domain in e-mail address            |         + 1.5 |
| Message contains phrases commonly used in spam             |         + 1.0 |
| Sender e-mail address matches domain in URL                |         - 2.0 |
| Naïve Bayesian text classifier                             | -1.0 to + 1.0 |


Once a submission is sent to Spammy it will respond with the total score, made
up of each triggered rule above.  The user can then decide to discard,
quarantine or allow the form submission based on their threshold.  The
recommended threshold is 3.0 (anything above this is probably spam).


Usage
-----

Spammy requires a JSON encoded message in the following format:

    {
       'url': [Fully qualified URL of form, eg: http://www.ips.co.za/contact],
       'remote_ip': [remote IP address of form sumitter, eg: 192.168.1.2],
       'name': [Full name, eg: 'John Smith'],
       'email': [Email address, eg: 'john@smith.me'],
       'contact_number': [Contact number (cell/tel), eg: '(031) 266 0035'], 
       'message': [The entire message as submitted by the user, eg: 'Hello']
    }

If a field is unavailable it MUST be sent as null.  A blank string represents a
blank field from the form which is used in the scoring process.


spammyc (the Spammy client library)
-----------------------------------
There is a python library available, wrapping up all functionality of Spammy
in a simple to use interface.  This library will attempt to get a score from
Spammy - if the connection times out, then a score of -100 is returned, which
represents an error condition.

    >>> import spammyc
    >>> import json
    >>> data = {
    ...    'url': 'http://www.domain.com/schedule-viewing/',
    ...    'remote_ip': 192.168.1.2,
    ...    'name': 'John Smith',
    ...    'email': 'john@smith.me',
    ...    'contact_number': 'wkjebgkwjebg', 
    ...    'message': 'Foo'
    ... }
    >>> spammyc.score(data)
    3.0
    >>>


Plain HTTP
----------
You can also interact with Spammy over plain text HTTP, an example using curl
is included below:

    $ curl -X "{'url':'http://www.domain.com/schedule-viewing/','remote_ip':192.168.1.2,'name':'John Smith','email':'john@smith.me','contact_number':'wkjebgkwjebg','message':'Foo'}" http://spammy.clickhappen.com/score
