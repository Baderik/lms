import django_filters
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from cathie.cats_api import cats_get_problem_description_by_url
from course.models import Course
from lesson.models import Lesson
from problem.models import Problem, Submit, CatsSubmit
from problem.serializers import ProblemSerializer, SubmitSerializer, SubmitListSerializer
from users.models import User


class ProblemViewSet(viewsets.ModelViewSet):
    serializer_class = ProblemSerializer
    queryset = Problem.objects.all()
    filterset_fields = ['lesson_id', ]


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 1000


class SubmitFilter(django_filters.FilterSet):
    course = django_filters.ModelChoiceFilter(
        label='course', queryset=Course.objects.all(), method='course_filter'
    )
    lesson = django_filters.ModelChoiceFilter(
        label='lesson', queryset=Lesson.objects.all(), method='lesson_filter'
    )

    class Meta:
        model = Submit
        fields = ['problem', 'student', 'status', 'cats_submit__is_sent', ]

    def course_filter(self, queryset, name, value):
        queryset = queryset.filter(lesson__course=value)
        return queryset

    def lesson_filter(self, queryset, name, value):
        queryset = queryset.filter(**{f'problem__{name}': value})
        return queryset


class SubmitViewSet(viewsets.ModelViewSet, viewsets.GenericViewSet):
    serializer_class = SubmitSerializer
    queryset = Submit.objects.prefetch_related('cats_submit').all()
    pagination_class = StandardResultsSetPagination
    filterset_class = SubmitFilter

    def get_queryset(self):
        user = self.request.user
        queryset = Submit.objects.filter(
            Q(student=user) | Q(problem__lesson__course__in=user.staff_for.all())
        )
        problem_id = self.request.query_params.get('', None)
        user_id = self.request.query_params.get('', None)
        course_id = self.request.query_params.get('', None)
        lesson_id = self.request.query_params.get('', None)
        if course_id:
            queryset = queryset.filter(lesson__course__id=course_id)
        if lesson_id:
            queryset = queryset.filter(lesson__course__id=lesson_id)

        if problem_id:
            user = User.objects.get(pk=user_id) if user_id else None
            is_staff = True if user and user.is_staff else False
            if is_staff:
                return queryset.filter(problem__id=problem_id)
            elif user:
                return queryset.filter(problem__id=problem_id, student__id=user_id)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubmitListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SubmitListSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        request = serializer.context["request"]
        validated_data = serializer.validated_data
        cats = CatsSubmit(data=dict(
            source_text=validated_data.get('content'),
            problem_id=validated_data.get('cats_problem_id'),
            de_id=validated_data.get('cats_de_id'),
            source=validated_data.get('source'),
        ))
        model = serializer.save(student=request.user, status=Submit.DEFAULT_STATUS)
        cats.submit = model
        cats.save()
        return


@login_required
@api_view(['POST'])
@renderer_classes([JSONRenderer])
def add_cats_problems(request, lesson_id):
    lesson = Lesson.objects.get(pk=lesson_id)
    data = request.data
    answer = list()
    for cats_problem in data:
        materials = cats_get_problem_description_by_url(cats_problem["text_url"])
        problem = Problem.objects.create(
            lesson=lesson, author=request.user, name=cats_problem['name'],
            cats_id=cats_problem['id'], cats_material_url=cats_problem["text_url"],
            description=materials,
        )
        answer.append(ProblemSerializer(problem).data)
    return Response(answer)
