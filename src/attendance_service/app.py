import os
from http import HTTPStatus

from flask import Flask, jsonify
from flasgger import Swagger

from .application.usecases import AttendanceOperationsUseCase
from .domain.exception import AttendanceNotFoundError, DuplicateAttendanceError
from .domain.service import AbsenceEventService
from .infrastructure.adapters.inbound import create_attendance_blueprint
from .infrastructure.adapters.outbound import (
    RabbitMQEventPublisher,
    SqlAlchemyAttendanceRepository,
)
from .infrastructure.config import build_session_factory


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    app.config["SWAGGER"] = {
        "title": "EduAttend API",
        "uiversion": 3,
        "openapi": "3.0.2",
    }
    Swagger(app)

    database_url = os.getenv(
        "ATTENDANCE_DATABASE_URL",
        "postgresql+psycopg2://attendance_user:attendance_password@postgres_attendance:5432/attendance_db",
    )
    session_factory = build_session_factory(database_url)

    repository = SqlAlchemyAttendanceRepository(session_factory)
    event_publisher = RabbitMQEventPublisher(os.getenv("RABBITMQ_URL"))
    absence_event_service = AbsenceEventService(event_publisher)
    attendance_operations_use_case = AttendanceOperationsUseCase(repository)
    app.extensions["absence_event_service"] = absence_event_service

    app.register_blueprint(
        create_attendance_blueprint(
            attendance_operations_use_case=attendance_operations_use_case,
        )
    )

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"}), HTTPStatus.OK

    @app.errorhandler(DuplicateAttendanceError)
    def handle_duplicate_attendance(error: DuplicateAttendanceError):
        return (
            jsonify(
                {
                    "error": "business_rule_violation",
                    "message": str(error),
                }
            ),
            HTTPStatus.CONFLICT,
        )

    @app.errorhandler(AttendanceNotFoundError)
    def handle_attendance_not_found(error: AttendanceNotFoundError):
        return (
            jsonify(
                {
                    "error": "not_found",
                    "message": str(error),
                }
            ),
            HTTPStatus.NOT_FOUND,
        )

    return app
