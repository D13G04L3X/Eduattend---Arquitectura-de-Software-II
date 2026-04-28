from datetime import date
from http import HTTPStatus

from flask import Blueprint, jsonify, request

from ....application.ports.inbound.i_attendance_operations_use_case import (
    IAttendanceOperationsUseCase,
)
from ....application.usecases import RegisterAttendanceCommand, UpdateAttendanceCommand
from ....domain.model.attendance import Attendance


def create_attendance_blueprint(
    attendance_operations_use_case: IAttendanceOperationsUseCase,
) -> Blueprint:
    blueprint = Blueprint("attendance", __name__)

    @blueprint.post("/api/v1/attendance")
    def register_attendance():
        """
        Registrar asistencia
        ---
        tags:
            - Attendance
        requestBody:
            required: true
            content:
                application/json:
                    schema:
                        type: object
                        required:
                            - student_id
                            - course_id
                            - class_session_id
                        properties:
                            student_id:
                                type: string
                                example: S1
                            course_id:
                                type: string
                                example: MAT101
                            class_session_id:
                                type: string
                                example: CLASE-01
                            attendance_date:
                                type: string
                                format: date
                                example: 2026-03-16
        responses:
            201:
                description: Asistencia registrada
            400:
                description: Error de validacion
            409:
                description: Registro duplicado
        """
        payload = request.get_json(silent=True) or {}
        validation_error = _validate_payload(payload, include_date=False)
        if validation_error is not None:
            return validation_error

        attendance_date, date_error = _parse_attendance_date(payload, required=False)
        if date_error is not None:
            return date_error

        command = RegisterAttendanceCommand(
            student_id=str(payload["student_id"]),
            course_id=str(payload["course_id"]),
            class_session_id=str(payload["class_session_id"]),
            attendance_date=attendance_date,
        )
        attendance = attendance_operations_use_case.register_attendance(command)
        return jsonify(_attendance_to_dict(attendance)), HTTPStatus.CREATED

    @blueprint.get("/api/v1/attendance")
    def list_attendance():
        """
        Listar asistencias
        ---
        tags:
            - Attendance
        responses:
            200:
                description: Lista de asistencias registradas
        """
        attendances = attendance_operations_use_case.list_attendances()
        return jsonify([_attendance_to_dict(attendance) for attendance in attendances])

    @blueprint.get("/api/v1/attendance/<int:attendance_id>")
    def get_attendance(attendance_id: int):
        """
        Obtener asistencia por ID
        ---
        tags:
            - Attendance
        parameters:
            - name: attendance_id
              in: path
              required: true
              schema:
                type: integer
        responses:
            200:
                description: Asistencia encontrada
            404:
                description: Asistencia no encontrada
        """
        attendance = attendance_operations_use_case.get_attendance_by_id(attendance_id)
        return jsonify(_attendance_to_dict(attendance)), HTTPStatus.OK

    @blueprint.put("/api/v1/attendance/<int:attendance_id>")
    def update_attendance(attendance_id: int):
        """
        Actualizar asistencia
        ---
        tags:
            - Attendance
        parameters:
            - name: attendance_id
              in: path
              required: true
              schema:
                type: integer
        requestBody:
            required: true
            content:
                application/json:
                    schema:
                        type: object
                        required:
                            - student_id
                            - course_id
                            - class_session_id
                            - attendance_date
                        properties:
                            student_id:
                                type: string
                            course_id:
                                type: string
                            class_session_id:
                                type: string
                            attendance_date:
                                type: string
                                format: date
        responses:
            200:
                description: Asistencia actualizada
            400:
                description: Error de validacion
            404:
                description: Asistencia no encontrada
            409:
                description: Registro duplicado
        """
        payload = request.get_json(silent=True) or {}
        validation_error = _validate_payload(payload, include_date=True)
        if validation_error is not None:
            return validation_error

        attendance_date, date_error = _parse_attendance_date(payload, required=True)
        if date_error is not None:
            return date_error

        command = UpdateAttendanceCommand(
            student_id=str(payload["student_id"]),
            course_id=str(payload["course_id"]),
            class_session_id=str(payload["class_session_id"]),
            attendance_date=attendance_date,
        )
        attendance = attendance_operations_use_case.update_attendance(attendance_id, command)
        return jsonify(_attendance_to_dict(attendance)), HTTPStatus.OK

    @blueprint.delete("/api/v1/attendance/<int:attendance_id>")
    def delete_attendance(attendance_id: int):
        """
        Eliminar asistencia
        ---
        tags:
            - Attendance
        parameters:
            - name: attendance_id
              in: path
              required: true
              schema:
                type: integer
        responses:
            204:
                description: Asistencia eliminada
            404:
                description: Asistencia no encontrada
        """
        attendance_operations_use_case.delete_attendance(attendance_id)
        return "", HTTPStatus.NO_CONTENT

    return blueprint


def _validation_error_response(message: str):
    return (
        jsonify(
            {
                "error": "validation_error",
                "message": message,
            }
        ),
        HTTPStatus.BAD_REQUEST,
    )


def _validate_payload(payload: dict, include_date: bool, require_email: bool = False):
    required_fields = ["student_id", "course_id", "class_session_id"]
    if include_date:
        required_fields.append("attendance_date")

    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return _validation_error_response(
            f"Campos requeridos faltantes: {', '.join(missing)}"
        )
    return None


def _parse_attendance_date(payload: dict, required: bool):
    raw_date = payload.get("attendance_date")
    if raw_date is None and not required:
        return date.today(), None

    try:
        return date.fromisoformat(raw_date), None
    except (TypeError, ValueError):
        return None, _validation_error_response(
            "attendance_date debe tener formato YYYY-MM-DD."
        )


def _attendance_to_dict(attendance: Attendance) -> dict:
    return {
        "id": attendance.id,
        "student_id": attendance.student_id,
        "course_id": attendance.course_id,
        "class_session_id": attendance.class_session_id,
        "attendance_date": attendance.attendance_date.isoformat(),
        "registered_at": attendance.registered_at.isoformat() + "Z",
    }
