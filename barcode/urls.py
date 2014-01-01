from django.conf.urls import patterns, include, url


urlpatterns = patterns('barcode.views',
    url(r'^csv/barcode/$', 'upload_csv', {'type': "barcodeportal"}, name = "barcodeportal"),
    url(r'^csv/participants/$', 'upload_csv', {'type': "participantsportal"}, name = "participantsportal"),
    url(r'^csv/add_single_barcode/$','add_single_entry',{'type': "barcodeportal"},name="add_single_barcode"),
    url(r'^csv/add_single_participant/$','add_single_entry',{'type': "participantsportal"},name="add_single_participant"),
    url(r'^get_details/(?P<sh_id>\w)/$','get_details'),#tried to get shaastra id search query from url
#    url(r'^get_details','get_details')
)
