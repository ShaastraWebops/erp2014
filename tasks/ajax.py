# For simple dajax(ice) functionalities
from django.utils import simplejson
from misc.dajaxice.decorators import dajaxice_register
from misc.dajax.core import Dajax
from dajaxice.utils import deserialize_form 

# Django imports
from django.db.models import Q

# For rendering templates
from django.template import RequestContext
from django.template.loader import render_to_string

# Decorators
from django.contrib.auth.decorators import login_required, user_passes_test

# From forms
from tasks.forms import IntraTaskForm, CrossTaskForm
# From models
from tasks.models import Task, Comment, TASK_STATUSES
from users.models import ERPUser
# From Misc to show bootstrap alert
from misc.utilities import core_check, core_or_supercoord_check, show_alert, get_position
# Python imports
import datetime

# Messages
from django.contrib import messages

   
    
# _____________--- TASK TABLE DISPLAY VIEW ---______________#
@dajaxice_register(name="tasks.task_table")
@login_required
def task_table(request, page):
    """
        Used to show table of subdepartment tasks using Dajax(ice)
        It handles all tables (personal/you, subdept, dept, pending, cross) of all users (coord, supercoord, core)
        
        Renders in : right_content
        Refreshes : null
        
        CORES :
            Personal/You
            Department
            Pending
            CrossTasks
        SUPERCOORD :
            Personal/You
            Department
        COORD :
            Personal/You
            SubDepartment
            
        QUERIES TO RETRIEVE:
            1.  The user's tasks.
            2.  Tasks assigned to the department
            3.  Tasks assigned to the subdepartment
            4.  The Crosstasks created by the department
            5.  Tasks pending approval
            6.  ?Crosstasks _to_ the department?

    """
    dajax = Dajax() # To hold the json
    
    userprofile = request.user.get_profile()
    # Query dictionary will contain UserProfile and the table to be drawn
    query_dictionary = {} # Initialize a blank Query dictionary.
    query_dictionary["userprofile"] = userprofile
    query_dictionary["TASK_STATUSES"] = TASK_STATUSES # To search for status msg
    html_content = ""
    
    # ALL QUERYSETS OF TASKS FILTERED FOR THE USER MUST BE AGAIN FILTERED BY DEPARTMENT (the way I've done it for user_tasks). THIS HANDLES THE MULTIPLE IDENTITY DISORDER.
    # Assigning the above values
    # ALL
    if page == "table_you":
        query_dictionary["user_tasks"] = userprofile.task_set.filter(targetdept=userprofile.dept).all()
        if userprofile.is_coord():
            html_content = render_to_string("dash/task_tables/coord_you.html", query_dictionary, RequestContext(request))
        elif userprofile.is_supercoord():
            html_content = render_to_string("dash/task_tables/supercoord_you.html", query_dictionary, RequestContext(request))
        elif userprofile.is_core():
            html_content = render_to_string("dash/task_tables/core_you.html", query_dictionary, RequestContext(request))
    
    # COORD ONLY
    elif page == "table_subdept" and userprofile.is_coord():
        #The attribute userprofile.subdept is present only if he's a coord
        query_dictionary["subdept_tasks"] = userprofile.subdept.task_set.exclude(taskstatus='U')
        html_content = render_to_string("dash/task_tables/coord_subdept.html", query_dictionary, RequestContext(request))
        
    # SUPERCOORD ONLY
    elif page == "table_cross" and userprofile.is_supercoord():
        query_dictionary["dept_todo_crosstasks"] = userprofile.dept.todo_task_set.filter(isxdepartmental=True).exclude(taskstatus='U') #Remove if necessary.
        html_content = render_to_string("dash/task_tables/supercoord_cross.html", query_dictionary, RequestContext(request))
    elif page == "table_dept" and userprofile.is_supercoord():
        query_dictionary["dept_tasks"] = userprofile.dept.todo_task_set.exclude(taskstatus='U')
        html_content = render_to_string("dash/task_tables/supercoord_dept.html", query_dictionary, RequestContext(request))
      
    # CORE ONLY
    elif page == "table_pending" and userprofile.is_core():
        query_dictionary["approval_pending_tasks"] = userprofile.dept.todo_task_set.filter(Q(taskstatus='R') | Q(taskstatus='U')) # Reported Completed tasks
        #query_dictionary["approval_pending_tasks"] += userprofile.dept.todo_task_set.filter(taskstatus='U') # Unapproved tasks
        html_content = render_to_string("dash/task_tables/core_pending.html", query_dictionary, RequestContext(request))
    elif page == "table_cross" and userprofile.is_core():
        query_dictionary["dept_created_crosstasks"] = userprofile.dept.created_task_set.filter(isxdepartmental=True)
        html_content = render_to_string("dash/task_tables/core_cross.html", query_dictionary, RequestContext(request))
    elif page == "table_dept" and userprofile.is_core():
        query_dictionary["dept_tasks"] = userprofile.dept.todo_task_set.exclude(taskstatus='U')
        html_content = render_to_string("dash/task_tables/core_dept.html", query_dictionary, RequestContext(request))
    
    # Weird case
    else:
        show_alert(dajax, 'error','Could not find the requested table. Contact WebOps Team.')
        
    if html_content != "": 
        # put html generated above into json if not null
        # if null, alert has already been taken care of
        dajax.assign('#id_content_right','innerHTML', html_content)
        
    return dajax.json()

# _____________--- TASK DISPLAY VIEW ---______________#
@dajaxice_register(method="GET", name="tasks.display_task_get")
@dajaxice_register(method="POST", name="tasks.display_task_post")
@login_required
def display_task(request, primkey, comments_field=None):
    """
        Displays a task to viewers with a commet field
        It handles the displaying of all tasks : intra and cross
        
        The post method handles the receiving of a submitted comment and saves it
        
        Renders in : modal
        Refreshes : if new comment added, refreshed content of modal
    """
    # TODO: Redirect people who aren't allowd to view this task. 
    # Add edit and delete buttons for cores and supercoords
    # Display ALL details in the template - template needs work.
    print primkey
    dajax = Dajax()
    html_content = ""
    primkey = int(primkey)
    
    # Save comment if new comment given
    
    # Get Task + comments and populate
    try:
        task = Task.objects.get(pk = primkey)
        task_statuses = TASK_STATUSES
        print "task"
        if request.method == 'POST' and comments_field != None: # Add new comment if necessary
            if comments_field == "":
                dajax.add_css_class("#comments_field", "error")
            else :
                task_comment = Comment()
                task_comment.task = Task.objects.filter(id = task.id)[0]
                task_comment.author = request.user
                task_comment.comment_string = comments_field
                task_comment.time_stamp = datetime.datetime.now()
                task_comment.save()
        print "check comment"        
        if ( comments_field != "" and comments_field != None ) or request.method == 'GET': 
            print "true"
            # i.e. if "Submit Comment" was pressed, and comment was given OR GET ... need to refresh
            comments = Comment.objects.filter(task = task)
            html_content = render_to_string('tasks/display.html', locals(), RequestContext(request))
            print html_content
            dajax.remove_css_class('#id_modal', 'hide') # Show modal
            dajax.assign("#id_modal", "innerHTML", html_content) # Populate modal
        print "done"
    except:
        show_alert(dajax, "error", "The task was not found")
        html_content = ""
    
    return dajax.json()

# _____________--- TASK UPGRADE VIEW ---______________#
@dajaxice_register(method="POST", name="tasks.upgrade_task")
def upgrade_task(request, primkey=None, direc=1):
    """
        Handles the upgrade task requests.
        CORE :
            Can upgrade from unapproved upto completed
            Can downgrade from completed to unapproved
        SUPERCOORD/COORD :
            Can upgrade from approved, ongoing upto Reported complete
            
        Renders in: alert
    """
    dajax = Dajax()
    direc = int(direc)
    
    userprofile = request.user.get_profile()
    upgradeable_statuses = [] #  A List containing all task_statuses to allow current to upgrade from and to (in order)
    if userprofile.is_coord():
        upgradeable_statuses = [
            TASK_STATUSES[1], # Approved and Ongoing
            TASK_STATUSES[2], # Approved, nearly done
            TASK_STATUSES[3], # Reported Complete
        ]
    elif userprofile.is_supercoord():
        upgradeable_statuses = [
            TASK_STATUSES[1], # Approved and Ongoing
            TASK_STATUSES[2], # Approved, nearly done
            TASK_STATUSES[3], # Reported Complete
        ]
    elif userprofile.is_core():
        upgradeable_statuses = TASK_STATUSES # All task statuses
    task = Task.objects.get(pk=int(primkey))
    flag_i_stat = 0;
    if task.taskstatus == 'C':
        """
            Taskstatus is maximum, don't do anything, give a warning
        """
        flag_i_stat = 2
        show_alert(dajax, 'warning', 'This Task is already completed.')
    elif direc == -1 and userprofile.is_core():
        """
            Only for cores
            
            Down grade the task. Go through the tuple elements by number,
            And give the taskstatus th value for i-2 (if that status exists)
            Give alert depending on what happened
        """
        for i_stat in range(len(upgradeable_statuses)): # This should be the whole list[0:x], else it won't work
            if flag_i_stat == 1:
                if i_stat >= 2: # if it is smaller, i cannot go negative, so leave as is
                    task.taskstatus = upgradeable_statuses[i_stat-2][0] # Set new task status
                    flag_i_stat = 2
                    task.save()
                    dajax.script("modal_hide()") # Refreshes the current tab
                    stat_msg = ""
                    for i_ in TASK_STATUSES:
                        if i_[0] == task.taskstatus:
                            stat_msg = i_[1]
                    show_alert(dajax, 'success', 'Task ' + task.subject + ' rejected to ' + stat_msg) # Gives success message
                else: # give error msg ?
                    dajax.script("alert('what to do if task is unapproved and rejected?')")
                break
            elif upgradeable_statuses[i_stat][0] == task.taskstatus:
                flag_i_stat = 1
    else:
        """
            For everyone
            
            Upgrade the task. Go through the tuple elements based on position
            And give the taskstatus the value after the current (if exists)
            Give alert depending on what happened
        """
        for i_stat in upgradeable_statuses:
            if flag_i_stat == 1:
                task.taskstatus = i_stat[0] # Set new task status
                flag_i_stat = 2
                task.save()
                dajax.script("modal_hide()") # Refreshes the current tab
                stat_msg = ""
                for i_ in TASK_STATUSES:
                    if i_[0] == task.taskstatus:
                        stat_msg = i_[1]
                show_alert(dajax, 'success', 'Task ' + task.subject + ' upgraded to ' + stat_msg) # Gives success message\
                break
            elif i_stat[0] == task.taskstatus:
                flag_i_stat = 1 # Next loop is what I need to set
    
    if flag_i_stat != 2: # New status was never set ... i.e. Not in upgradeable_statuses
        show_alert(dajax, 'error', 'Task was not upgraded. You cannot upgrade this task.') # Gives error message
        
    return dajax.json()

# _____________--- ADD INTRADEPARTMENTAL TASK ---______________#
@dajaxice_register(method="GET", name="tasks.new_intra_task_get")
@dajaxice_register(method="POST", name="tasks.new_intra_task_post")
@login_required
@user_passes_test (core_or_supercoord_check)
def new_intra_task(request, serializedform=None, primkey=None):
    """
        Serves and processes a new intradepartmental task.
         - if processing error, shows errors on same form
         - if no error, shows success alert
        
        CORES and SUPERS :
            Have access to edit and add tasks
            
        Arguments :
            serializedform - in post request, the form is sent
            primkey - prinkey of parent task (if any)
        
        Fields entered by user:
            'deadline', 'subject', 'description', 'taskforce'
        
        Fields automatically taken care of by model/model save function override:
            'taskcreator', 'datecreated', 'datelastmodified', 'depthlevel', 'parenttask'
        
        Fields taken care of by the view:
            'targetsubdepts', 'origindept', 'targetdept', 'isxdepartmental', 'taskstatus'
    """
    dajax = Dajax()
    
    print ("Primkey: %s" % primkey)

    # Check parent task and create parent-string
    if primkey:
        # Need to figure out the try, except block here
        parenttask = Task.objects.get(pk=primkey)
        parentlabel = "\nParent task: " + parenttask.subject
    else:
        parentlabel = "\nThis is a top level task."
        parenttask = None
    
    # Get basic data
    id_form = "new_task"
    userprofile = request.user.get_profile()
    department = userprofile.dept
    title = "Add Intradepartmental Task"
    info = parentlabel
    
    if request.method == 'POST' and serializedform != None:
        form = IntraTaskForm(department, deserialize_form(serializedform)) # get form
        if form.is_valid(): # check validity
            newTask = form.save(commit=False)
            
            #Set the origin & target departments & approve the task.        
            newTask.origindept = userprofile.dept
            newTask.targetdept = userprofile.dept
            newTask.taskcreator = userprofile
            newTask.taskstatus = 'O'
            newTask.parenttask = parenttask
            
            #For many to many relationships to be created, the object MUST first exist in the database.
            newTask.save()
            #UNCOMMENT THE BELOW LINE IF MANYTOMANY DATA IS BEING SAVED DIRECTLY FROM THE FORM
            #form.save_m2m()
                    
            #Get the TaskForce from the form
            cores = form.cleaned_data['cores']
            coords = form.cleaned_data['coords']
            supercoords = form.cleaned_data['supercoords']
            
            #Set the TaskForce for the Task
            for user in coords: 
                newTask.taskforce.add(user)
            for user in supercoords: 
                newTask.taskforce.add(user)
            for user in cores: 
                newTask.taskforce.add(user)
        
            newTask.save() # task saved
            
            dajax.remove_css_class('#form_' + str(id_form) + ' input', 'error') # remove earlier errors mentioned
            show_alert(dajax, 'success', "Task saved successfully") # show alert
        else: # some errors found 
            errors = True
            dajax.remove_css_class('#form_' + str(id_form) + ' input', 'error')
            for error in form.errors: # tell which parts had errors
                dajax.add_css_class('#id_%s' % error, 'error')
            print [error for error in form.errors]
            show_alert(dajax, 'error', "There were some errors : please rectify them") # show alert
    else: # it was a get request
        intra_form = IntraTaskForm(department)
        context = {'form': intra_form, 'id_form' : id_form, 'title':title, 'tasktype': "intra", 'primkey': primkey, 'info':info}
        html_content = render_to_string('tasks/task.html', context, context_instance=RequestContext(request))
        dajax.assign("#id_content_right", "innerHTML", html_content) # Populate modal
        
    return dajax.json()
    
    
    

# _____________--- ADD CROSSDEPARTMENTAL TASK ---______________#
@dajaxice_register(method="GET", name="tasks.new_cross_task_get")
@dajaxice_register(method="POST", name="tasks.new_cross_task_post")
@login_required
@user_passes_test (core_check)
def new_cross_task(request, serializedform=None, primkey=None):
    """
        Serves and processes a new intradepartmental task.
         - if processing error, shows errors on same form
         - if no error, shows success alert
        
        CORES: (ONLY)
            Have access to edit and add tasks
            
        Arguments :
            serializedform - in post request, the form is sent
            primkey - prinkey of parent task (if any)
        
        Fields entered by user:
            'deadline', 'subject', 'description', 'parenttask', 'targetsubdepts'
        
        Fields automatically taken care of by model/model save function override:
            'taskcreator', 'datecreated', 'datelastmodified', 'depthlevel'
        
        Fields taken care of by the view:
            'origindept', 'targetdept', 'isxdepartmental', 'taskstatus' 
            
        Fields that are unset:
             'taskforce'
    """
    dajax = Dajax()
    
    # Check parenttask and create parent-string
    if primkey:
        parenttask = Task.objects.get(pk=primkey)
        parentlabel = "\nParent task: " + parenttask.subject
    else:
        parentlabel = "\nThis is a top level task."
        parenttask = None
    
    # Add some more basic info
    title = "Add Cross-departmental Task."
    info = "Subject to approval of the target department's core." + parentlabel
    userprofile = request.user.get_profile()
    department = userprofile.dept
    id_form = "new_cross_task"
    
    if request.method == 'POST' and serializedform != None:
        form = CrossTaskForm(department, deserialize_form(serializedform))
        if form.is_valid():
            #Create a task object without writing to the database
            newTask = form.save(commit=False)
            
            #Get selected subdepartment from form and set targetdepartment
            #There's only one object in the form field - the loop is only going to run once.
            for subdept in form.cleaned_data['targetsubdepts']:
                newTask.targetdept = subdept.dept
            
            #Set these variables - Unapproved X-Departmental task
            newTask.taskcreator = userprofile
            newTask.isxdepartmental = True
            newTask.taskstatus = 'U'
            if primkey:
                newTask.parenttask = parenttask
      
            #Set the origin & target departments.        
            newTask.origindept = userprofile.dept
            
            #For many to many relationships to be created, the object MUST first exist in the database
            #Saves newTask and also saves the ManyToMany Data
            newTask.save()
            form.save_m2m() # Form saved
            
            dajax.remove_css_class('#form_' + str(id_form) + ' input', 'error') # remove earlier errors mentioned
            show_alert(dajax, 'success', "Task saved successfully") # show alert
        else: # some errors found 
            errors = True
            dajax.remove_css_class('#form_' + str(id_form) + ' input', 'error')
            for error in form.errors: # tell which parts had errors
                dajax.add_css_class('#id_%s' % error, 'error')
            print [error for error in form.errors]
            show_alert(dajax, 'error', "There were some errors : please rectify them") # show alert
    else: # it was a get request
        cross_form = CrossTaskForm(department)
        context = {'form': cross_form, 'id_form' : id_form, 'title':title, 'tasktype': "cross", 'primkey': primkey, 'info':info}
        html_content = render_to_string('tasks/task.html', context, context_instance=RequestContext(request))
        dajax.assign("#id_content_right", "innerHTML", html_content) # Populate modal
    return dajax.json()
    
    

# _____________--- DELETE A TASK - INTRA/CROSS ---______________#
@dajaxice_register(name="tasks.delete_task")
@login_required
@user_passes_test (core_check)
def delete_task(request, primkey):
    """
        This function handles deleting any task
        CORES : (ONLY)
            Only they can delete tasks.
        
        Renders in : alert
        Refreshes : right_content
    """
    dajax = Dajax()
    try:
        task = Task.objects.get(pk = primkey)
        subj = task.subject
        task.delete()
        show_alert(dajax, "success", "Task " + subj + " was deleted !") # Shows alert
        dajax.script("modal_hide()") # This refreshes the current tab to update what changes need to be made
    except:
        show_alert(dajax, "error", "That task does not exist !") # Shows alert
        
    return dajax.json()
