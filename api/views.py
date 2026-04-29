import json
from datetime import date
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from academics.models import Classroom
from academics.models import Grade
from academics.models import Subject
from attendance.models import AttendanceRecord
from students.models import Student


def _parse_json_body(request: HttpRequest) -> tuple[dict, JsonResponse | None]:
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
        if not isinstance(payload, dict):
            return {}, JsonResponse({"error": "JSON body must be an object."}, status=400)
        return payload, None
    except json.JSONDecodeError:
        return {}, JsonResponse({"error": "Invalid JSON payload."}, status=400)


def _serialize_student(student: Student) -> dict:
    return {
        "id": student.id,
        "admission_number": student.admission_number,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "full_name": student.full_name,
        "date_of_birth": student.date_of_birth.isoformat(),
        "classroom": {
            "id": student.current_classroom_id,
            "code": student.current_classroom.code if student.current_classroom else "",
            "name": student.current_classroom.name if student.current_classroom else "",
        },
        "guardian_name": student.guardian_name,
        "contact_email": student.contact_email,
        "contact_phone": student.contact_phone,
        "status": student.status,
    }


def _serialize_classroom(classroom: Classroom) -> dict:
    return {
        "id": classroom.id,
        "name": classroom.name,
        "code": classroom.code,
        "description": classroom.description,
        "homeroom_teacher_id": classroom.homeroom_teacher_id,
    }


def _serialize_subject(subject: Subject) -> dict:
    return {
        "id": subject.id,
        "name": subject.name,
        "code": subject.code,
        "classroom_id": subject.classroom_id,
        "teacher_id": subject.teacher_id,
        "weekly_sessions": subject.weekly_sessions,
    }


def _serialize_attendance(record: AttendanceRecord) -> dict:
    return {
        "id": record.id,
        "student_id": record.student_id,
        "classroom_id": record.classroom_id,
        "subject_id": record.subject_id,
        "date": record.date.isoformat(),
        "status": record.status,
        "notes": record.notes,
        "recorded_by_id": record.recorded_by_id,
    }


def _serialize_grade(grade: Grade) -> dict:
    return {
        "id": grade.id,
        "student_id": grade.student_id,
        "assessment_id": grade.assessment_id,
        "score": str(grade.score),
        "remarks": grade.remarks,
        "percentage": round(grade.percentage, 2),
        "letter_grade": grade.letter_grade,
        "entered_by_id": grade.entered_by_id,
    }


def _is_write_allowed(request: HttpRequest) -> bool:
    if not getattr(request.user, "is_authenticated", False):
        return False
    return request.user.is_superuser or request.user.role in {"ADMIN", "STAFF", "TEACHER"}


@csrf_exempt
@login_required
def students_collection(request: HttpRequest):
    if request.method == "GET":
        students = Student.objects.select_related("current_classroom").all()
        status_filter = request.GET.get("status", "").strip()
        classroom_id = request.GET.get("classroom_id", "").strip()

        if status_filter:
            students = students.filter(status=status_filter)
        if classroom_id:
            students = students.filter(current_classroom_id=classroom_id)

        return JsonResponse({"results": [_serialize_student(s) for s in students]}, status=200)

    if request.method == "POST":
        if not _is_write_allowed(request):
            return JsonResponse({"error": "Insufficient permissions."}, status=403)

        payload, err = _parse_json_body(request)
        if err:
            return err

        required = ["admission_number", "first_name", "last_name", "date_of_birth", "guardian_name"]
        missing = [field for field in required if not payload.get(field)]
        if missing:
            return JsonResponse({"error": f"Missing required fields: {', '.join(missing)}"}, status=400)

        try:
            student = Student(
                admission_number=str(payload["admission_number"]).strip(),
                first_name=str(payload["first_name"]).strip(),
                last_name=str(payload["last_name"]).strip(),
                date_of_birth=date.fromisoformat(str(payload["date_of_birth"])),
                guardian_name=str(payload["guardian_name"]).strip(),
                contact_email=str(payload.get("contact_email", "")).strip(),
                contact_phone=str(payload.get("contact_phone", "")).strip(),
                status=str(payload.get("status") or Student.Status.ACTIVE).strip(),
                current_classroom_id=payload.get("current_classroom_id") or None,
            )
            student.full_clean()
            student.save(
                enrollment_actor=request.user,
                enrollment_note="Student onboarded via API v1.",
            )
            return JsonResponse(_serialize_student(student), status=201)
        except Exception as exc:
            return JsonResponse({"error": str(exc)}, status=400)

    return HttpResponseNotAllowed(["GET", "POST"])


@csrf_exempt
@login_required
def student_detail(request: HttpRequest, pk: int):
    student = Student.objects.select_related("current_classroom").filter(pk=pk).first()
    if not student:
        return JsonResponse({"error": "Student not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(_serialize_student(student), status=200)

    if request.method in {"PATCH", "PUT"}:
        if not _is_write_allowed(request):
            return JsonResponse({"error": "Insufficient permissions."}, status=403)

        payload, err = _parse_json_body(request)
        if err:
            return err

        editable_fields = [
            "first_name",
            "last_name",
            "guardian_name",
            "contact_email",
            "contact_phone",
            "status",
            "current_classroom_id",
        ]

        for field in editable_fields:
            if field in payload:
                setattr(student, field, payload[field])

        if "date_of_birth" in payload:
            student.date_of_birth = date.fromisoformat(str(payload["date_of_birth"]))

        try:
            student.full_clean()
            student.save(
                enrollment_actor=request.user,
                enrollment_note="Student updated via API v1.",
            )
            return JsonResponse(_serialize_student(student), status=200)
        except Exception as exc:
            return JsonResponse({"error": str(exc)}, status=400)

    if request.method == "DELETE":
        if not (request.user.is_superuser or request.user.role == "ADMIN"):
            return JsonResponse({"error": "Only admin can delete students."}, status=403)
        student.delete()
        return JsonResponse({}, status=204)

    return HttpResponseNotAllowed(["GET", "PATCH", "PUT", "DELETE"])


@login_required
def classrooms_collection(request: HttpRequest):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    classrooms = Classroom.objects.select_related("homeroom_teacher").all()
    return JsonResponse({"results": [_serialize_classroom(c) for c in classrooms]}, status=200)


@login_required
def subjects_collection(request: HttpRequest):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    subjects = Subject.objects.select_related("classroom", "teacher").all()
    classroom_id = request.GET.get("classroom_id", "").strip()
    if classroom_id:
        subjects = subjects.filter(classroom_id=classroom_id)
    return JsonResponse({"results": [_serialize_subject(s) for s in subjects]}, status=200)


@csrf_exempt
@login_required
def attendance_collection(request: HttpRequest):
    if request.method == "GET":
        records = AttendanceRecord.objects.select_related("student", "classroom", "subject").all()
        date_from = request.GET.get("date_from", "").strip()
        date_to = request.GET.get("date_to", "").strip()
        classroom_id = request.GET.get("classroom_id", "").strip()
        status_filter = request.GET.get("status", "").strip()

        if date_from:
            records = records.filter(date__gte=date_from)
        if date_to:
            records = records.filter(date__lte=date_to)
        if classroom_id:
            records = records.filter(classroom_id=classroom_id)
        if status_filter:
            records = records.filter(status=status_filter)

        return JsonResponse({"results": [_serialize_attendance(r) for r in records]}, status=200)

    if request.method == "POST":
        if not _is_write_allowed(request):
            return JsonResponse({"error": "Insufficient permissions."}, status=403)

        payload, err = _parse_json_body(request)
        if err:
            return err

        required = ["student_id", "classroom_id", "date", "status"]
        missing = [field for field in required if payload.get(field) in (None, "")]
        if missing:
            return JsonResponse({"error": f"Missing required fields: {', '.join(missing)}"}, status=400)

        try:
            record = AttendanceRecord(
                student_id=payload["student_id"],
                classroom_id=payload["classroom_id"],
                subject_id=payload.get("subject_id") or None,
                date=date.fromisoformat(str(payload["date"])),
                status=str(payload["status"]).strip(),
                notes=str(payload.get("notes", "")).strip(),
                recorded_by=request.user,
            )
            record.full_clean()
            record.save()
            return JsonResponse(_serialize_attendance(record), status=201)
        except Exception as exc:
            return JsonResponse({"error": str(exc)}, status=400)

    return HttpResponseNotAllowed(["GET", "POST"])


@csrf_exempt
@login_required
def grades_collection(request: HttpRequest):
    if request.method == "GET":
        grades = Grade.objects.select_related("student", "assessment", "assessment__subject").all()
        student_id = request.GET.get("student_id", "").strip()
        subject_id = request.GET.get("subject_id", "").strip()

        if student_id:
            grades = grades.filter(student_id=student_id)
        if subject_id:
            grades = grades.filter(assessment__subject_id=subject_id)

        return JsonResponse({"results": [_serialize_grade(g) for g in grades]}, status=200)

    if request.method == "POST":
        if not _is_write_allowed(request):
            return JsonResponse({"error": "Insufficient permissions."}, status=403)

        payload, err = _parse_json_body(request)
        if err:
            return err

        required = ["student_id", "assessment_id", "score"]
        missing = [field for field in required if payload.get(field) in (None, "")]
        if missing:
            return JsonResponse({"error": f"Missing required fields: {', '.join(missing)}"}, status=400)

        try:
            grade = Grade(
                student_id=payload["student_id"],
                assessment_id=payload["assessment_id"],
                score=Decimal(str(payload["score"])),
                remarks=str(payload.get("remarks", "")).strip(),
                entered_by=request.user,
            )
            grade.full_clean()
            grade.save()
            return JsonResponse(_serialize_grade(grade), status=201)
        except Exception as exc:
            return JsonResponse({"error": str(exc)}, status=400)

    return HttpResponseNotAllowed(["GET", "POST"])
