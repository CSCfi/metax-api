# This file is part of the Metax API service
#
# Copyright 2017-2018 Ministry of Education and Culture, Finland
#
# :author: CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# :license: MIT

"""metax_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include

from metax_api.api.oaipmh.base.view import oaipmh_view as oaipmh
from metax_api.api.rest.base.router import api_urlpatterns as api_v1
from metax_api.views.router import view_urlpatterns

urlpatterns = [
    url('', include(view_urlpatterns)),
    url(r'^rest/', include(api_v1)),
    url(r'^rest/v1/', include(api_v1)),
    url(r'^oai/', oaipmh, name='oai'),
]
