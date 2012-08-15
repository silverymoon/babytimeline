Feature: privacy of files
In order to keep my stuff private,
As a user
I want no-one else to see my data

Scenario: view other people's pdf
Given I am logged in
When I enter the url /baby/export/1.pdf
Then I get an access denied page

Scenario: view other people's pics
Given I am logged in
When I enter the url /milestone/image/12
Then I get an access denied page

Scenario: view my own pic
Given I am logged in
When I enter the url /milestone/image/17
Then I can see an image

