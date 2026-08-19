from flask import Flask,render_template,request,redirect,url_for,session,send_from_directory,flash,jsonify
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime,date,timedelta
from sqlalchemy import or_
import os

app=Flask(__name__)
app.config['SECRET_KEY']='healthforge-merged-secret-key-change-me'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthforge.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["UPLOAD_FOLDER"] = "uploads/medical_records"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
# ============================================================
# Doctor portal (merged from HealthForge AI doctor project)
# ============================================================

DOCTOR = {
    "email": "doctor@healthforge.ai",
    "password": "doctor123",
    "name": "Dr. Rahul Verma",
    "specialization": "Cardiologist",
    "qualification": "MBBS, MD (Cardiology)",
    "experience": "10+ Years",
    "phone": "9876543210",
    "photo_initials": "RV",
}

RECEPTIONIST = {
    "email": "receptionist@healthforge.ai",
    "password": "reception123",
    "name": "HealthForge Reception",
}
ALLOWED_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg"
}

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )
db = SQLAlchemy(app)

def create_notification(
    patient_id,
    title,
    message,
    notification_type="general"
):

    notification = Notification(

        patient_id=patient_id,

        title=title,

        message=message,

        notification_type=notification_type

    )

    db.session.add(notification)


@app.route('/')
def index():
    return render_template('index.html')

class Patient(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)
    email=db.Column(db.String(50),nullable=False,unique=True)
    password_hash=db.Column(db.String(50),nullable=False)
    phone=db.Column(db.String(15),nullable=False,unique=True)
    date_of_birth=db.Column(db.Date,nullable=False)
    address=db.Column(db.String(100),nullable=True)

class Hospital(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    location = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    rating = db.Column(
        db.Float
    )

    review_count = db.Column(
        db.Integer,
        default=0
    )

    image = db.Column(
        db.String(255)
    )

    beds = db.relationship(
        "Bed",
        backref="hospital",
        lazy=True
    )
    doctors = db.relationship(
    "Doctor",
    backref="hospital",
    lazy=True
    )

class Bed(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    hospital_id = db.Column(
        db.Integer,
        db.ForeignKey("hospital.id"),
        nullable=False
    )

    bed_type = db.Column(
        db.String(50),
        nullable=False
    )

    total_beds = db.Column(
        db.Integer,
        nullable=False
    )

    available_beds = db.Column(
        db.Integer,
        nullable=False
    )
class Doctor(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    hospital_id = db.Column(
        db.Integer,
        db.ForeignKey("hospital.id"),
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    specialization = db.Column(
        db.String(100),
        nullable=False
    )

    experience = db.Column(
        db.Integer,
        nullable=False
    )

    qualification = db.Column(
        db.String(200)
    )

    consultation_fee = db.Column(
        db.Integer
    )

    available_days = db.Column(
        db.String(100)
    )

    timings = db.Column(
        db.String(100)
    )

    rating = db.Column(
        db.Float,
        default=0
    )

    review_count = db.Column(
        db.Integer,
        default=0
    )

class Appointment(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id"),
        nullable=False
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctor.id"),
        nullable=False
    )

    hospital_id = db.Column(
        db.Integer,
        db.ForeignKey("hospital.id"),
        nullable=False
    )

    appointment_date = db.Column(
        db.Date,
        nullable=False
    )

    appointment_time = db.Column(
        db.String(20),
        nullable=False
    )

    consultation_type = db.Column(
        db.String(50),
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="Confirmed",
        nullable=False
    )


    patient = db.relationship(
        "Patient",
        backref="appointments"
    )

    doctor = db.relationship(
        "Doctor",
        backref="appointments"
    )

    hospital = db.relationship(
        "Hospital",
        backref="appointments"
    )

class MedicalRecord(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id"),
        nullable=False
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    filepath = db.Column(
        db.String(500),
        nullable=False
    )

    file_type = db.Column(
        db.String(50),
        nullable=False
    )

    file_size = db.Column(
        db.Integer,
        nullable=False
    )

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    patient = db.relationship(
        "Patient",
        backref="medical_records"
    )

class Notification(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id"),
        nullable=False
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    notification_type = db.Column(
        db.String(50),
        nullable=False,
        default="general"
    )

    is_read = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    patient = db.relationship(
        "Patient",
        backref="notifications"
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        phone = request.form['phone'].strip()
        date_of_birth = datetime.strptime(
            request.form["date_of_birth"], "%Y-%m-%d"
        ).date()
        address = request.form.get('address', '').strip()

        existing_patient = Patient.query.filter_by(email=email).first()
        if existing_patient:
            return "Email already registered", 409

        if Patient.query.filter_by(phone=phone).first():
            return "Phone number already registered", 409

        new_patient = Patient(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone,
            date_of_birth=date_of_birth,
            address=address
        )
        db.session.add(new_patient)
        db.session.commit()

        flash("Patient account created. Please log in.", "success")
        return redirect(url_for('role_login', role='patient'))

    return render_template('register.html')


@app.route("/login", methods=["GET"])
def login():
    return render_template("role_selector.html")


@app.route("/login/<role>", methods=["GET", "POST"])
def role_login(role):
    if role not in {"patient", "doctor", "receptionist"}:
        return "Invalid role", 404

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if role == "patient":
            patient = Patient.query.filter_by(email=email).first()
            if patient and check_password_hash(patient.password_hash, password):
                session.clear()
                session["role"] = "patient"
                session["patient_id"] = patient.id
                return redirect(url_for("dashboard"))
            flash("Invalid patient email or password.", "error")

        elif role == "doctor":
            if email == DOCTOR["email"] and password == DOCTOR["password"]:
                session.clear()
                session["role"] = "doctor"
                session["doctor_email"] = email
                flash("Welcome back, Dr. Rahul Verma!", "success")
                return redirect(url_for("doctor_dashboard"))
            flash("Invalid doctor credentials.", "error")

        else:
            if email == RECEPTIONIST["email"] and password == RECEPTIONIST["password"]:
                session.clear()
                session["role"] = "receptionist"
                session["receptionist_email"] = email
                flash("Welcome to the receptionist portal.", "success")
                return redirect(url_for("receptionist_dashboard"))
            flash("Invalid receptionist credentials.", "error")

    return render_template("role_login.html", role=role)


@app.route("/dashboard")
def dashboard():
    if session.get("role") != "patient" or "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))

    today = date.today()

    next_appointment = Appointment.query.filter(
        Appointment.patient_id == session["patient_id"],
        Appointment.appointment_date >= today,
        Appointment.status == "Confirmed"
    ).order_by(
        Appointment.appointment_date.asc()
    ).first()

    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == session["patient_id"],
        Appointment.appointment_date >= today,
        Appointment.status == "Confirmed"
    ).count()

    patient = db.session.get(Patient, session["patient_id"])

    if patient is None:
        session.clear()
        return redirect(url_for("role_login", role="patient"))

    return render_template(
        "dashboard.html",
        patient=patient,
        next_appointment=next_appointment,
        upcoming_appointments=upcoming_appointments,
        upcoming_count=upcoming_appointments
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/hospitals")
def hospitals():

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))

    hospitals = Hospital.query.all()

    return render_template(
        "hospitals.html",
        hospitals=hospitals
    )

@app.route("/hospital/<int:hospital_id>")
def hospital_details(hospital_id):

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))

    hospital = db.session.get(
        Hospital,
        hospital_id
    )

    if hospital is None:
        return "Hospital not found", 404

    return render_template(
        "hospital_details.html",
        hospital=hospital
    )

@app.route("/hospital/<int:hospital_id>/beds")
def bed_availability(hospital_id):

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))

    hospital = db.session.get(
        Hospital,
        hospital_id
    )

    if hospital is None:
        return "Hospital not found", 404

    return render_template(
        "beds.html",
        hospital=hospital
    )

@app.route("/hospital/<int:hospital_id>/doctors")
def doctor_list(hospital_id):

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))

    hospital = db.session.get(
        Hospital,
        hospital_id
    )

    if hospital is None:
        return "Hospital not found", 404

    doctors = Doctor.query.filter_by(
        hospital_id=hospital_id
    ).all()

    return render_template(
        "doctors.html",
        hospital=hospital,
        doctors=doctors
    )

@app.route("/doctor/<int:doctor_id>")
def doctor_profile(doctor_id):

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))

    doctor = db.session.get(
        Doctor,
        doctor_id
    )

    if doctor is None:
        return "Doctor not found", 404

    return render_template(
        "doctor_profile.html",
        doctor=doctor
    )

def doctor_available_on_date(doctor, appointment_date):

    day = appointment_date.strftime("%a")

    days = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun"
    ]

    available_days = doctor.available_days

    if "Mon - Sat" in available_days:
        return day in [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat"
        ]

    if "Mon - Fri" in available_days:
        return day in [
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri"
        ]

    if "Mon - Sun" in available_days:
        return True

    return day in available_days

def generate_time_slots(timings):

    start_string, end_string = timings.split(" - ")

    start_time = datetime.strptime(
        start_string,
        "%I:%M %p"
    )

    end_time = datetime.strptime(
        end_string,
        "%I:%M %p"
    )


    slots = []

    current_time = start_time


    while current_time < end_time:

        slots.append(
            current_time.strftime("%I:%M %p")
        )

        current_time += timedelta(minutes=30)


    return slots

@app.route(
    "/doctor/<int:doctor_id>/book",
    methods=["GET", "POST"]
)
def book_appointment(doctor_id):

    # Patient must be logged in
    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))

    # Find doctor
    doctor = db.session.get(
        Doctor,
        doctor_id
    )

    if doctor is None:
        return "Doctor not found", 404


    # Generate temporary time slots
    time_slots = generate_time_slots(
        doctor.timings
    )


    # =================================
    # POST - Patient submits booking
    # =================================

    if request.method == "POST":

        # -----------------------------
        # Get form data
        # -----------------------------

        appointment_date = datetime.strptime(
            request.form["appointment_date"],
            "%Y-%m-%d"
        ).date()

        appointment_time = request.form[
            "appointment_time"
        ]

        consultation_type = request.form[
            "consultation_type"
        ]


        # -----------------------------
        # Check past date
        # -----------------------------

        if appointment_date < date.today():

            return render_template(
                "book_appointment.html",
                doctor=doctor,
                time_slots=time_slots,
                today=date.today().isoformat(),
                error="You cannot book an appointment for a past date."
            )


        # -----------------------------
        # Check doctor's available day
        # -----------------------------

        if not doctor_available_on_date(
            doctor,
            appointment_date
        ):

            return render_template(
                "book_appointment.html",
                doctor=doctor,
                time_slots=time_slots,
                today=date.today().isoformat(),
                error="Doctor is not available on this day."
            )


        # -----------------------------
        # Check whether slot is valid
        # -----------------------------

        if appointment_time not in time_slots:

            return render_template(
                "book_appointment.html",
                doctor=doctor,
                time_slots=time_slots,
                today=date.today().isoformat(),
                error="Invalid appointment time."
            )


        # -----------------------------
        # Check duplicate booking
        # -----------------------------

        existing_appointment = Appointment.query.filter_by(

            doctor_id=doctor.id,

            appointment_date=appointment_date,

            appointment_time=appointment_time,

            status="Confirmed"

        ).first()


        if existing_appointment:

            return render_template(
                "book_appointment.html",
                doctor=doctor,
                time_slots=time_slots,
                today=date.today().isoformat(),
                error="This time slot is already booked."
            )


        # -----------------------------
        # Create appointment
        # -----------------------------

        appointment = Appointment(

            patient_id=session["patient_id"],

            doctor_id=doctor.id,

            hospital_id=doctor.hospital_id,

            appointment_date=appointment_date,

            appointment_time=appointment_time,

            consultation_type=consultation_type,

            status="Confirmed"
        )


        db.session.add(appointment)
        create_notification(

            patient_id=session["patient_id"],

            title="Appointment Confirmed",

            message=(
                f"Your appointment with "
                f"{doctor.name} has been confirmed "
                f"for {appointment_date.strftime('%d %b %Y')} "
                f"at {appointment_time}."
            ),

            notification_type="appointment"

        )

        db.session.commit()


        # -----------------------------
        # Go to My Appointments
        # -----------------------------

        return redirect(
            url_for("my_appointments")
        )


    # =================================
    # GET - Show booking page
    # =================================

    return render_template(

        "book_appointment.html",

        doctor=doctor,

        time_slots=time_slots,

        today=date.today().isoformat()

    )

@app.route("/appointments")
def my_appointments():

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))


    today = date.today()


    upcoming = Appointment.query.filter(

        Appointment.patient_id == session["patient_id"],

        Appointment.appointment_date >= today,

        Appointment.status != "Cancelled"

    ).order_by(
        Appointment.appointment_date.asc()
    ).all()


    past = Appointment.query.filter(

        Appointment.patient_id == session["patient_id"],

        Appointment.appointment_date < today

    ).order_by(
        Appointment.appointment_date.desc()
    ).all()


    return render_template(
        "appointments.html",
        upcoming=upcoming,
        past=past
    )

@app.route(
    "/appointment/<int:appointment_id>/cancel",
    methods=["POST"]
)
def cancel_appointment(appointment_id):

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))


    appointment = db.session.get(
        Appointment,
        appointment_id
    )


    if appointment is None:
        return "Appointment not found", 404


    # Make sure this appointment belongs
    # to the logged-in patient

    if appointment.patient_id != session["patient_id"]:

        return "Unauthorized", 403


    # Don't allow cancellation of
    # already cancelled appointment

    if appointment.status == "Cancelled":

        return redirect(
            url_for("my_appointments")
        )


    appointment.status = "Cancelled"


    db.session.commit()


    return redirect(
        url_for("my_appointments")
    )

@app.route("/my-doctors")
def my_doctors():

    # Patient must be logged in
    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))

    patient_id = session["patient_id"]


    # ==========================================
    # Find doctors previously booked by patient
    # ==========================================

    doctor_ids = db.session.query(
        Appointment.doctor_id
    ).filter(
        Appointment.patient_id == patient_id
    ).distinct().all()


    # Convert tuples into a simple list of IDs

    doctor_ids = [
        row[0]
        for row in doctor_ids
    ]


    # ==========================================
    # Get search text
    # ==========================================

    search = request.args.get(
        "q",
        ""
    ).strip()


    # ==========================================
    # Find doctors
    # ==========================================

    if doctor_ids:

        query = Doctor.query.filter(
            Doctor.id.in_(doctor_ids)
        )


        # Search by name OR specialization

        if search:

            query = query.filter(
                or_(
                    Doctor.name.ilike(
                        f"%{search}%"
                    ),

                    Doctor.specialization.ilike(
                        f"%{search}%"
                    )
                )
            )


        # Sort alphabetically

        doctors = query.order_by(
            Doctor.name.asc()
        ).all()


    else:

        # Patient has never booked a doctor

        doctors = []


    # ==========================================
    # Send data to template
    # ==========================================

    return render_template(
        "my_doctors.html",
        doctors=doctors,
        search=search
    )

@app.route("/my-doctor/<int:doctor_id>")
def doctor_details(doctor_id):

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))


    # Check that this patient has
    # previously booked this doctor

    previous_appointment = Appointment.query.filter_by(

        patient_id=session["patient_id"],

        doctor_id=doctor_id

    ).first()


    if previous_appointment is None:

        return "Doctor not found in your doctors list.", 404


    doctor = db.session.get(
        Doctor,
        doctor_id
    )


    if doctor is None:
        return "Doctor not found.", 404

    doctor=db.session.get(Doctor,doctor_id)
    if doctor is None:
        return "Doctor not found", 404


    return render_template(
        "doctor_details.html",
        doctor=doctor
    )

@app.route("/medical-records")
def medical_records():

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))

    records = MedicalRecord.query.filter_by(
        patient_id=session["patient_id"]
    ).order_by(
        MedicalRecord.uploaded_at.desc()
    ).all()

    return render_template(
        "medical_records.html",
        records=records
    )

@app.route(
    "/medical-records/upload",
    methods=["GET", "POST"]
)
def upload_medical_record():

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))


    if request.method == "POST":

        file = request.files.get("file")


        # No file selected

        if file is None or file.filename == "":

            return render_template(
                "upload_record.html",
                error="Please select a file."
            )


        # Check extension

        if not allowed_file(file.filename):

            return render_template(
                "upload_record.html",
                error="File type is not allowed."
            )


        # Secure filename

        filename = secure_filename(
            file.filename
        )


        patient_id = session["patient_id"]


        # Create patient's folder

        patient_folder = os.path.join(
            app.config["UPLOAD_FOLDER"],
            str(patient_id)
        )


        os.makedirs(
            patient_folder,
            exist_ok=True
        )


        # Prevent filename conflicts

        timestamp = datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )

        filename = (
            f"{timestamp}_{filename}"
        )


        filepath = os.path.join(
            patient_folder,
            filename
        )


        # Save actual file

        file.save(filepath)


        # Get file information

        file_size = os.path.getsize(
            filepath
        )

        file_type = (
            filename.rsplit(".", 1)[1]
            .lower()
        )


        # Save information in database

        record = MedicalRecord(

            patient_id=patient_id,

            filename=filename,

            filepath=filepath,

            file_type=file_type,

            file_size=file_size

        )


        db.session.add(record)

        db.session.commit()


        return redirect(
            url_for("medical_records")
        )


    return render_template(
        "upload_record.html"
    )

@app.route("/medical-records/<int:record_id>/download")
def download_medical_record(record_id):

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))

    record = db.session.get(
        MedicalRecord,
        record_id
    )

    if record is None:
        return "Medical record not found", 404

    # --------------------------------
    # Security check
    # --------------------------------

    if record.patient_id != session["patient_id"]:
        return "Unauthorized", 403

    # --------------------------------
    # Get folder and filename
    # --------------------------------

    directory = os.path.dirname(
        record.filepath
    )

    filename = os.path.basename(
        record.filepath
    )

    return send_from_directory(
        directory,
        filename,
        as_attachment=True
    )

@app.route(
    "/medical-records/<int:record_id>/delete",
    methods=["POST"]
)
def delete_medical_record(record_id):

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))

    record = db.session.get(
        MedicalRecord,
        record_id
    )

    if record is None:
        return "Medical record not found", 404

    # --------------------------------
    # Security check
    # --------------------------------

    if record.patient_id != session["patient_id"]:
        return "Unauthorized", 403

    # --------------------------------
    # Delete physical file
    # --------------------------------

    if os.path.exists(record.filepath):

        os.remove(
            record.filepath
        )

    # --------------------------------
    # Delete database record
    # --------------------------------

    db.session.delete(record)

    db.session.commit()

    return redirect(
        url_for("medical_records")
    )

@app.route("/medical-records/<int:record_id>/analyze")
def analyze_medical_record(record_id):

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))

    record = db.session.get(
        MedicalRecord,
        record_id
    )

    if record is None:
        return "Medical record not found", 404

    # Security check
    if record.patient_id != session["patient_id"]:
        return "Unauthorized", 403

    return render_template(
        "medical_report_summary.html",
        record=record
    )

@app.route("/profile")
def profile():

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))

    patient = db.session.get(
        Patient,
        session["patient_id"]
    )

    if patient is None:
        return redirect(url_for("role_login", role="patient"))

    return render_template(
        "profile.html",
        patient=patient
    )

@app.route(
    "/profile/edit",
    methods=["GET", "POST"]
)
def edit_profile():

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))


    patient = db.session.get(
        Patient,
        session["patient_id"]
    )


    if patient is None:
        return redirect(url_for("role_login", role="patient"))


    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        date_of_birth = request.form.get(
            "date_of_birth",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()


        # -----------------------------
        # Basic validation
        # -----------------------------

        if not name:

            return render_template(
                "edit_profile.html",
                patient=patient,
                error="Name is required."
            )


        if not phone:

            return render_template(
                "edit_profile.html",
                patient=patient,
                error="Phone number is required."
            )


        # -----------------------------
        # Date conversion
        # -----------------------------

        if date_of_birth:

            try:

                patient.date_of_birth = datetime.strptime(
                    date_of_birth,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                return render_template(
                    "edit_profile.html",
                    patient=patient,
                    error="Invalid date of birth."
                )


        # -----------------------------
        # Update patient
        # -----------------------------

        patient.name = name

        patient.phone = phone

        patient.address = address


        db.session.commit()


        return redirect(
            url_for("profile")
        )


    return render_template(
        "edit_profile.html",
        patient=patient
    )

@app.route("/notifications")
def notifications():

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))

    patient_id = session["patient_id"]

    notifications = Notification.query.filter_by(
        patient_id=patient_id
    ).order_by(
        Notification.created_at.desc()
    ).all()

    unread_count = Notification.query.filter_by(
        patient_id=patient_id,
        is_read=False
    ).count()

    return render_template(
        "notifications.html",
        notifications=notifications,
        unread_count=unread_count
    )

@app.route(
    "/notifications/<int:notification_id>/read",
    methods=["POST"]
)
def mark_notification_read(notification_id):

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))

    notification = db.session.get(
        Notification,
        notification_id
    )

    if notification is None:
        return "Notification not found", 404

    # Security check
    if notification.patient_id != session["patient_id"]:
        return "Unauthorized", 403

    notification.is_read = True

    db.session.commit()

    return redirect(
        url_for("notifications")
    )

@app.context_processor
def inject_notification_count():

    unread_notification_count = 0

    if "patient_id" in session:

        unread_notification_count = Notification.query.filter_by(
            patient_id=session["patient_id"],
            is_read=False
        ).count()

    return {
        "unread_notification_count": unread_notification_count
    }

@app.route(
    "/notifications/read-all",
    methods=["POST"]
)
def mark_all_notifications_read():

    if "patient_id" not in session:
        return redirect(url_for("role_login", role="patient"))

    Notification.query.filter_by(
        patient_id=session["patient_id"],
        is_read=False
    ).update(
        {"is_read": True}
    )

    db.session.commit()

    return redirect(
        url_for("notifications")
    )



with app.app_context():
    db.create_all()
    
doctor_appointments = [
    {"id": 1, "time": "09:00 AM", "patient": "Ramesh Sharma", "age": 45, "gender": "Male",
     "type": "Follow-up", "token": "TK0125", "status": "Checked in"},
    {"id": 2, "time": "10:00 AM", "patient": "Neha Singh", "age": 32, "gender": "Female",
     "type": "Consultation", "token": "TK0126", "status": "Waiting"},
    {"id": 3, "time": "11:30 AM", "patient": "Amit Kumar", "age": 28, "gender": "Male",
     "type": "Consultation", "token": "TK0127", "status": "Waiting"},
    {"id": 4, "time": "02:00 PM", "patient": "Priya Patel", "age": 38, "gender": "Female",
     "type": "Follow-up", "token": "TK0128", "status": "Scheduled"},
    {"id": 5, "time": "03:30 PM", "patient": "Suresh Yadav", "age": 50, "gender": "Male",
     "type": "Consultation", "token": "TK0129", "status": "Scheduled"},
]

doctor_patients = [
    {"id": 1, "name": "Ramesh Sharma", "mrn": "HF2500125", "age": 45, "gender": "Male", "last_visit": "10 May 2025"},
    {"id": 2, "name": "Neha Singh", "mrn": "HF2500126", "age": 32, "gender": "Female", "last_visit": "15 May 2025"},
    {"id": 3, "name": "Amit Kumar", "mrn": "HF2500127", "age": 28, "gender": "Male", "last_visit": "15 May 2025"},
    {"id": 4, "name": "Priya Patel", "mrn": "HF2500128", "age": 38, "gender": "Female", "last_visit": "12 May 2025"},
    {"id": 5, "name": "Suresh Yadav", "mrn": "HF2500129", "age": 50, "gender": "Male", "last_visit": "11 May 2025"},
    {"id": 6, "name": "Vikram Joshi", "mrn": "HF2500130", "age": 41, "gender": "Male", "last_visit": "09 May 2025"},
]

doctor_schedule = {
    "15 May 2025": [
        {"time": "09:00 AM - 01:00 PM", "enabled": True},
        {"time": "02:00 PM - 05:00 PM", "enabled": True},
        {"time": "05:00 PM - 08:00 PM", "enabled": False},
    ]
}

doctor_notifications = [
    {"id": 1, "title": "New appointment booked", "message": "Neha Singh has booked a consultation for today at 10:00 AM.", "time": "10 minutes ago", "type": "appointment", "read": False},
    {"id": 2, "title": "Appointment reminder", "message": "You have 5 appointments scheduled for today.", "time": "30 minutes ago", "type": "reminder", "read": False},
    {"id": 3, "title": "Profile update", "message": "Your profile information was last updated successfully.", "time": "Yesterday", "type": "system", "read": True},
]


def doctor_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("role") != "doctor":
            return redirect(url_for("role_login", role="doctor"))
        return view(*args, **kwargs)
    return wrapped_view


@app.context_processor
def merged_globals():
    unread = sum(1 for n in doctor_notifications if not n["read"])
    return {
        "doctor": DOCTOR,
        "unread_notifications": unread,
        "today": date.today().strftime("%d %b %Y"),
    }


@app.route("/doctor/dashboard")
@doctor_required
def doctor_dashboard():
    checked_in = sum(1 for a in doctor_appointments if a["status"] == "Checked in")
    pending = sum(1 for a in doctor_appointments if a["status"] in ("Waiting", "Scheduled"))
    return render_template(
        "doctor/dashboard.html",
        appointments=doctor_appointments[:5],
        stats={
            "today": len(doctor_appointments),
            "seen": checked_in,
            "new_patients": len(doctor_patients),
            "pending": pending,
        },
    )


@app.route("/doctor/appointments")
@doctor_required
def doctor_appointment_list():
    status = request.args.get("status", "All")
    filtered = doctor_appointments if status == "All" else [
        a for a in doctor_appointments if a["status"] == status
    ]
    return render_template(
        "doctor/appointments.html",
        appointments=filtered,
        current_status=status
    )


@app.route("/doctor/appointments/<int:appointment_id>/status", methods=["POST"])
@doctor_required
def doctor_update_appointment_status(appointment_id):
    new_status = request.form.get("status", "")
    allowed = {"Scheduled", "Waiting", "Checked in", "Completed", "Cancelled"}

    for appointment in doctor_appointments:
        if appointment["id"] == appointment_id:
            if new_status in allowed:
                appointment["status"] = new_status
                flash(
                    f"{appointment['patient']}'s appointment is now {new_status}.",
                    "success"
                )
            break

    return redirect(request.referrer or url_for("doctor_appointment_list"))


@app.route("/doctor/patients")
@doctor_required
def doctor_patient_list():
    query_text = request.args.get("q", "").strip()
    query = query_text.lower()
    gender = request.args.get("gender", "All")

    filtered = doctor_patients
    if query:
        filtered = [
            p for p in filtered
            if query in p["name"].lower() or query in p["mrn"].lower()
        ]
    if gender != "All":
        filtered = [p for p in filtered if p["gender"] == gender]

    page_size = 5
    total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
    try:
        page = max(1, int(request.args.get("page", 1)))
    except ValueError:
        page = 1
    page = min(page, total_pages)

    start = (page - 1) * page_size

    return render_template(
        "doctor/patients.html",
        patients=filtered[start:start + page_size],
        query=query_text,
        gender=gender,
        page=page,
        total_pages=total_pages,
    )


@app.route("/doctor/schedule", methods=["GET", "POST"])
@doctor_required
def doctor_schedule_page():
    selected_date = request.values.get("date", "15 May 2025")

    if selected_date not in doctor_schedule:
        doctor_schedule[selected_date] = []

    if request.method == "POST":
        action = request.form.get("action")

        if action == "toggle":
            index = int(request.form.get("index", -1))
            if 0 <= index < len(doctor_schedule[selected_date]):
                doctor_schedule[selected_date][index]["enabled"] = not doctor_schedule[selected_date][index]["enabled"]
                flash("Schedule availability updated.", "success")

        elif action == "add":
            start = request.form.get("start", "").strip()
            end = request.form.get("end", "").strip()
            if start and end:
                doctor_schedule[selected_date].append({
                    "time": f"{start} - {end}",
                    "enabled": True
                })
                flash("New time slot added.", "success")
            else:
                flash("Please enter both start and end times.", "error")

        elif action == "save":
            flash("Schedule saved successfully.", "success")

        return redirect(url_for("doctor_schedule_page", date=selected_date))

    return render_template(
        "doctor/schedule.html",
        selected_date=selected_date,
        slots=doctor_schedule[selected_date],
    )


@app.route("/doctor/notifications")
@doctor_required
def doctor_notification_page():
    return render_template(
        "doctor/notifications.html",
        notifications=doctor_notifications
    )


@app.route("/doctor/notifications/<int:notification_id>/read", methods=["POST"])
@doctor_required
def doctor_mark_notification_read(notification_id):
    for notification in doctor_notifications:
        if notification["id"] == notification_id:
            notification["read"] = True
            break
    return redirect(url_for("doctor_notification_page"))


@app.route("/doctor/notifications/read-all", methods=["POST"])
@doctor_required
def doctor_mark_all_notifications_read():
    for notification in doctor_notifications:
        notification["read"] = True
    flash("All notifications marked as read.", "success")
    return redirect(url_for("doctor_notification_page"))


@app.route("/doctor/profile", methods=["GET", "POST"])
@doctor_required
def doctor_portal_profile():
    if request.method == "POST":
        for field in ["name", "email", "phone", "specialization", "qualification", "experience"]:
            value = request.form.get(field, "").strip()
            if value:
                DOCTOR[field] = value

        flash("Profile updated successfully.", "success")
        return redirect(url_for("doctor_portal_profile"))

    return render_template("doctor/profile.html")


@app.route("/doctor/logout")
def doctor_logout():
    session.clear()
    return redirect(url_for("index"))


# ============================================================
# Receptionist portal
# ============================================================

receptionist_appointments = [
    {"id": 1, "time": "09:00 AM", "patient": "Ramesh Sharma", "doctor": "Dr. Rahul Verma", "status": "Checked in"},
    {"id": 2, "time": "10:00 AM", "patient": "Neha Singh", "doctor": "Dr. Rahul Verma", "status": "Waiting"},
    {"id": 3, "time": "11:30 AM", "patient": "Amit Kumar", "doctor": "Dr. Amit Kumar", "status": "Scheduled"},
    {"id": 4, "time": "02:00 PM", "patient": "Priya Patel", "doctor": "Dr. Neha Singh", "status": "Scheduled"},
]


def receptionist_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get("role") != "receptionist":
            return redirect(url_for("role_login", role="receptionist"))
        return view(*args, **kwargs)
    return wrapped_view


@app.route("/receptionist/dashboard")
@receptionist_required
def receptionist_dashboard():
    return render_template(
        "receptionist/dashboard.html",
        appointments=receptionist_appointments,
        patient_count=Patient.query.count(),
        doctor_count=Doctor.query.count(),
        hospital_count=Hospital.query.count(),
    )


@app.route("/receptionist/patients")
@receptionist_required
def receptionist_patients():
    patients = Patient.query.order_by(Patient.name.asc()).all()
    return render_template(
        "receptionist/patients.html",
        patients=patients
    )


@app.route("/receptionist/appointments")
@receptionist_required
def receptionist_appointments_page():
    return render_template(
        "receptionist/appointments.html",
        appointments=receptionist_appointments
    )


@app.route("/receptionist/logout")
def receptionist_logout():
    session.clear()
    return redirect(url_for("index"))


# ============================================================
# Simple API for the three portals
# ============================================================

@app.route("/api/receptionist/stats")
@receptionist_required
def receptionist_stats():
    return jsonify({
        "patients": Patient.query.count(),
        "doctors": Doctor.query.count(),
        "hospitals": Hospital.query.count(),
        "appointments": len(receptionist_appointments),
    })


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
