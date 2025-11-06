import pytest
from app import create_app, db
from app.models import User, Book, Comment

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_add_comment(client):
    # Create a user and a book
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    book = Book(title='Test Book', author='Test Author', isbn='1234567890', user_id=user.id)
    db.session.add(book)
    db.session.commit()

    # Log in as the user
    client.post('/auth/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)

    # Visit the book's page
    response = client.get(f'/book/{book.uid}', follow_redirects=True)
    assert response.status_code == 200

    # Add a comment
    response = client.post(f'/book/{book.uid}', data={'text': 'This is a test comment.'}, follow_redirects=True)
    assert response.status_code == 200

    # Check if the comment is displayed on the page
    assert b'This is a test comment.' in response.data
