from django.contrib.auth.models import User
from django.core.files import File
from django.http import HttpResponse
from persiantools.jdatetime import JalaliDate, JalaliDateTime
from rest_framework import permissions, authentication, filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_200_OK
from rest_framework.views import APIView

from rollcall import models
from rollcall.excel_converter import ExcelConverter
from rollcall.models import Rollout, UserDetail
from rollcall.serializers import RolloutSerializer, UserDetailSerializer, UserSerializer


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['POST'], detail=False, url_path="register", permission_classes=[])
    def register(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)

    @action(methods=['GET', 'PUT'], detail=False, url_path="self")
    def self_user_endpoint(self, request, *args, **kwargs):
        if request.method == "GET":
            return self._get_current_user(request, *args, **kwargs)
        elif request.method == "PUT":
            return self._update_current_user(request, *args, **kwargs)
        else:
            raise Exception(f"Unexpected method: {request.method}")

    @staticmethod
    def _get_current_user(request, *args, **kwargs):
        serializer = UserSerializer(instance=request.user, context={"request": request})
        return Response(serializer.data)

    @staticmethod
    def _update_current_user(request, *args, **kwargs):
        user_data = {key: val for key, val in request.data.items() if key != 'detail'}
        user_detail_data = request.data.get('detail', {})
        user_serializer = UserSerializer(request.user, user_data, partial=True)
        user_detail_serializer = UserDetailSerializer(request.user.detail, user_detail_data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_detail_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        user_detail_serializer.save()
        return Response(status=HTTP_200_OK)


class RolloutViewSet(viewsets.ModelViewSet):
    serializer_class = RolloutSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['time']
    ordering = ['-time']

    def get_queryset(self):
        user = self.request.user
        return Rollout.objects.filter(user=user)


class ReportRollouts(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication,
                              authentication.BasicAuthentication,
                              authentication.SessionAuthentication]

    def get(self, request, username, year, month):
        if request.user.username != username and not request.user.is_superuser:
            return HttpResponse("", status=HTTP_403_FORBIDDEN)
        user = models.User.objects.get(username=username)
        total_days = JalaliDate.days_in_month(month=month, year=year)
        date_from = JalaliDateTime(year=year, month=month, day=1).to_gregorian()
        date_to = JalaliDateTime(year=year, month=month, day=total_days, hour=23, minute=59, second=59,
                                 microsecond=999999).to_gregorian()
        rollouts = Rollout.objects \
            .filter(user=user) \
            .filter(time__gte=date_from,
                    time__lte=date_to) \
            .order_by('time')

        excel_file = ExcelConverter(user, rollouts, starting_date=date_from).get_excel_file()
        response = HttpResponse(File(excel_file),
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=timesheet.xlsx'
        return response
