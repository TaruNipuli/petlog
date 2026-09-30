import os
import db

db.DB_PATH = "test.db"
db.init_db()

pet_id = db.add_pet("user1", "Rex", "dog", breed="Labrador")

values = {"mood": 4, "appetite": 5, "sleep_hours": 8, "exercise_minutes": 60,
          "notes": "Good day", "walk_distance_km": 3.5}
db.save_entry(pet_id, "user1", "2026-09-29", values)

# Saving again for the same day should update, not duplicate
values["mood"] = 5
db.save_entry(pet_id, "user1", "2026-09-29", values)

print("user1 pets:   ", db.get_pets("user1"))
print("user1 entries:", db.get_entries(pet_id, "user1"))
print("user2 pets:   ", db.get_pets("user2"))
print("user2 entries:", db.get_entries(pet_id, "user2"))

os.remove("test.db")