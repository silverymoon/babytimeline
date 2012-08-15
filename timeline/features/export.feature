Feature: export of pdf
In order to print timelines,
As a user
I want to export PDFs

@only
Scenario: export a pdf
Given I am logged in
When I enter the url /baby/export/1.pdf
Then I can download a pdf