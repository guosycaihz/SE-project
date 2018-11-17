from ASP.models import UserData

class UserWeb():
    def user_test(request, type):
        if request.user.is_authenticated:
            user = UserData.objects.get(user_name=request.user)
            if user.type == type:
                return True
        return False