import json
import base64
import razorpay
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from digiotal_jazz.agent import Agent, Task, InputType, OutputType
from digiotal_jazz.openai_model import OpenAIModel
from digiotal_jazz.arch import SequentialFlow
from .database import SQLiteDB
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.core.mail import EmailMessage
from django.core.mail import BadHeaderError, send_mail
import logging
import requests


logger = logging.getLogger(__name__)

import json
import base64
import logging
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


# logger = logging.getLogger(__name__)

load_dotenv()
db = SQLiteDB()

expertise = "Interior Designer"
task = Task("Image Generation")
input_type = InputType("Text")
output_type = OutputType("Image")
agent = Agent(expertise, task, input_type, output_type)


@csrf_exempt
def login_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            # Check for missing fields
            if not all([username, password]):
                logger.error("Missing fields: username or password")
                return JsonResponse({"error": "Missing fields"}, status=400)

            user = authenticate(username=username, password=password)

            if user is not None:
                if not user.is_active:
                    logger.error(f"Inactive user: {username}")
                    return JsonResponse({"error": "Inactive account"}, status=400)

                token, created = Token.objects.get_or_create(user=user)
                user_details = {
                    "username": user.username,
                    "email": user.email,
                    "token": token.key,
                }
                return JsonResponse(user_details, status=200)
            else:
                logger.error(f"Invalid credentials for user: {username}")
                return JsonResponse({"error": "Invalid credentials"}, status=400)
        
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.exception("Exception during user login")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid HTTP method"}, status=405)

@csrf_exempt
def register_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            email = data.get("email")
            password1 = data.get("password1")
            password2 = data.get("password2")

            # Check for missing fields
            if not all([username, email, password1, password2]):
                logger.error("Missing fields: username, email, password1, or password2")
                return JsonResponse({"error": "Missing fields"}, status=400)

            if password1 != password2:
                logger.error("Passwords do not match")
                return JsonResponse({"error": "Passwords do not match"}, status=400)

            if User.objects.filter(username=username).exists():
                logger.error("Username already exists")
                return JsonResponse({"error": "Username already exists"}, status=400)

            if User.objects.filter(email=email).exists():
                logger.error("Email already registered")
                return JsonResponse({"error": "Email already registered"}, status=400)

            user = User.objects.create_user(username=username, email=email, password=password1)
            token, created = Token.objects.get_or_create(user=user)  # Get or create token
            return JsonResponse({"token": token.key}, status=201)
        
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.exception("Exception during user registration")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid HTTP method"}, status=405)


@csrf_exempt
def generateImage(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            api_key = data.get("api_key")
            selected_style = data.get("selected_style")
            selected_room_color = data.get("selected_room_color")
            selected_room_type = data.get("selected_room_type")

            if not (selected_style and selected_room_color and selected_room_type):
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Assuming these fields are base64 encoded image data in the JSON payload
            s_style = base64.b64encode(selected_style.encode('utf-8')).decode('utf-8')
            s_room_c = base64.b64encode(selected_room_color.encode('utf-8')).decode('utf-8')
            s_room_t = base64.b64encode(selected_room_type.encode('utf-8')).decode('utf-8')

            prompt = f"Generate a final Image based on the 3 input images provided: Image_1={s_style}, Image_2={s_room_c}, Image_3={s_room_t}"

            model = OpenAIModel(api_key=api_key, model="dall-e-2")
            sequential_flow = SequentialFlow(agent, model)

            image_url = sequential_flow.execute(prompt)
            return JsonResponse({"image": image_url, "status": "Success"})
        except Exception as e:
            logger.exception("Exception during image generation")
            return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def send_email(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print(data)
            email = data.get("email1")
            image_url = data.get("imageUrl")
            Selected_type = data.get("Select_Type")
            Selected_style = data.get("Select_Style")
            Selected_color = data.get("Select_Color")

            logger.info(f"Received email: {email}")
            logger.info(f"Received imageURL: {image_url}")
            
            if not email or not image_url:
                logger.error("Missing email or imageURL")
                return JsonResponse({"error": "Missing email or imageURL"}, status=400)

            # Fetch the image from the URL
            response = requests.get(image_url)
            if response.status_code != 200:
                logger.error("Failed to fetch image from URL")
                return JsonResponse({"error": "Failed to fetch image from URL"}, status=400)

            # Convert image to base64
            image_data = response.content

            # Create the email with the image attachment
            email_message = EmailMessage(
                "Interior Design",
                f"Please find the generated image attached. Count = 1\n"
                f"Selected type: {Selected_type}\n"
                f"Selected style: {Selected_style}\n"
                f"Selected color: {Selected_color}",
                "shivshankarrao696@gmail.com",
                [email],
            )
            email_message.attach("generated_image.png", image_data, "image/png")
            email_message.send()

            return JsonResponse({"status": "Email sent successfully"}, status=200)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.exception("Exception during email sending")
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid HTTP method"}, status=405)
