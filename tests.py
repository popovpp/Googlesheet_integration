import pytest
from pytest_django.asserts import assertTemplateUsed
import requests
import socket
from django.conf import settings
from django.db import models

from integration.models.googlesheet import GoogleSheetIntegration
from user.models import User
from poll.models.poll import Poll

    
    
@pytest.fixture()
def set_googlesheetintegration(db):    
            
    user = User.objects.create_user(email='x@x.com')
    poll = Poll.objects.create(user=user)
    googlesheetintegration = GoogleSheetIntegration.objects.create(user=user, poll_id=poll)

    return googlesheetintegration

@pytest.fixture(scope='module')
def set_uris():
    hostname = socket.gethostname()
    IP = socket.gethostbyname(hostname)
    uri_auth = 'http://' + IP + ':9002' + '/v1/authentication/token/obtaining/'
    uri_reg = 'http://' + IP + ':9002' + '/v1/users/registration/'
    uri_googlesheet = 'http://' + IP + ':9002' + '/v1/googlesheet/googlesheetintegration/'

    return {
        'uri_auth': uri_auth,
        'uri_reg': uri_reg,
        'uri_googlesheet': uri_googlesheet
    }

def test_auto_created_id_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('id').auto_created
    assert field_param == True


def test_primary_key_id_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('id').primary_key
    assert field_param == True


def test_serialize_id_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('id').serialize
    assert field_param == False


def test_verbose_name_id_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('id').verbose_name
    assert field_param == 'id'


def test_verbose_name_user_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('user').verbose_name
    assert field_param == 'User'


def test_verbose_name_poll_id_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('poll_id').verbose_name
    assert field_param == 'poll id'


def test_default_is_active_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('is_active').default
    assert field_param == False


def test_verbose_name_is_active_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('is_active').verbose_name
    assert field_param == 'active'


def test_max_length_spreadsheet_id_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('spreadsheet_id').max_length
    assert field_param == 255


def test_default_spreadsheet_id_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('spreadsheet_id').default
    assert field_param == ''


def test_blank_spreadsheet_id_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('spreadsheet_id').blank
    assert field_param == True


def test_null_spreadsheet_id_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('spreadsheet_id').null
    assert field_param == True


def test_verbose_name_spreadsheet_id_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('spreadsheet_id').verbose_name
    assert field_param == 'spreadsheetId'


def test_blank_spreadsheet_url_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('spreadsheet_url').blank
    assert field_param == True


def test_null_spreadsheet_url_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('spreadsheet_url').null
    assert field_param == True


def test_verbose_name_spreadsheet_url_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('spreadsheet_url').verbose_name
    assert field_param == 'spreadsheet url'


def test_verbose_name_row_count_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('row_count').verbose_name
    assert field_param == 'row count'


def test_default_row_count_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('row_count').default
    assert field_param == 1


def test_verbose_name_survey_id_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('survey_id').verbose_name
    assert field_param == 'survey_id'


def test_blank_survey_id_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('survey_id').blank
    assert field_param == True


def test_null_survey_id_field(set_googlesheetintegration):
    field_param = set_googlesheetintegration._meta.get_field('survey_id').null
    assert field_param == True


def test_GET_GS_integration_list(set_uris):

    response = requests.post(set_uris['uri_auth'], data={"email":"a@a.com", 
                             "password":"12345678"})
    token = response.json()['token']
    response = requests.get(set_uris['uri_googlesheet'], 
                            headers={'Authorization': 'jwt {}'.format(token)})
    assert response.status_code == 200
