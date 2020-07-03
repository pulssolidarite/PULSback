# Backend for Fleet Management
Backend using Django REST Framework for our fleet management. You can find the frontend on https://github.com/hilaliMoncef/PULSfront
We are using Heroku for deployment and Amazon S3 for static files serving.

### Used plugins
```
asgiref==3.2.3
boto3==1.10.45
botocore==1.13.45
dj-database-url==0.5.0
Django==3.0.3
django-cors-headers==3.2.0
django-heroku==0.3.1
django-storages==1.8
djangorestframework==3.10.3
docutils==0.15.2
gunicorn==20.0.4
jmespath==0.9.4
numpy==1.17.4
pandas==0.25.3
psycopg2==2.8.4
python-dateutil==2.8.1
pytz==2019.3
s3transfer==0.2.1
six==1.13.0
sqlparse==0.3.0
urllib3==1.25.7
whitenoise==5.0.1
```

### Used endpoints
```
# Login and user management
path('api-auth', include('rest_framework.urls')),
path('auth/', CustomObtainAuthToken.as_view()),
path('user/', UserList.as_view()),
path('user/<int:pk>/', UserDetail.as_view()),

# Routers
router = DefaultRouter()
router.register(r'customer', CustomerViewSet)
router.register(r'campaign', CampaignViewSet)
router.register(r'game', GameViewSet)
router.register(r'terminal', TerminalViewSet)
router.register(r'donator', DonatorViewSet)
router.register(r'session', SessionViewSet)
router.register(r'payment', PaymentViewSet)

# GET method : getting donator by email
path('donator/email/<str:email>/', DonatorByEmail.as_view()),

# GET methods : Activation and deactivation for models
path('customer/<int:pk>/activate/', ActivateCustomer.as_view()),
path('customer/<int:pk>/deactivate/', DeactivateCustomer.as_view()),
path('terminal/<int:pk>/activate/', ActivateTerminal.as_view()),
path('terminal/<int:pk>/deactivate/', DeactivateTerminal.as_view()),

# GET methods : Getting only campaigns activated on terminal
path('terminal/<int:pk>/campaigns/', CampaignsByTerminal.as_view()),

# GET method : Getting only games activated on terminal
path('terminal/<int:pk>/games/', GamesByTerminal.as_view()),

# GET methods : Acivating differents states on a terminal, used for fleet status management
path('terminal/mine/', TerminalByOwner.as_view()),
path('terminal/mine/on/', TurnOnTerminal.as_view()),
path('terminal/mine/off/', TurnOffTerminal.as_view()),
path('terminal/mine/play/', PlayingOnTerminal.as_view()),
path('terminal/mine/gameover/', PlayingOffTerminal.as_view()),

# GET methods : different statistics for the admin dashboard
path('terminal/<int:terminal>/stats/', StatsByTerminal.as_view()),
path('session/terminal/<int:terminal>/avg/', AvgSessionByTerminal.as_view()),
path('campaign/<int:id>/stats/', StatsByCampaign.as_view()),
path('campaign/<int:id>/full/', StatsByCampaign.as_view()),
path('campaigns/full/', StatsByCampaign.as_view()),
path('dashboard/', DashboardStats.as_view())
```

### Errors & fixes
Please feel free to create pull requests in case you find any critical issue.
