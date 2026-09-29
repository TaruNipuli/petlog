"""Species and field definitions.

Field types:
- "scale":  integer slider between min and max
- "number": numeric input (float if step is a float, otherwise int)
- "choice": one option from a list
- "text":   free text
"""

# Fields that every pet has
COMMON_FIELDS = [
    {"key": "mood", "label": "Mood (1 = poor, 5 = great)",
     "type": "scale", "min": 1, "max": 5, "default": 3},
    {"key": "appetite", "label": "Appetite (1 = none, 5 = great)",
     "type": "scale", "min": 1, "max": 5, "default": 3},
    {"key": "sleep_hours", "label": "Sleep (hours)",
     "type": "number", "min": 0.0, "max": 24.0, "step": 0.5, "default": 8.0},
    {"key": "exercise_minutes", "label": "Exercise (minutes)",
     "type": "number", "min": 0, "max": 600, "step": 5, "default": 0},
    {"key": "notes", "label": "Notes", "type": "text", "default": ""},
]

# Extra fields for each species
SPECIES = {
    "dog": {
        "label": "Dog",
        "fields": [
            {"key": "walk_distance_km", "label": "Walk distance (km)",
             "type": "number", "min": 0.0, "max": 50.0, "step": 0.5, "default": 0.0},
        ],
    },
    "cat": {
        "label": "Cat",
        "fields": [
            {"key": "litter_box_visits", "label": "Litter box visits",
             "type": "number", "min": 0, "max": 30, "step": 1, "default": 0},
        ],
    },
    "rabbit": {
        "label": "Rabbit",
        "fields": [
            {"key": "hay_eaten", "label": "Hay eaten",
             "type": "choice", "options": ["Lots", "Some", "Little"], "default": "Lots"},
        ],
    },
    "guinea_pig": {
        "label": "Guinea pig",
        "fields": [
            {"key": "vegetables_given", "label": "Vegetables given",
             "type": "choice", "options": ["Yes", "No"], "default": "Yes"},
        ],
    },
    "horse": {
        "label": "Horse",
        "fields": [
            {"key": "training_type", "label": "Training type",
             "type": "choice",
             "options": ["None", "Walk", "Riding", "Groundwork", "Jumping", "Other"],
             "default": "None"},
        ],
    },
    "other": {
        "label": "Other",
        "fields": [],
    },
}


def species_options():
    """Return a list of (key, label) pairs for a species dropdown"""
    return [(key, data["label"]) for key, data in SPECIES.items()]


def get_fields(species_key):
    """Return the common fields plus the extra fields for one species"""
    extra = SPECIES.get(species_key, SPECIES["other"])["fields"]
    return COMMON_FIELDS + extra