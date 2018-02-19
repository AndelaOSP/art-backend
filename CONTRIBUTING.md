### Contributing

We love pull requests from everyone.

### Usage

To get the end points for this project, run:

[https://art-backend.herokuapp.com/docs](https://art-backend.herokuapp.com/docs)

Fork, then clone the repo:
```
git clone https://github.com/AndelaOSP/art-backend.git
```
Set up your machine:

- [Add Virtual Environment](http://www.pythonforbeginners.com/basics/how-to-use-python-virtualenv)
- [Add .env](https://github.com/theskumar/python-dotenv)


*An .env file is an .ini-style file. It must contain a list of KEY=value pairs, just like Shell environment variables:*

```
# .env

DJANGO_DEBUG=False
SECRET_KEY='1q2w3e4r5t6z7u8i9o0(%&)$§"!pqaycz'
DATABASE_URL='art-backend'
```

```
$ pip install -r requirements.txt
```
Make sure the tests pass:
```
$ python manage.py test
```
Make your change. Add [tests](https://docs.djangoproject.com/en/2.0/topics/testing/overview/) for your change. Make the tests pass:
```
$ python manage.py test
```
Push to your fork and submit a pull request.

Writing a new endpoint?
Here's how you can ensure it apprears in the API docs:
[http://www.django-rest-framework.org/topics/documenting-your-api/](http://www.django-rest-framework.org/topics/documenting-your-api/)

At this point you're waiting on us. We like to at least comment on pull requests within three business days (and, typically, one business day). We may suggest some changes or improvements or alternatives.

Some things that will increase the chance that your pull request is accepted:

- Write [tests]((https://docs.djangoproject.com/en/2.0/topics/testing/overview/) ).
- Follow our [style guide.](https://www.python.org/dev/peps/pep-0008/)
- Write a [good commit message.](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)