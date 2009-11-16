from hubreporter.lib.base import BaseController

from tg import expose, flash, require, url, request, redirect, validate, tmpl_context, response

from hubreporter.widgets.ticket_form import ticketform, mhpsticketform

#import twill.commands
import mechanize
import tg
from hubreporter.tools.agent import simpledetect

import base64
from mako.template import Template

def submit(project, reporter, email, location, summary, description="", component="", **kw):
    baseurl = tg.config.global_conf['trac_url']
    loginurl = "%s/%s/login" % (baseurl, project)
    newticketurl = "%s/%s/newticket" % (baseurl, project)
    b = mechanize.Browser()
    b.open(loginurl)
    forms = list(b.forms())
    for form in forms:
        all_fields = set([c.name for c in form.controls])
        if set(["user", "password"]).issubset(all_fields):
            nr = forms.index(form)
            b.select_form(nr=nr)
            break
    # else: no form ?
    b['user'] = tg.config.global_conf['trac_user']
    b['password'] = tg.config.global_conf['trac_secret']
    b.submit()
    
    b.open(newticketurl)
    forms = list(b.forms())
    for form in forms:
        if set(["field_reporter", "field_summary"]).issubset(set([c.name for c in form.controls])):
            nr = forms.index(form)
            b.select_form(nr=nr)
            break
    # else: no form ?
    b["field_reporter"] = "%(reporter)s <%(email)s>" % locals()
    b["field_summary"] = summary
    b["field_description"] = description
    #b["field_type"] = ["defect"]
    b["field_priority"] = ["major"]
    print all_fields
    if "field_hub_location" in all_fields:
        b["field_hub_location"] = location
    if component:
        b["field_component"] = [component]
    b.submit('submit')
    links = b.links()
    defect_url = [lnk for lnk in b.links() if lnk.text == 'View'][0].absolute_url
    return defect_url
    
template_map = dict (issue = "hubreporter/templates/issue.txt", mailreq = "hubreporter/templates/mailreq.txt")

class TicketController(BaseController):

    @expose('hubreporter.templates.newTicket')
    def default(self, *args, **kw):
        return self.new(*args, **kw)

    @expose('hubreporter.templates.newTicket')
    def new(self, *args, **kw):
        tmpl_context.form = ticketform
        return dict(modelname='Ticket', page='New Ticket')

    @expose()
    @validate(form=ticketform, error_handler=new)
    def create(self, **kw):
        #import pylons
        #return str(pylons.c.form_errors) + str(kw)
        whatrequest = kw['Request']['whatrequest']
        if whatrequest == "mailreq":
            project = "networks"
            desc_d = dict (
                project = project,
                )
            desc_d.update(kw)
            template = Template(filename=template_map[whatrequest])
            description = template.render(kw=desc_d)
        else:
            project = kw['Request']['clientinfo']['project']
            desc_d = dict (
                project = project,
                url = kw['Request']['clientinfo']['url'],
                browser = kw['Request']['clientinfo']['browser'],
                location = kw['Request']['reporterinfo']['location'],
                os = kw['Request']['clientinfo']['os'],
                description = kw['Request']['moredetails']['description'],
                suggestion = kw['Request']['moredetails']['suggestion'],
                )
            template = Template(filename=template_map[whatrequest])
            description = template.render(**desc_d)
        email = kw['Request']['reporterinfo']['email']
        if kw['Request']['whatrequest'] == "mailreq":
            summary = "Mail address request"
            reporter = "%(fname)s %(lname)s" % kw['Request']['reporterinfo']
        else:
            summary = kw['Request']['moredetails'] and kw['Request']['moredetails'].get('summary', "") or ""
            reporter = kw['Request']['reporterinfo']['reporter']
        location = kw['Request']['reporterinfo']['location']
        defect_url = submit(project, reporter, email, location, summary, description, component="", **kw)
        # what is twill fails?
        flash("Thank you, %s, you can further followup the defect at %s" % (reporter, defect_url))
        redirect("/tickets/new")

class MHPSTicketController(BaseController):

    @expose('hubreporter.templates.newTicket')
    def new(self, *args, **kw):
        tmpl_context.form = mhpsticketform
        return dict(modelname='Ticket', page='New Ticket')

    @expose()
    @validate(mhpsticketform, error_handler=new)
    def create(self, **kw):
        project = "hubplus"
        reporter = kw['reporterinfo']['reporter']
        email = kw['reporterinfo']['email']
        summary = kw['moredetails'] and kw['moredetails'].get('summary', "") or ""
        template = Template(filename=template_map['issue'])
        desc_d = dict (
            project = project,
            url = kw['clientinfo']['url'],
            browser = kw['clientinfo']['browser'],
            location = kw['reporterinfo']['location'],
            os = kw['clientinfo']['os'],
            description = kw['moredetails']['description'],
            suggestion = kw['moredetails']['suggestion'],
            )
        description = template.render(**desc_d)
        component = "MHPS"
        defect_url = submit(project, reporter, email, summary, description, component)
        flash("Thank you, %s, you can further followup the defect at %s" % (reporter, defect_url))
        redirect("/mhps/new")
