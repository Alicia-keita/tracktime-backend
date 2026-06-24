from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, time

User = get_user_model()

from .chat import ChatMessage