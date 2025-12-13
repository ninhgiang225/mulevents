def test_forms_load(app):
    from forms import LoginForm, SignupForm, EventForm
    LoginForm()
    SignupForm()
    EventForm()
