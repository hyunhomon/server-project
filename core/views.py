from django.shortcuts import get_object_or_404
from rest_framework import status, response, decorators, permissions
from django.contrib.auth.hashers import make_password, check_password
from . import models, utils

@decorators.api_view(['POST'])
@decorators.permission_classes([permissions.AllowAny])
def login(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')

    user = get_object_or_404(models.User, username=username)

    if not check_password(password, user.password):
        return response.Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
    
    tokens = utils.generate_tokens(user)

    return response.Response({"message": "Login successful.", "tokens": tokens}, status=status.HTTP_200_OK)

@decorators.api_view(['POST'])
@decorators.permission_classes([permissions.AllowAny])
def register(request):
    data = request.data
    name = data.get('name')
    username = data.get('username')
    password = data.get('password')

    if models.User.objects.filter(username=username).exists():
        return response.Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

    user = models.User.objects.create(
        username=username,
        password=make_password(password),
        name=name
    )
    tokens = utils.generate_tokens(user)

    return response.Response({"message": "User registered successfully.", "tokens": tokens}, status=status.HTTP_201_CREATED)

@decorators.api_view(['GET'])
@decorators.permission_classes([permissions.IsAuthenticated])
def get_user_info(request):
    user = request.user
    return response.Response({
        "username": user.username,
        "name": user.name,
        "modified_times_ago": utils.modified_times_ago(user.modified_at)
    }, status=200)

@decorators.api_view(['GET'])
@decorators.permission_classes([permissions.IsAuthenticated])
def get_user_follows(request):
    user = request.user
    follow_usernames = user.follows
    follow_users = models.User.objects.filter(username__in=follow_usernames).values('name', 'modified_at')
    follow_list = []

    for follow_user in follow_users:
        name = follow_user['name']
        modified_at = follow_user['modified_at']
        follow_list.append({
            "name": name,
            "modified_times_ago": utils.modified_times_ago(modified_at)
        })

    return response.Response(follow_list, status=200)

@decorators.api_view(['GET'])
@decorators.permission_classes([permissions.IsAuthenticated])
def get_user_notifications(request):
    user = request.user
    notifications = user.notifications
    return response.Response(notifications, status=200)

@decorators.api_view(['GET'])
@decorators.permission_classes([permissions.IsAuthenticated])
def get_user_categories(request):
    user = request.user
    categories = models.Category.objects.filter(owner=user).values('id', 'name', 'content')
    return response.Response(list(categories), status=200)

@decorators.api_view(['POST'])
@decorators.permission_classes([permissions.IsAuthenticated])
def add_category(request):
    data = request.data

    username = data.get('username')
    name = data.get('name')
    content = data.get('content', '')

    target_user = get_object_or_404(models.User, username=username)

    if not name:
        return response.Response({"error": "Category name is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    category = models.Category.objects.create(owner=target_user, name=name, content=content)

    utils.notify_followers(target_user, name, content)

    return response.Response({
        "message": "Category added successfully.",
        "category": {
            "id": category.id,
            "name": category.name,
            "content": category.content,
        }
    }, status=status.HTTP_201_CREATED)

@decorators.api_view(['POST'])
@decorators.permission_classes([permissions.IsAuthenticated])
def mod_category(request):
    data = request.data

    id = data.get('id')
    name = data.get('name')
    content = data.get('content', '')

    if not id:
        return response.Response({"error": "Category ID is required."}, status=status.HTTP_400_BAD_REQUEST)
    if not name:
        return response.Response({"error": "Category name is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        category = models.Category.objects.get(id=id)
    except models.Category.DoesNotExist:
        return response.Response({"error": "Category not found or you do not have permission to edit it."}, status=status.HTTP_404_NOT_FOUND)

    category.name = name
    category.content = content
    category.save()

    utils.notify_followers(category.owner, name, content)

    return response.Response({
        "message": "Category updated successfully.",
        "category": {
            "id": category.id,
            "name": category.name,
            "content": category.content,
        }
    }, status=status.HTTP_200_OK)

@decorators.api_view(['POST'])
@decorators.permission_classes([permissions.IsAuthenticated])
def add_follow(request):
    user = request.user
    data = request.data

    target_username = data.get('username')

    if not target_username:
        return response.Response({"error": "Target username is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        target_user = models.User.objects.get(username=target_username)
    except models.User.DoesNotExist:
        return response.Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    if user.username == target_username:
        return response.Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
    if target_username in user.follows:
        return response.Response({"error": "You are already following this user."}, status=status.HTTP_400_BAD_REQUEST)

    user.follows.append(target_username)
    user.save()

    return response.Response({
        "message": f"You are now following {target_username}.",
        "follows": user.follows,
    }, status=status.HTTP_200_OK)

@decorators.api_view(['POST'])
@decorators.permission_classes([permissions.IsAuthenticated])
def del_follow(request):
    user = request.user
    data = request.data

    target_username = data.get('username')

    if not target_username:
        return response.Response({"error": "Target username is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    if target_username not in user.follows:
        return response.Response({"error": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)

    user.follows.remove(target_username)
    user.save()

    return response.Response({
        "message": f"You have unfollowed {target_username}.",
        "follows": user.follows,
    }, status=status.HTTP_200_OK)
