from users.models import *

def create_junk_profile(shaastra_id):
    shaastra_id = str(shaastra_id)
    user = User.objects.using('mainsite').get_or_create(username = shaastra_id,email = shaastra_id +'@'+shaastra_id+'.com',password = 'default' )[0]
    user.first_name = 'Junk'
    print '*************'
    user.is_staff = True
    user.save(using = 'mainsite')
    try:
        UserProfile.objects.get(user = user)
        return UserProfile.objects.get(user = user)
    except:
        profile = UserProfile.objects.using('mainsite').get_or_create(user = user)[0]
        profile.user = user = user
        profile.gender = 'F'
        profile.age = 0
        profile.branch = 'Others'
        profile.shaastra_id = str(1500000 - user.id)        
        print '!*--------------!!!!'
        profile.save(using = 'mainsite')
        return profile

def id_is_valid(sh_id):
    if len(sh_id) == 10 and sh_id[:5] == 'SHA14' and sh_id[5:].isdigit():
        return True
    return False

def id_in_db(shid):
    up = get_userprofile(shid)
    if up is None:
        return False
    return True

def is_valid_insti_roll(roll):
    #TODO::
    if len(roll)==8 and roll[:2].isalpha() and roll[2:4].isdigit() and roll[4].isalpha() and roll[5:].isdigit():
        return True
    return False

def get_userprofile(shaastra_id = None):
    if shaastra_id is None:
        return None
    try:
        up = UserProfile.objects.using('mainsite').filter(shaastra_id = shaastra_id)[0]
    except:
        return None
    return up

def is_junk(profile):
    if profile.user.is_staff:
        return True
    #returns 0 for 
    return False
    #TODO
    
        
