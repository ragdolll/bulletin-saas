"""Seed the database with placeholder family data. Run once."""

from db import connect, init_db

PEOPLE = [
    {
        "name": "Sarah Lim",
        "relationship": "daughter",
        "spouse": "David Lim",
        "children": "Emma Lim, Noah Lim",
        "lives_in": "Singapore",
        "notes": "Eldest daughter. Works as a paediatrician. Calls every Sunday evening.",
    },
    {
        "name": "Michael Smith",
        "relationship": "son",
        "spouse": "Jennifer Smith",
        "children": "Lucas Smith",
        "lives_in": "Melbourne, Australia",
        "notes": "Younger son. Civil engineer. Visits twice a year, usually around birthdays.",
    },
    {
        "name": "Emma Lim",
        "relationship": "granddaughter",
        "spouse": None,
        "children": None,
        "lives_in": "Singapore",
        "notes": "Sarah's daughter. 12 years old. Loves drawing and gymnastics.",
    },
    {
        "name": "Noah Lim",
        "relationship": "grandson",
        "spouse": None,
        "children": None,
        "lives_in": "Singapore",
        "notes": "Sarah's son. 9 years old. Plays football, supports Liverpool.",
    },
    {
        "name": "Lucas Smith",
        "relationship": "grandson",
        "spouse": None,
        "children": None,
        "lives_in": "Melbourne, Australia",
        "notes": "Michael's son. 7 years old. Loves dinosaurs.",
    },
    {
        "name": "John Smith",
        "relationship": "brother",
        "spouse": "Margaret Smith (deceased)",
        "children": "Peter Smith",
        "lives_in": "Manchester, UK",
        "notes": "Older brother. Retired teacher. Margaret passed away in 2019.",
    },
    {
        "name": "Helen Tan",
        "relationship": "wife",
        "spouse": None,
        "children": "Sarah Lim, Michael Smith",
        "lives_in": "same household",
        "notes": "Married 1972. Retired nurse. Loves gardening.",
    },
]

PLACES = [
    {
        "place": "Penang, Malaysia",
        "significance": "Birthplace and childhood home",
        "years": "1947-1965",
        "notes": "Grew up in George Town. Family ran a small grocery shop on Lebuh Chulia.",
    },
    {
        "place": "London, UK",
        "significance": "University and early career",
        "years": "1966-1975",
        "notes": "Studied engineering at Imperial College. Met Helen there in 1970.",
    },
    {
        "place": "Singapore",
        "significance": "Long-term family home",
        "years": "1975-present",
        "notes": "Moved here after marriage. Raised Sarah and Michael in Bishan.",
    },
]

EVENTS = [
    {
        "event": "Wedding to Helen Tan",
        "date": "1972-06-15",
        "people_involved": "Helen Tan, John Smith",
        "description": "Small ceremony at St Mary's in London. John was best man.",
    },
    {
        "event": "Sarah's birth",
        "date": "1974-03-22",
        "people_involved": "Helen Tan, Sarah Lim",
        "description": "Born at King's College Hospital, London.",
    },
    {
        "event": "Move to Singapore",
        "date": "1975-09-01",
        "people_involved": "Helen Tan, Sarah Lim",
        "description": "Relocated for an engineering role. First lived in Toa Payoh.",
    },
    {
        "event": "Michael's birth",
        "date": "1978-11-08",
        "people_involved": "Helen Tan, Michael Smith",
        "description": "Born at Mount Elizabeth Hospital, Singapore.",
    },
    {
        "event": "50th wedding anniversary",
        "date": "2022-06-15",
        "people_involved": "Helen Tan, Sarah Lim, Michael Smith, John Smith",
        "description": "Celebrated with whole family at a restaurant on Sentosa. John flew in from the UK.",
    },
]

STORIES = [
    {
        "title": "The grocery shop in Penang",
        "date_told": "2024-01-12",
        "told_by": "self",
        "transcript": (
            "My father ran a small grocery on Lebuh Chulia. I used to help after school, "
            "weighing rice and stacking tins. The shop smelled of dried shrimp and old wood. "
            "Mr Krishnan from next door would come in every morning for his cigarettes."
        ),
        "summary": "Childhood memory of helping at the family grocery shop in George Town, Penang.",
        "topics": "Penang, childhood, family business, Lebuh Chulia",
    },
    {
        "title": "Meeting Helen at Imperial",
        "date_told": "2024-02-03",
        "told_by": "self",
        "transcript": (
            "I met Helen in the library in 1970. She was studying nursing across the road and "
            "came to our library because it was quieter. I dropped a stack of textbooks trying "
            "to impress her. She laughed and helped me pick them up."
        ),
        "summary": "How he met his wife Helen at Imperial College library in 1970.",
        "topics": "Helen, London, Imperial College, courtship",
    },
]


def seed() -> None:
    init_db()
    with connect() as conn:
        cur = conn.cursor()

        # Clear existing seeded data so reruns are idempotent.
        for table in ("people", "places", "events", "stories"):
            cur.execute(f"DELETE FROM {table}")

        cur.executemany(
            "INSERT INTO people (name, relationship, spouse, children, lives_in, notes) "
            "VALUES (:name, :relationship, :spouse, :children, :lives_in, :notes)",
            PEOPLE,
        )
        cur.executemany(
            "INSERT INTO places (place, significance, years, notes) "
            "VALUES (:place, :significance, :years, :notes)",
            PLACES,
        )
        cur.executemany(
            "INSERT INTO events (event, date, people_involved, description) "
            "VALUES (:event, :date, :people_involved, :description)",
            EVENTS,
        )
        cur.executemany(
            "INSERT INTO stories (title, date_told, told_by, transcript, summary, topics) "
            "VALUES (:title, :date_told, :told_by, :transcript, :summary, :topics)",
            STORIES,
        )
        conn.commit()
        print(
            f"Seeded {len(PEOPLE)} people, {len(PLACES)} places, "
            f"{len(EVENTS)} events, {len(STORIES)} stories."
        )


if __name__ == "__main__":
    seed()
