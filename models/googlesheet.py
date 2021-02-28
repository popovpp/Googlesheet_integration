from django.db import models

from poll.models.poll import Poll
from user.models import User
from poll.models.surveypassing import SurveyPassing

class GoogleSheetIntegration(models.Model):   

    id = models.AutoField(auto_created=True, primary_key=True, serialize=True,
                          verbose_name='id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')
    poll_id = models.OneToOneField(Poll, on_delete=models.CASCADE,
                                   verbose_name='poll id')
    is_active = models.BooleanField(default=False, 
                                    verbose_name='active')
    spreadsheet_id = models.CharField(max_length=255, default='', blank=True, null=True, 
                                      verbose_name='spreadsheetId')
    spreadsheet_url = models.URLField(blank=True, null=True, 
    	                              verbose_name='spreadsheet url')
    row_count = models.PositiveIntegerField(default=1, verbose_name='row count')
    survey_id = models.ManyToManyField(SurveyPassing, blank=True,
                                       verbose_name='survey_id', null=True)



    REQUIRED_FIELDS = []

    class Meta:
    	verbose_name = 'GoogleSheetIntegration'
    	verbose_name_plural = 'GoogleSheetIntegrations'

    def __str__(self):
        return repr(self.id)
        