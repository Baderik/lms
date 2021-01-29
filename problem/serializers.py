from rest_framework import serializers

from cathie.cats_api import cats_submit_solution
from lesson.models import Lesson
from problem.models import Problem, Submit
from users.serializers import DefaultUserSerializer


class SubmitSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    problem = serializers.PrimaryKeyRelatedField(queryset=Problem.objects.all())
    student = DefaultUserSerializer(read_only=True)
    content = serializers.CharField()
    cats_request_id = serializers.IntegerField(read_only=True)
    status = serializers.ChoiceField(choices=Submit.SUBMIT_STATUS, default='NP')

    def update(self, instance, validated_data):
        print(validated_data)
        instance.content = validated_data.get('content', instance.content)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

    def create(self, validated_data):
        request = self.context.get('request')
        student = request.user if request and hasattr(request, 'user') else None
        cats_request_id = cats_submit_solution(
            validated_data.get('content'),
            validated_data.get('cats_problem_id'),
            validated_data.get('cats_de_id'),
            validated_data.get('source')
        )
        return Submit.objects.create(**validated_data, **{
            'student': student,
        })

    class Meta:
        model = Submit
        fields = ['id', 'problem', 'student', 'content', 'status']


class ProblemSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all())
    author = DefaultUserSerializer(required=False, read_only=True)
    name = serializers.CharField()
    description = serializers.CharField()
    submits = SubmitSerializer(many=True, read_only=True)
    manual = serializers.BooleanField()
    type = serializers.CharField()
    language = serializers.CharField(required=True, allow_null=True)
    cats_material_url = serializers.CharField()
    # success_or_last_submits = serializers.SerializerMethodField()

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.author = validated_data.get('author', instance.author)
        instance.save()
        return instance

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request and hasattr(request, "user") else None
        return Problem.objects.create(**validated_data, **{'author': user})

    # def get_success_or_last_submits(self, obj):
    #     submit_query = Submit.objects.filter(problem=obj).order_by('id')
    #     submits_ok = submit_query.filter(status="OK").distinct('student')
    #     submits_aw = submit_query.filter(status="AW").distinct('student')
    #     submits = submit_query.distinct('student')
    #     query = (submits_ok + submits_aw + submits).distinct('student')
    #     return SubmitSerializer(query, many=True)

    class Meta:
        model = Problem
        fields = (
            'id', 'name', 'description', 'author', 'lesson', 'submits',
            'manual', 'type', 'language', 'cats_material_url', 'cats_id',  # 'success_or_last_submits'
        )
