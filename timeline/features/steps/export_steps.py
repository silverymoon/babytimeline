from freshen import *

from steps_util import *

@Then("I can download a pdf")
def check_pdf_result():
    print scc.response_get
    assert scc.response_get['Content-Disposition'] == "attachment; filename=/home/britta/babytimeline/src/babytimeline/user_files/exports/Foobar.pdf"
