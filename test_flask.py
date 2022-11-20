import pytest
from main import app



def test_index():
    test = app.get("/")
    assert test.status == '200'
    assert test.status == '302'
    assert test.status == '304'

def test_login():
    test = app.get("/login")
    assert test.email == 'test123@gmail.com'
    assert test.password == 'password1!'

if __name__ == '__main__':
    pytest.main()
