import base64

import tw.forms as twf
import tw.dynforms as twd
import tw.forms.validators as twv
from tw.api import WidgetsList, CSSSource, JSSource, js_function
from tg import request

from hubreporter.tools.agent import simpledetect

def get_default(x=None):
    default = dict()
    agent_values = simpledetect(request.user_agent)
    default["Request"] = dict (clientinfo = agent_values)
    try:
        reporterinfo = dict( zip(("fname", "lname", "location", "email"), base64.b64decode(request.cookies['uinfo']).split("|")))
        reporterinfo["reporter"] = "%(fname)s %(lname)s" % reporterinfo
        default["Request"]["reporterinfo"] = reporterinfo
        lhs = "%(fname)s.%(lname)s" % reporterinfo
        location_from_cookie = reporterinfo["location"]
        location_lc = reporterinfo["location"].lower()
        mailreq = dict (
                lhs = lhs.lower(),
                maillogin = lhs.lower(),
                publhs = default["Request"]["reporterinfo"]["location"].lower() + ".TOPIC",
                listlhs = default["Request"]["reporterinfo"]["location"].lower() + ".TOPIC",
                mldescr = "Hub %(location)s TOPIC mailing list" % reporterinfo,
                mladmin = "%s.hosts@the-hub.net" % location_lc,
                mlqueries = "%s.hosts@the-hub.net" % location_lc,
                mlsubjectprefix = "[Hub %s TOPIC]" % reporterinfo["location"])
        default["Request"]["mailreq"] = mailreq
        if location_from_cookie in locations.values():
            default["Request"]["reporterinfo"]["location"] = [location for location in locations if location_from_cookie == locations[location]][0]
        if x: return mailreq # kind of ugly but quick
    except Exception, err:
        print err
    return default

domain_template = """
<span>
<input xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/"
    type="${type}" name="${name}" class="${css_class}" id="${id}" value="${value}"
py:attrs="attrs" />%s
</span>
"""

whatreqtext = twf.Label(text='What describes your request best?') # default='issue',
summary_field = twf.TextField("summary", label_text="Short summary of the problem", size="50%", help_text="eg. I can't upload an image", validator=twv.NotEmpty, show_error=False)
whatreqopts = (('issue', 'Report an issue (like problem, requirement or feature request)'), ('mailreq', 'Mail address request'))
whatreqmapping = dict (
            issue = ['reporterinfo.reporter', 'reporterinfo.email', 'clientinfo', 'moredetails'],
            mailreq = ['reporterinfo.fname', 'reporterinfo.lname', 'reporterinfo.email', 'moremail', 'mailreq'])
reporterinfotitle = twf.Label('reporterinfotitle', text="About you")
whatreq = twd.HidingRadioButtonList("whatrequest", label_text="What describes your request best?", options=whatreqopts, mapping=whatreqmapping, \
        validator=twv.OneOf(["issue", "mailreq"]), show_error=True)
mailreqopts = (('', ''),
    ('personal', 'Personal Email'),
    ('forward', 'Personal mail address as a simple forwarding'),
    ('pubcontact', 'Public contact address'),
    ('ml', 'Mailing List'))
mailreqmapping = dict ( personal = ['lhs', 'maillogin', 'mobile'],
                        forward = ['lhs', 'forward'],
                        pubcontact = ['publhs', 'emaillist'],
                        ml = ['listlhs', 'mldescr', 'mlsubjectprefix', 'mladmin', 'mlqueries'])
email = twf.TextField(label_text="What's your e-mail address?", is_required=True, show_error=False, validator=twv.All(twv.Email, twv.NotEmpty))
reporter = twf.TextField(label_text="What's your name?", is_required=True, show_error=False)
fname = twf.TextField(label_text="What's your first name?", is_required=True)
lname = twf.TextField(label_text="What's your last name?", is_required=True)
lhs = twf.TextField('lhs', label_text="Requested Address", template=domain_template % "@the-hub.net", validator=twv.NotEmpty)
listlhs = twf.TextField('listlhs', label_text="Requested Address", template=domain_template % "@lists.the-hub.net")
publhs = twf.TextField('publhs', label_text="Requested Address", template=domain_template %"@the-hub.net")
mailreqtype = twd.HidingSingleSelectField('mailreqtype', label_text='Request Type', mapping=mailreqmapping, options=mailreqopts, default="")
mailreqmoreinfo = twf.TextArea('mailreqmoreinfo', label_text="Additional information on this person/address/list")
maillogin = twf.TextField('maillogin', label_text='Requested mailbox login name')
mobile = twf.TextField('mobile', label_text = 'A mobile phone number', help_text='where we can SMS the password to')
forward = twf.TextField('forward', help_text="The mail address to which incoming mail should get forwarded to.", label_text="Existing Email Address")
mldescr = twf.TextField('mldescr', label_text = 'One line description for the mailing list')
mlsubjectprefix = twf.TextField('mlsubjectprefix', label_text='Tag prefixing the subject of each posting')
mladmin = twf.TextField('mladmin', label_text="The mail addresses of the initial administrators/moderators for this mailing list")
mlqueries = twf.TextField('mlqueries', label_text="A contact mail address for questions from subscribers")

class EmailList(twd.GrowingTableFieldSet):
    label_text = "Addresses to forward the mails to public contact"
    help_text = "Press Tab to add more addresses"
    children = [twf.TextField('fwdmail', label_text="Forward to", dotitle="zzz", help_text="Tab to add more..")]

emaillist = EmailList('emaillist')

class MailRequest(twd.HidingTableFieldSet):
    legend = "Mail Address Request"
    suppress_label = True
    get_default = get_default
    children = [
        mailreqtype,
        lhs,
        listlhs,
        publhs,
        emaillist,
        maillogin,
        mobile,
        forward,
        mldescr,
        mlsubjectprefix,
        mladmin,
        mlqueries,
        mailreqmoreinfo,
    ]

project_options = (("space", "Hub Space (Invoicing, space booking, membership management)"),
                   ("website", "Hub Website (microsite, main website)"),
                   ("networks", "Hub Networks (Mailing lists, e-mail, internet, security, printing)"),
                   ("hubplus", "Hub Plus"),
                   ("test", "Test project (Don't use for real issues)"))

hide_mappings = dict(space = ['os', 'browser', 'url'],
                    website = ['os', 'browser', 'url'],
                    hubplus = ['os', 'browser', 'url'],
                    test = ['os', 'browser', 'url'])


mailreqrepeater = twd.GrowingRepeater('moremail', button_text='Add more requests..', widget = MailRequest, suppress_label=True, repeatations=0)
project_fields = [ twd.HidingRadioButtonList("project",label_text="Which area are you having problems with?" , options=project_options, selected="networks",
                       help_text="If you are not sure of the area select 'Hub Networks'", is_required=True, mapping = hide_mappings, validator=twv.NotEmpty)]

client_fields = [
        twf.TextField("browser", label_text="What browser are you using?", help_text="eg. Firefox 3.0"),
        twf.TextField("url", label_text="What's the URL of the page you are having a problem on?", show_error=False),
        twf.TextField("os", label_text="Are you using a PC, Mac or Linux?", is_required=True) ]

class ClientInfo(twd.HidingTableFieldSet):
    legend = "" #"Area and your client"
    show_children_errors = False
    suppress_label = True
    children = [ twf.Label("title", text="Area and your client details") ]
    children = children + project_fields + client_fields

class MHPSClientInfo(twd.HidingTableFieldSet):
    legend = "" #"Area and your client"
    suppress_label = True
    show_children_errors = True
    show_error = False
    children = [ twf.Label("title", text="Your client details") ]
    children = children + client_fields

locations = {
'LIS': 'Islington',
'JHB': 'Johannesburg',
'LSB': 'Southbank',
'BAY': 'San Francisco',
'RTD': 'Rotterdam',
'VIE': 'Vienna',
'SPA': 'Sao Paulo',
'BAY': 'San Francisco',
'BER': 'Berlin',
'BRK': 'Berkeley',
'BXL': 'Brussels',
'PTO': 'Porto',
'OAX': 'Oaxaca',
'BRI': 'Bristol',
'HFX': 'Halifax',
'LKX': 'Kings Cross',
'CAI': 'Cairo',
'MLN': 'Milan',
'MAD': 'Madrid',
'AMS': 'Amsterdam',
'COP': 'Copenhagen',
'BOM': 'Bombay',
}

class ReporterInfo(twd.HidingTableFieldSet):
    legend="About you"
    suppress_label = True
    show_children_errors = True
    show_error = False
    #show_error = True
    class fields(WidgetsList):
        reporter = reporter
        fname = fname
        lname = lname
        email = email
        # as described at http://the-hub.pbworks.com/Hub%20three%20letter%20codes
        location = twf.SingleSelectField(label_text="Location", help_text="eg. Berkeley, Berlin", options=locations.items())

class MHPSReporterInfo(twd.HidingTableFieldSet):
    legend="About you"
    suppress_label = True
    show_children_errors =True 
    #show_error = True
    class fields(WidgetsList):
        reporter = reporter
        email = email

class MoreDetails(twd.HidingTableFieldSet):
    legend="Ticket details"
    show_children_errors = True
    suppress_label = True
    children = [summary_field,
                twf.TextArea("description", label_text="Please take us through, step by step, what happened before the error occurred. This will help us recreate what happened on our machines", help_text=["eg.", "1) Click edit in Profile section ","2) Change the fax no."]),
                twf.Spacer('spacer', suppress_label=True),
                twf.TextArea("suggestion", label_text="Do you have a suggested solution?", help_text=["eg. Show the warning", "before upload starts"]),]

moredetails = MoreDetails("moredetails")
saythanks = twf.Label("saythanks", help_text="After submitting this form you should receive an update on your ticket by e-mail shortly.  Thanks for letting us know!"),

class MainFieldSet(twd.HidingTableFieldSet):
    suppress_label = True
    show_children_errors = False
    show_error = False
    children = [whatreq,
                ReporterInfo("reporterinfo"),
                MailRequest("mailreq", get_default=get_default),
                mailreqrepeater,
                ClientInfo("clientinfo"),
                moredetails,
                ]

class TicketForm(twf.ListForm, twd.HidingTableForm):
    submit_text = "Create A Ticket"
    show_children_errors = False
    children = [
        MainFieldSet("Request", suppress_label=True),
        twf.Label("saythanks", help_text="After submitting this form you should receive an update on your ticket by e-mail shortly.  Thanks for letting us know!"),
            ]

class MHPSTicketForm(twf.ListForm):

    suppress_label = True
    submit_text = "Create Ticket"
    show_children_errors = False

    children = [
        MHPSReporterInfo("reporterinfo"),
        MHPSClientInfo("clientinfo"),
        moredetails,
        twf.Spacer("space", suppress_label=True),
        twf.Label("saythanks", help_text="After submitting this form you should receive an update on your ticket by e-mail shortly.  Thanks for letting us know!"),
        ]

ticketform = TicketForm("create_ticket_form", action="create", get_default=get_default)#, validator=ticketschema)
mhpsticketform = MHPSTicketForm("create_ticket_form", action="create", get_default= lambda: dict (clientinfo = simpledetect(request.user_agent)))
