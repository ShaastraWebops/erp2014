from django import forms 
from django.forms import ModelForm 
from hospi.models import *
from users.models import UserProfile,College
from events.models import GenericEvent
from erp.settings import DATABASES
mainsite_db = DATABASES.keys()[1]
COLLEGE_CHOICES = ((college.name+"|"+college.city+"|"+college.state, college.name+"|"+college.city+"|"+college.state) for college in College.objects.using(mainsite_db))
event_list = GenericEvent.objects.all()
event_choices = [(event,event) for event in event_list]


class AddRoomForm(ModelForm):
    class Meta:
        model = AvailableRooms
        exclude = ('already_checkedin','mattresses',)

class IndividualForm(ModelForm):
    class Meta:
        model = IndividualCheckIn
        fields = ('room',
                'duration_of_stay',
                'number_of_mattresses_given',
                'mattress_room',
                'shaastra_ID',
                'check_in_control_room',
                'check_out_control_room',
                )


class ShaastraIDForm(forms.Form):
    shaastraID = forms.CharField(required=False,help_text='Enter Shaastra ID')

class RemoveRoom(ModelForm):
    class Meta:
        model = AvailableRooms
        exclude = ('already_checkedin','mattresses','max_number')

class RegistrationForm(ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    username = forms.CharField(max_length=30)
    email = forms.EmailField()
    college = forms.ChoiceField(choices=COLLEGE_CHOICES, help_text = 'Try to find college here, else fill form below')
    class Meta:
        model = UserProfile
        fields = (
                'age',
                'gender',
                'branch',
                'mobile_number',
                'college_roll',
                'shaastra_id',
                )

class TeamCheckinForm(forms.Form):
    
    event = forms.ChoiceField(choices=event_choices,required=False,widget=forms.Select())
    check_in_control_room = forms.ChoiceField(choices=CONTROL_ROOM_CHOICES,required=False,widget=forms.Select())
    team_id_num = forms.IntegerField(required=False)

class TeamCheckoutForm(forms.Form):
    event = forms.ChoiceField(choices=event_choices,required=False,widget=forms.Select())
    check_out_control_room = forms.ChoiceField(choices=CONTROL_ROOM_CHOICES,required=False,widget=forms.Select())
    team_id_num = forms.IntegerField(required=False)
