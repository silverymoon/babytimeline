import re

from freshen import *

from steps_util import *

@Then("I am logged out")
def logout():
    assert scc.response_get.template[0].name == "registration/logout.html"
    assert not re.search("Du bist eingeloggt als", scc.response_get.content)

@Then("I get to the login page")
def loggedout():
    assert scc.response_get.template[0].name == "registration/login.html"

@And("I debug")
def debug():
    resp = scc.client.post("/accounts/register/", {'username' : 'foobar', 'email' : 'x@y.zz', 'password1' : 'q', 'password2': 'q'})
    assert False

@And("I click the activation link")
def activate_account():
    scc.email_url = re.search("http://localhost:8000(/.*/)", scc.email.body).group(1)
    scc.response_email = scc.client.get(scc.email_url, follow=True)

@Then("I am a proper new user")
def new_user():
    assert re.search("Account.*aktiv!", scc.response_email.content)

@And("I input a new password")
def new_pwd():
    scc.response_get = scc.response_email
    scc.response_post = scc.client.post(scc.email_url, {'new_password1': '1', 'new_password2' : '1'}, follow = True)
