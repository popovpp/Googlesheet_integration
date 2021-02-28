from rest_framework import serializers
from integration.service import get_item_questions, get_user_answers, get_captions_questions
from django.conf import settings

from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import apiclient.discovery
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from integration.models.googlesheet import GoogleSheetIntegration
from poll.models.questions import ManyFromListQuestion, YesNoQuestion
from poll.models.questions import DivisionQuestion, RatingQuestion
from poll.models.questions import MediaQuestion, TextQuestion
from poll.models.questions import FinalQuestion
from poll.models.surveypassing import SurveyPassing
from user.models import User, SecretGuestProfile, BusinessUserProfile



class GoogleSheetIntegrationSerializer(serializers.ModelSerializer):

    class UserSerializer(serializers.ModelSerializer):

        class Meta:
            model = User
            fields = ['id']


    is_active = serializers.BooleanField(default=False, read_only=True)
    row_count = serializers.IntegerField(default=1, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = GoogleSheetIntegration
        fields = ['url', 'id', 'user', 'poll_id', 'is_active', 
		              'spreadsheet_url', 'row_count', 'survey_id']

    def create(self, *args, **kwargs):
        google_sheet_integration = GoogleSheetIntegration.objects.create(user=self.context['user'], 
                                                                         poll_id=args[0]['poll_id'])

# Connect to GoogleSheet API

        CREDENTIALS_FILE = settings.STATICFILES_DIRS[0] + '/' + 'credentials.json' 
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, 
        	                                                           ['https://www.googleapis.com/auth/spreadsheets',
                                                                      'https://www.googleapis.com/auth/drive'])
        httpAuth = credentials.authorize(httplib2.Http())
        service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

# Create name of sheet
        sheet_name = google_sheet_integration.user.email + '_' + str(args[0]['poll_id'].poll_id)

# Create the row with questions      
        
        captions = [[]]
        questions = ManyFromListQuestion.objects.filter(poll=args[0]['poll_id'])
        for question in questions:
            captions[0].append(question.caption)
        
        questions = YesNoQuestion.objects.filter(poll=args[0]['poll_id'])
        for question in questions:
            captions[0].append(question.caption)

        questions = DivisionQuestion.objects.filter(poll=args[0]['poll_id'])
        for question in questions:
            captions[0].append(question.caption)

        questions = RatingQuestion.objects.filter(poll=args[0]['poll_id'])
        for question in questions:
            captions[0].append(question.caption)

        questions = MediaQuestion.objects.filter(poll=args[0]['poll_id'])
        for question in questions:
            captions[0].append(question.caption)

        questions = TextQuestion.objects.filter(poll=args[0]['poll_id'])
        for question in questions:
            captions[0].append(question.caption)

        row_lenth = len(questions) + 10



# Create empty spreadsheets        
        spreadsheet = service.spreadsheets().create(body={
                                                    'properties': {'title': sheet_name, 'locale': 'ru_RU'},
                                                    'sheets': [{'properties': {'sheetType': 'GRID',
                                                    'sheetId': 0,
                                                    'title': sheet_name,
                                                    'gridProperties': {'rowCount': 10000, 'columnCount': row_lenth}}}]
                                                    }).execute()

# Connect to GoogleDrive API to get access to spreadsheets for any user
        driveService = apiclient.discovery.build('drive', 'v3', http=httpAuth)
        shareRes = driveService.permissions().create(fileId=spreadsheet['spreadsheetId'],
                                                     body={'type': 'anyone', 'role': 'writer'},  
                                                     fields='id').execute()




# Add informations of poll to sheet
        results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet['spreadsheetId'], 
                                                              body={
                                                              "valueInputOption": "USER_ENTERED",
                                                              "data": [
                                                              {"range": "{}!A1:ZZZ5".format(sheet_name),
                                                              "majorDimension": "ROWS",
                                                              "values": captions}
                                                                       ]}).execute()

        google_sheet_integration.spreadsheet_id = spreadsheet["spreadsheetId"]
        google_sheet_integration.spreadsheet_url = spreadsheet["spreadsheetUrl"]
        google_sheet_integration.row_count += 1
        google_sheet_integration.is_active = True
        google_sheet_integration.save()
        return google_sheet_integration

    def update(self, pk, *args, **kwargs):
        
        google_sheet_integration = GoogleSheetIntegration.objects.get(poll_id=args[0]['poll_id'])
        if args[0]['survey_id'][0] not in google_sheet_integration.survey_id.all():
            questions_items = get_item_questions(args[0]['poll_id'])
            user_answer_items = get_user_answers(args[0]['survey_id'][0], questions_items)
            answers = [[], []]
            
            if len(user_answer_items) == 0:
                user_answer_items.append({'question_id': 1, 'text': 'There are not amswers.'})
            qid_flag = user_answer_items[0]['question_id']
            answers = []
            i = -1
            for el in user_answer_items:
                if qid_flag == el['question_id']:
                    if i >= len(answers)-1:
                        answers.append(['' for i in range(0, user_answer_items[len(user_answer_items)-1]['question_id'])])
                    i += 1
                    answers[i][el['question_id']-1] = el['text']
                else:
                    i =0
                    answers[i][el['question_id']-1] = el['text']
                qid_flag = el['question_id']

            answers.append([])
            answers[len(answers)-1].append(args[0]['survey_id'][0].id)
        
            survey_passing = SurveyPassing.objects.get(id=args[0]['survey_id'][0].id)
            answers[len(answers)-1].append(survey_passing.user.email)
            
            try:
                secret_guest_profile = SecretGuestProfile.objects.get(user=survey_passing.user)
            except Exception as e:
                print(e)
                secret_guest_profile = None
            
            if secret_guest_profile is not None:
                full_name = secret_guest_profile.full_name                
            else:
                try:
                    business_user_profile = BusinessUserProfile.objects.get(user=survey_passing.user)
                    full_name = business_user_profile.full_name
                except Exception as e:
                    print(e)
                    full_name = 'Anonimous'

            answers[len(answers)-1].append(full_name)

# Connect to GoogleSheet API
            CREDENTIALS_FILE = settings.STATICFILES_DIRS[0] + '/' + 'credentials.json' 
            credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, 
                                                                     ['https://www.googleapis.com/auth/spreadsheets',
                                                                      'https://www.googleapis.com/auth/drive'])
            httpAuth = credentials.authorize(httplib2.Http())
            service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)


# Create name of sheet
            sheet_name = google_sheet_integration.user.email + '_' + str(args[0]['poll_id'].poll_id)

# Add informations of poll to sheet
            results = service.spreadsheets().values().batchUpdate(spreadsheetId=google_sheet_integration.spreadsheet_id, 
                                                              body={
                                                              "valueInputOption": "USER_ENTERED",
                                                              "data": [
                                                              {"range": "{}!A{}:ZZZ{}".format(sheet_name, google_sheet_integration.row_count, 
                                                                                              (google_sheet_integration.row_count+len(answers))),
                                                              "majorDimension": "ROWS",
                                                              "values": answers}
                                                                       ]}).execute()

            google_sheet_integration.row_count += len(answers)
            google_sheet_integration.survey_id.add(args[0]['survey_id'][0])
            google_sheet_integration.save()
        return google_sheet_integration
