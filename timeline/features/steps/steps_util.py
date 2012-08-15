import re

from freshen import *
from django.test.client import Client
from django.core import management
from django.core import mail

@Before
def before(scenario):
    mail.outbox = []
    scc.client = Client()
    management.call_command('loaddata', 'test_data.json', verbosity=0)

@Given("I am logged in")
def login():
    scc.client.login(username="borgo", password="a")

@When("I enter the url (/.*)")
def press_button(button):
    scc.button = button
    scc.response_get = scc.client.get(button, follow=True)

@And("I enter the data (.*)")
def enter_data(data):
    dict = eval(data)
    scc.response_post = scc.client.post(scc.button, dict, follow=True)

@And("I upload the file '([^']+)' and enter the data (.*)")
def enter_data(file, data):
    f = open(file)
    dict = eval(data)
    scc.response_post = scc.client.post(scc.button, dict, follow=True)
    f.close()

@Then("I see the template ([^.]+.html) and the data (.*)")
def check_response_find(template_name, regex):
    assert scc.response_get.template[0].name == template_name
    assert scc.response_post.status_code == 200
    print scc.response_post.content
    assert re.search(regex, scc.response_post.content)

@Then("I see the template ([^.]+.html) but not the data (.*)")
def check_response_not_find(template_name, regex):
    assert scc.response_get.template[0].name == template_name
    assert scc.response_post.status_code == 200
    assert not re.search(regex, scc.response_post.content)

@Then("there's an email in the outbox to ([^ ]+) subject '([^']+)' containing (.*)")
def outbox(to, subject, body):
    assert len(mail.outbox) == 1
    scc.email = mail.outbox[0]
    assert re.search(to, scc.email.to[0])
    assert re.search(subject, scc.email.subject)
    assert re.search(body, scc.email.body)


