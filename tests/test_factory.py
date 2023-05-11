"""
This module is used to test the application factory. 

Functions:
- test_config: Test for configuration of the Flask application instance. 
- test_hello: Test for the hello view function.

"""
from mlapp import create_app

def test_config():
    """Test configuration of the Flask application.  

    If test_config is not passed to the application factory, the Flask 
    instance's testing attribute should be False.
    If test_config is passed, and TESTING is passed as True, the Flask's 
    instance's testing attribute should be True. 
    """
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

def test_hello(client):
    """Test the hello route in application factory.

    The route should return a response with the text "Hello, World!"

    Parameters
    ----------
    client : FlaskClient
        Similar to a Werkzeug test client but has knowledge about Flask's contexts.
    """
    response = client.get('/hello')
    assert response.data == b'Hello, World!'