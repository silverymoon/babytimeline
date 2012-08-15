Feature: CRUD of babies and milestones
In order to create timelines,
As a user
I want to create babies and milestones

Scenario: create a baby
Given I am logged in
When I enter the url /addbaby/
And I enter the data {'name' : 'test', 'birth_date_0': '2009-02-17', 'birth_date_1' : '18:45', 'weight_in_g': '4567', 'size_in_cm': '56', 'user': '6'}
Then I see the template timeline/baby_form.html and the data <a name="test" id="baby_3"

Scenario: edit a baby
Given I am logged in
When I enter the url /baby/edit/2
And I enter the data {'name' : 'foofoofoo', 'birth_date_0': '2009-02-17', 'birth_date_1' : '18:45', 'weight_in_g': '4567', 'size_in_cm': '56', 'user': '6'}
Then I see the template timeline/baby_form.html and the data <a name="foofoofoo" id="baby_2"

Scenario: delete a baby
Given I am logged in
When I enter the url /baby/delete/2
And I enter the data {}
Then I see the template timeline/baby_confirm_delete.html but not the data id="baby_">

Scenario: create a milestone with photo
Given I am logged in
When I enter the url /baby/addmilestone/2/
And I upload the file 'media/kuerbis.jpg' and enter the data {'date': '2013-04-01', 'baby': '2', 'image': f}
Then I see the template timeline/milestone_form.html and the data milestone/image/22

Scenario: create a milestone with free text
Given I am logged in
When I enter the url /baby/addmilestone/2/
And I enter the data {'date': '2013-04-01', 'baby': '2', 'note': 'hallolulila'}
Then I see the template timeline/milestone_form.html and the data hallolulila

@only
Scenario: edit a milestone
Given I am logged in
When I enter the url /milestone/edit/17/
And I enter the data {'date': '2013-04-01', 'baby': '2', 'type': 'CRAWL'}
Then I see the template timeline/milestone_form.html and the data I can crawl

Scenario: delete a milestone
Given I am logged in
When I enter the url /milestone/delete/17/
And I enter the data {}
Then I see the template timeline/milestone_confirm_delete.html but not the data /milestone/image/17