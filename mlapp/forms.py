from wtforms import Form, BooleanField, IntegerField, StringField, PasswordField, TextAreaField, validators
EMAIL_MIN_LENGTH = 6
EMAIL_MAX_LENGTH = 100

class RegistrationForm(Form):
    email = StringField('Register Email Address', 
                        [validators.DataRequired("Email address is required!"),
                         validators.Length(min=EMAIL_MIN_LENGTH, 
                                           max=EMAIL_MAX_LENGTH, 
                                           message=f'Accepted email addresses are {EMAIL_MIN_LENGTH}-{EMAIL_MAX_LENGTH} characters!'), 
                         validators.Email(message="Not a valid email address!")]
                        )
    password = PasswordField('New Password', 
                             [validators.DataRequired("Password is required!"), 
                              validators.EqualTo('confirm_password', 
                                                 message='Both passwords must match!')]
                             )
    confirm_password = PasswordField('Repeat Password',
                                 [validators.DataRequired("Confirm password required!")])

class LoginForm(Form):
    email = StringField('Login Email Address', 
                        [validators.Length(min=EMAIL_MIN_LENGTH,
                                           max=EMAIL_MAX_LENGTH,
                                           message=f'Accepted email addresses are {EMAIL_MIN_LENGTH}-{EMAIL_MAX_LENGTH} characters!')]
                                           )
    password = PasswordField("Login Password",
                             [validators.DataRequired("Password is required!")])
    
class AnalyseForm(Form):
    comment = StringField("Comment",
                          [validators.DataRequired("Cannot analyse an empty comment!")])

class IssueForm(Form):
    # TODO check this works
    comment = TextAreaField("Issue Comment",
                            [validators.DataRequired("The issues's comment is required!")])
    # an issue isn't compulsory. It may be provided to help understand why the issue was raised.   
    issue = TextAreaField("Issue") 
    user_id = IntegerField("Issue Author",
                             [validators.DataRequired("A user_id is required!")])
    classification_id = IntegerField("Classification",
                                     [validators.DataRequired("A classification_id is required!")])

