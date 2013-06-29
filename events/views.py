from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from events.forms import EventDetailsForm

import os
from erp.settings import MEDIA_ROOT

import json

#Get the path of of json directory
def get_json_file_path(filename):
    if not os.path.exists('%sjson/events' %(MEDIA_ROOT)):
        os.makedirs('%sjson/events' %(MEDIA_ROOT))
    return '%sjson/events/' %(MEDIA_ROOT) + filename

def home(request):
    event_json_filepath = get_json_file_path('test.json')
    if not os.path.exists(event_json_filepath):
        message = 'No event details to display.'
        return render_to_response('events/home.html', {'message': message})
    with open(event_json_filepath) as f:
        event_details = json.load(f) # This is a python object: has to be converted to a json object1
        f.close()
    event_details = json.dumps(event_details, sort_keys=True, indent=4) # This gives a json object
    return render_to_response('events/home.html', {'event_details': event_details})
    
def edit_event(request):
    if request.method == 'POST':
        form = EventDetailsForm(request.POST)
        if form.is_valid():
            cleaned_form = form.cleaned_data
            event_details = {}
            event_details['name'] = cleaned_form['name']
            event_details['description'] = cleaned_form['description']
            event_details['update'] = cleaned_form['update']
            filepath = get_json_file_path('test.json')
            with open(filepath, 'w') as f:
                json.dump(event_details, f)
                f.close()
            return HttpResponseRedirect(reverse('events.views.home'))
        else:
            error = 'There seems to be an error. Please fill all the fields and submit the form again.'
            form = EventDetailsForm()
            return render_to_response('events/editEvent.html', {'error': error, 'form': form}, context_instance = RequestContext(request))
    else:
        form = EventDetailsForm()
    return render_to_response('events/editEvent.html', {'form': form}, context_instance = RequestContext(request))