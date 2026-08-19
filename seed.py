from app import app, db, Hospital, Bed, Doctor


with app.app_context():

    # =====================================
    # Get hospitals
    # =====================================

    city_care = Hospital.query.filter_by(
        name="City Care Hospital"
    ).first()

    medilife = Hospital.query.filter_by(
        name="MediLife Hospital"
    ).first()

    sunrise = Hospital.query.filter_by(
        name="Sunrise Hospital"
    ).first()


    # =====================================
    # Delete old demo data
    # =====================================

    Doctor.query.delete()
    Bed.query.delete()

    db.session.commit()


    # =====================================
    # Create beds
    # =====================================

    beds = [

        Bed(
            hospital_id=city_care.id,
            bed_type="General Beds",
            total_beds=100,
            available_beds=25
        ),

        Bed(
            hospital_id=city_care.id,
            bed_type="ICU Beds",
            total_beds=20,
            available_beds=5
        ),

        Bed(
            hospital_id=city_care.id,
            bed_type="Private Rooms",
            total_beds=15,
            available_beds=8
        ),

        Bed(
            hospital_id=city_care.id,
            bed_type="Ventilator",
            total_beds=10,
            available_beds=2
        ),

        Bed(
            hospital_id=medilife.id,
            bed_type="General Beds",
            total_beds=80,
            available_beds=12
        ),

        Bed(
            hospital_id=medilife.id,
            bed_type="ICU Beds",
            total_beds=15,
            available_beds=4
        ),

        Bed(
            hospital_id=sunrise.id,
            bed_type="General Beds",
            total_beds=70,
            available_beds=18
        ),

        Bed(
            hospital_id=sunrise.id,
            bed_type="ICU Beds",
            total_beds=12,
            available_beds=3
        )
    ]


    # =====================================
    # Create doctors
    # =====================================

    doctors = [

        Doctor(
            hospital_id=city_care.id,
            name="Dr. Rahul Verma",
            specialization="Cardiologist",
            experience=10,
            qualification="MBBS, MD (Medicine), DM (Cardiology)",
            consultation_fee=800,
            available_days="Mon - Sat",
            timings="10:00 AM - 05:00 PM",
            rating=4.7,
            review_count=820
        ),

        Doctor(
            hospital_id=city_care.id,
            name="Dr. Neha Singh",
            specialization="Neurologist",
            experience=8,
            qualification="MBBS, MD, DM (Neurology)",
            consultation_fee=700,
            available_days="Mon - Fri",
            timings="09:00 AM - 03:00 PM",
            rating=4.6,
            review_count=650
        ),

        Doctor(
            hospital_id=city_care.id,
            name="Dr. Amit Kumar",
            specialization="Orthopedic",
            experience=12,
            qualification="MBBS, MS (Orthopedics)",
            consultation_fee=600,
            available_days="Mon - Sat",
            timings="11:00 AM - 04:00 PM",
            rating=4.5,
            review_count=720
        ),

        Doctor(
            hospital_id=city_care.id,
            name="Dr. Priya Sharma",
            specialization="Gynecologist",
            experience=9,
            qualification="MBBS, MD (Gynecology)",
            consultation_fee=700,
            available_days="Mon - Fri",
            timings="10:00 AM - 02:00 PM",
            rating=4.8,
            review_count=590
        ),

        Doctor(
            hospital_id=medilife.id,
            name="Dr. Arjun Mehta",
            specialization="Cardiologist",
            experience=11,
            qualification="MBBS, MD, DM",
            consultation_fee=900,
            available_days="Mon - Sat",
            timings="10:00 AM - 04:00 PM",
            rating=4.6,
            review_count=710
        ),

        Doctor(
            hospital_id=sunrise.id,
            name="Dr. Rohan Gupta",
            specialization="Orthopedic",
            experience=7,
            qualification="MBBS, MS",
            consultation_fee=600,
            available_days="Mon - Fri",
            timings="09:00 AM - 02:00 PM",
            rating=4.4,
            review_count=430
        )
    ]


    # =====================================
    # Add new data
    # =====================================

    db.session.add_all(beds)
    db.session.add_all(doctors)

    db.session.commit()


    # =====================================
    # Verify
    # =====================================

    print("Bed data added successfully!")
    print("Doctor data added successfully!")

    print("Total beds:", Bed.query.count())
    print("Total doctors:", Doctor.query.count())