from freshen import *

from steps_util import *

@Then("I get an access denied page")
def check_access_denied():
    assert scc.response_get.template[0].name == "timeline/not_allowed.html"

@Then("I can see an image")
def check_image():
    assert scc.response_get['Content-Type'] == 'application/image'
