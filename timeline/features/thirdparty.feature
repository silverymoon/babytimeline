Feature: 3rd party tools
As a user,
I want to register and contact the website owner

Scenario: Logout
Given I am logged in
When I enter the url /accounts/logout/
Then I am logged out

Scenario: Login
Given I enter the url /addbaby/
Then I get to the login page

Scenario: Contact website owner
Given I enter the url /contact/
When I enter the data {'name' : 'foo', 'email': 'a@b.cd', 'body' : "I'm too sexy for this email"}
Then there's an email in the outbox to babytimeline subject 'KONTAKTAUFNAHME' containing too sexy

Scenario: Register
Given I enter the url /accounts/register/
When I enter the data {'username' : 'foobar', 'email' : 'x@y.zz', 'password1' : 'q', 'password2': 'q'}
And there's an email in the outbox to x@y.zz subject 'Aktivierung' containing aktivieren.*Link
And I click the activation link
Then I am a proper new user

Scenario: Forgot password
Given I enter the url /accounts/password/reset/
And I enter the data {'email' : 'a@b.cd'}
When there's an email in the outbox to a@b.cd subject 'Passwort.*babytimeline' containing benutze bitte diesen Link
And I click the activation link
And I input a new password
Then I see the template registration/password_reset_confirm.html and the data Passwort wurde erfolgreich

Scenario: Forgot password, invalid user
Given I enter the url /accounts/password/reset/
And I enter the data {'email' : 'x@y.za'}
Then I see the template registration/password_reset_form.html and the data existiert kein Benutzer

Scenario: Change password
Given I am logged in
And I enter the url /accounts/password/change/
When I enter the data {'old_password' : 'a', 'new_password1' : 'q', 'new_password2' : 'q'}
Then I see the template registration/password_change_form.html and the data Passwort wurde erfolgreich