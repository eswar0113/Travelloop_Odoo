from app import create_app
from models import db, City, Activity

app = create_app()

CITIES = [
    {'name': 'Paris', 'country': 'France', 'region': 'Europe', 'cost_index': 75, 'popularity': 95,
     'description': 'The City of Light — iconic art, fashion, and the Eiffel Tower.',
     'image_url': 'https://images.unsplash.com/photo-1502602449-6b949d4e1af7?w=600&h=400&fit=crop'},
    {'name': 'Tokyo', 'country': 'Japan', 'region': 'Asia', 'cost_index': 70, 'popularity': 92,
     'description': 'Ancient temples collide with futuristic neon in Japan\'s capital.',
     'image_url': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=600&h=400&fit=crop'},
    {'name': 'New York', 'country': 'USA', 'region': 'North America', 'cost_index': 88, 'popularity': 98,
     'description': 'The city that never sleeps — skyscrapers, Broadway, and endless energy.',
     'image_url': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?w=600&h=400&fit=crop'},
    {'name': 'London', 'country': 'UK', 'region': 'Europe', 'cost_index': 82, 'popularity': 94,
     'description': 'History, culture, and iconic landmarks along the Thames.',
     'image_url': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=600&h=400&fit=crop'},
    {'name': 'Bangkok', 'country': 'Thailand', 'region': 'Asia', 'cost_index': 30, 'popularity': 88,
     'description': 'Street food, golden temples, and vibrant nightlife in Southeast Asia.',
     'image_url': 'https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=600&h=400&fit=crop'},
    {'name': 'Bali', 'country': 'Indonesia', 'region': 'Asia', 'cost_index': 35, 'popularity': 90,
     'description': 'Island paradise of rice terraces, Hindu temples, and turquoise beaches.',
     'image_url': 'https://images.unsplash.com/photo-1537996134519-0dda8571c311?w=600&h=400&fit=crop'},
    {'name': 'Barcelona', 'country': 'Spain', 'region': 'Europe', 'cost_index': 65, 'popularity': 89,
     'description': "Gaudí's masterpieces, tapas culture, and Mediterranean beaches.",
     'image_url': 'https://images.unsplash.com/photo-1539037116277-4db20889f2d4?w=600&h=400&fit=crop'},
    {'name': 'Dubai', 'country': 'UAE', 'region': 'Middle East', 'cost_index': 90, 'popularity': 87,
     'description': 'Ultra-modern skyline, desert safaris, and world-class luxury.',
     'image_url': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&h=400&fit=crop'},
    {'name': 'Singapore', 'country': 'Singapore', 'region': 'Asia', 'cost_index': 80, 'popularity': 85,
     'description': 'A city-state of Gardens by the Bay, hawker food, and futuristic skyline.',
     'image_url': 'https://images.unsplash.com/photo-1525625293386-4b5e31dc0ce7?w=600&h=400&fit=crop'},
    {'name': 'Rome', 'country': 'Italy', 'region': 'Europe', 'cost_index': 68, 'popularity': 91,
     'description': 'The Eternal City — Colosseum, Vatican, and world-class Italian cuisine.',
     'image_url': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=600&h=400&fit=crop'},
    {'name': 'Kyoto', 'country': 'Japan', 'region': 'Asia', 'cost_index': 62, 'popularity': 86,
     'description': 'Ancient temples, bamboo groves, geisha districts, and autumn leaves.',
     'image_url': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=600&h=400&fit=crop'},
    {'name': 'Amsterdam', 'country': 'Netherlands', 'region': 'Europe', 'cost_index': 72, 'popularity': 84,
     'description': 'Canals, world-class museums, cycling culture, and Dutch hospitality.',
     'image_url': 'https://images.unsplash.com/photo-1534351590666-13e3e96b5017?w=600&h=400&fit=crop'},
    {'name': 'Istanbul', 'country': 'Turkey', 'region': 'Europe', 'cost_index': 45, 'popularity': 83,
     'description': 'A city bridging two continents, rich with bazaars, mosques, and history.',
     'image_url': 'https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=600&h=400&fit=crop'},
    {'name': 'Prague', 'country': 'Czech Republic', 'region': 'Europe', 'cost_index': 50, 'popularity': 82,
     'description': 'Fairy-tale architecture, medieval old town, and legendary Czech beer.',
     'image_url': 'https://images.unsplash.com/photo-1541849546-216549ae216d?w=600&h=400&fit=crop'},
    {'name': 'Lisbon', 'country': 'Portugal', 'region': 'Europe', 'cost_index': 55, 'popularity': 80,
     'description': 'Hilltop viewpoints, fado music, and the best pastéis de nata in the world.',
     'image_url': 'https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=600&h=400&fit=crop'},
    {'name': 'Cape Town', 'country': 'South Africa', 'region': 'Africa', 'cost_index': 40, 'popularity': 79,
     'description': 'Table Mountain, vineyards, penguins, and vibrant African culture.',
     'image_url': 'https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=600&h=400&fit=crop'},
    {'name': 'Sydney', 'country': 'Australia', 'region': 'Oceania', 'cost_index': 78, 'popularity': 85,
     'description': 'Harbour Bridge, Opera House, golden beaches, and outdoor lifestyle.',
     'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&h=400&fit=crop'},
    {'name': 'Santorini', 'country': 'Greece', 'region': 'Europe', 'cost_index': 80, 'popularity': 88,
     'description': 'White-washed buildings, blue-domed churches, and Aegean sunsets.',
     'image_url': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=600&h=400&fit=crop'},
    {'name': 'Marrakech', 'country': 'Morocco', 'region': 'Africa', 'cost_index': 35, 'popularity': 78,
     'description': 'Souks, riads, Djemaa el-Fna square, and the magic of the medina.',
     'image_url': 'https://images.unsplash.com/photo-1489749798305-4fea3ae63d43?w=600&h=400&fit=crop'},
    {'name': 'Buenos Aires', 'country': 'Argentina', 'region': 'South America', 'cost_index': 38, 'popularity': 76,
     'description': 'Tango, juicy steaks, tree-lined boulevards, and European-style architecture.',
     'image_url': 'https://images.unsplash.com/photo-1589909202802-8f4aadce5b56?w=600&h=400&fit=crop'},
]

ACTIVITIES = {
    'Paris': [
        {'name': 'Eiffel Tower Visit', 'category': 'sightseeing', 'cost': 28, 'duration': 3,
         'description': 'Climb or take the lift to the top of the iconic iron lattice tower.'},
        {'name': 'Louvre Museum', 'category': 'culture', 'cost': 17, 'duration': 4,
         'description': "World's largest art museum — home to the Mona Lisa and Venus de Milo."},
        {'name': 'Seine River Cruise', 'category': 'sightseeing', 'cost': 15, 'duration': 1,
         'description': 'Float past Notre-Dame, the Eiffel Tower, and Musée d\'Orsay by boat.'},
        {'name': 'Montmartre Food Walk', 'category': 'food', 'cost': 35, 'duration': 3,
         'description': 'Taste croissants, cheese, and wine in the artistic Montmartre district.'},
        {'name': 'Palace of Versailles', 'category': 'culture', 'cost': 20, 'duration': 5,
         'description': 'Explore the lavish palace and sprawling gardens of French royalty.'},
    ],
    'Tokyo': [
        {'name': 'Senso-ji Temple', 'category': 'culture', 'cost': 0, 'duration': 2,
         'description': 'Tokyo\'s oldest and most significant Buddhist temple in Asakusa.'},
        {'name': 'Shibuya Crossing', 'category': 'sightseeing', 'cost': 0, 'duration': 1,
         'description': 'Experience the world\'s busiest pedestrian crossing at rush hour.'},
        {'name': 'Tsukiji Outer Market', 'category': 'food', 'cost': 20, 'duration': 2,
         'description': 'Sample the freshest sushi and seafood at the world-famous fish market.'},
        {'name': 'teamLab Borderless', 'category': 'adventure', 'cost': 32, 'duration': 3,
         'description': 'Immersive digital art museum where art moves between rooms freely.'},
        {'name': 'Mt. Fuji Day Trip', 'category': 'adventure', 'cost': 50, 'duration': 10,
         'description': 'Take the Shinkansen to see Japan\'s sacred volcano up close.'},
    ],
    'New York': [
        {'name': 'Statue of Liberty', 'category': 'sightseeing', 'cost': 24, 'duration': 4,
         'description': 'Ferry to Liberty Island and explore America\'s iconic symbol of freedom.'},
        {'name': 'Central Park Bike Tour', 'category': 'adventure', 'cost': 45, 'duration': 3,
         'description': 'Cycle through 843 acres of greenery in the heart of Manhattan.'},
        {'name': 'Broadway Show', 'category': 'culture', 'cost': 120, 'duration': 3,
         'description': 'Catch a world-class musical or play on the Great White Way.'},
        {'name': 'High Line Walk', 'category': 'sightseeing', 'cost': 0, 'duration': 2,
         'description': 'Stroll the elevated linear park built on a historic freight rail line.'},
        {'name': 'NYC Food Tour', 'category': 'food', 'cost': 65, 'duration': 3,
         'description': 'Pizza in Brooklyn, bagels in Lower East Side, and cheesecake in Midtown.'},
    ],
    'London': [
        {'name': 'Tower of London', 'category': 'culture', 'cost': 33, 'duration': 3,
         'description': 'Explore the historic castle and see the Crown Jewels.'},
        {'name': 'British Museum', 'category': 'culture', 'cost': 0, 'duration': 4,
         'description': 'Free admission to one of the world\'s greatest collections of human history.'},
        {'name': 'Thames River Walk', 'category': 'sightseeing', 'cost': 0, 'duration': 2,
         'description': 'Walk from Tower Bridge to the Tate Modern along the South Bank.'},
        {'name': 'Afternoon Tea', 'category': 'food', 'cost': 55, 'duration': 2,
         'description': 'Savour scones, finger sandwiches, and fine tea in a classic tearoom.'},
        {'name': 'West End Musical', 'category': 'culture', 'cost': 85, 'duration': 3,
         'description': 'Catch a top-tier musical at one of London\'s legendary theatres.'},
    ],
    'Bangkok': [
        {'name': 'Grand Palace & Wat Phra Kaew', 'category': 'culture', 'cost': 15, 'duration': 3,
         'description': 'The dazzling royal palace complex housing the sacred Emerald Buddha.'},
        {'name': 'Floating Market Tour', 'category': 'food', 'cost': 20, 'duration': 4,
         'description': 'Shop and eat at vendors selling goods from traditional wooden boats.'},
        {'name': 'Muay Thai Night', 'category': 'adventure', 'cost': 30, 'duration': 3,
         'description': 'Watch authentic Muay Thai bouts at Rajadamnern Stadium.'},
        {'name': 'Street Food Tour', 'category': 'food', 'cost': 25, 'duration': 3,
         'description': 'Pad Thai, mango sticky rice, and Tom Yum on Bangkok\'s night streets.'},
        {'name': 'Chao Phraya River Cruise', 'category': 'sightseeing', 'cost': 10, 'duration': 2,
         'description': 'Sunset dinner cruise past temples and the Bangkok skyline.'},
    ],
    'Bali': [
        {'name': 'Ubud Monkey Forest', 'category': 'adventure', 'cost': 5, 'duration': 2,
         'description': 'Walk through a sacred forest with hundreds of Balinese long-tailed macaques.'},
        {'name': 'Tegalalang Rice Terraces', 'category': 'sightseeing', 'cost': 3, 'duration': 2,
         'description': 'Hike through UNESCO-listed emerald green rice paddies in Ubud.'},
        {'name': 'Tanah Lot Sunset', 'category': 'sightseeing', 'cost': 4, 'duration': 2,
         'description': 'Watch the sun set behind the iconic ocean temple perched on a rock.'},
        {'name': 'Balinese Cooking Class', 'category': 'food', 'cost': 40, 'duration': 4,
         'description': 'Learn to cook Nasi Goreng, Satay, and Lawar with a local chef.'},
        {'name': 'Surfing Lesson in Kuta', 'category': 'adventure', 'cost': 35, 'duration': 3,
         'description': 'Catch your first wave on Bali\'s legendary surfing beach.'},
    ],
    'Barcelona': [
        {'name': 'Sagrada Família', 'category': 'culture', 'cost': 26, 'duration': 2,
         'description': 'Gaudí\'s extraordinary unfinished basilica — a UNESCO World Heritage Site.'},
        {'name': 'Park Güell', 'category': 'sightseeing', 'cost': 10, 'duration': 2,
         'description': 'Colourful mosaic terraces and whimsical sculptures by Antoni Gaudí.'},
        {'name': 'La Boqueria Market', 'category': 'food', 'cost': 15, 'duration': 2,
         'description': 'Barcelona\'s famous covered market bursting with fresh produce and tapas.'},
        {'name': 'Gothic Quarter Walk', 'category': 'sightseeing', 'cost': 0, 'duration': 2,
         'description': 'Wander the narrow medieval streets of Barcelona\'s oldest neighbourhood.'},
        {'name': 'Flamenco Show', 'category': 'culture', 'cost': 45, 'duration': 2,
         'description': 'Watch passionate flamenco dancing and live guitar in an intimate tablao.'},
    ],
    'Dubai': [
        {'name': 'Burj Khalifa Observation Deck', 'category': 'sightseeing', 'cost': 40, 'duration': 2,
         'description': 'Take the high-speed elevator to the world\'s tallest building at 828m.'},
        {'name': 'Desert Safari & BBQ', 'category': 'adventure', 'cost': 75, 'duration': 6,
         'description': 'Dune bashing, camel riding, and a starlit BBQ dinner in the Arabian desert.'},
        {'name': 'Dubai Mall & Aquarium', 'category': 'sightseeing', 'cost': 30, 'duration': 4,
         'description': 'World\'s largest mall with an underwater zoo and 33,000 aquatic animals.'},
        {'name': 'Old Dubai Spice Souk', 'category': 'food', 'cost': 5, 'duration': 2,
         'description': 'Explore narrow alleyways piled high with saffron, frankincense, and spices.'},
        {'name': 'Ski Dubai', 'category': 'adventure', 'cost': 85, 'duration': 4,
         'description': 'Ski on real snow inside a giant mall in the middle of the desert.'},
    ],
    'Singapore': [
        {'name': 'Gardens by the Bay', 'category': 'sightseeing', 'cost': 14, 'duration': 3,
         'description': 'Walk among the iconic Supertrees and explore the giant glass domes.'},
        {'name': 'Hawker Centre Food Tour', 'category': 'food', 'cost': 20, 'duration': 3,
         'description': 'Chicken rice, laksa, and chilli crab at iconic Maxwell or Lau Pa Sat.'},
        {'name': 'Universal Studios Singapore', 'category': 'adventure', 'cost': 81, 'duration': 8,
         'description': 'Thrilling rides and movie-themed zones on Sentosa Island.'},
        {'name': 'Marina Bay Sands Skypark', 'category': 'sightseeing', 'cost': 26, 'duration': 2,
         'description': 'Rooftop infinity pool and 360° views from the world-famous hotel.'},
        {'name': 'Chinatown Heritage Centre', 'category': 'culture', 'cost': 12, 'duration': 2,
         'description': 'Discover the story of early Chinese immigrants to Singapore.'},
    ],
    'Rome': [
        {'name': 'Colosseum & Roman Forum', 'category': 'culture', 'cost': 18, 'duration': 4,
         'description': 'Walk through 2,000 years of history at the ancient amphitheatre and forum.'},
        {'name': 'Vatican Museums & Sistine Chapel', 'category': 'culture', 'cost': 20, 'duration': 4,
         'description': 'Marvel at Michelangelo\'s ceiling and the world\'s greatest art collection.'},
        {'name': 'Trastevere Food Walk', 'category': 'food', 'cost': 40, 'duration': 3,
         'description': 'Cacio e pepe, supplì, and gelato in Rome\'s most charming neighbourhood.'},
        {'name': 'Trevi Fountain & Spanish Steps', 'category': 'sightseeing', 'cost': 0, 'duration': 2,
         'description': 'Toss a coin in the Trevi Fountain then climb the iconic 135-step staircase.'},
        {'name': 'Pizza Making Class', 'category': 'food', 'cost': 55, 'duration': 3,
         'description': 'Learn authentic Roman pizza-making from a local chef.'},
    ],
}

GENERIC_ACTIVITIES = [
    {'name': 'City Walking Tour', 'category': 'sightseeing', 'cost': 20, 'duration': 3,
     'description': 'Explore the city\'s highlights with a knowledgeable local guide.'},
    {'name': 'Local Food Tour', 'category': 'food', 'cost': 35, 'duration': 3,
     'description': 'Taste the city\'s best street food and local specialties.'},
    {'name': 'Museum Visit', 'category': 'culture', 'cost': 15, 'duration': 3,
     'description': 'Discover the local history and culture at the main city museum.'},
    {'name': 'Day Hike', 'category': 'adventure', 'cost': 10, 'duration': 6,
     'description': 'Explore the natural landscapes surrounding the city on foot.'},
    {'name': 'Sunset Viewpoint', 'category': 'sightseeing', 'cost': 0, 'duration': 2,
     'description': 'Watch the sun go down from the city\'s most scenic viewpoint.'},
]


def seed():
    with app.app_context():
        if City.query.count() > 0:
            print('Database already seeded. Skipping.')
            return

        print('Seeding cities...')
        city_map = {}
        for c in CITIES:
            city = City(**c)
            db.session.add(city)
            db.session.flush()
            city_map[c['name']] = city

        print('Seeding activities...')
        for city_name, acts in ACTIVITIES.items():
            city = city_map.get(city_name)
            if not city:
                continue
            for a in acts:
                act = Activity(city_id=city.id, name=a['name'], category=a['category'],
                               estimated_cost=a['cost'], duration_hours=a['duration'],
                               description=a['description'])
                db.session.add(act)

        for city in city_map.values():
            if city.name not in ACTIVITIES:
                for a in GENERIC_ACTIVITIES:
                    act = Activity(city_id=city.id, name=a['name'], category=a['category'],
                                   estimated_cost=a['cost'], duration_hours=a['duration'],
                                   description=a['description'])
                    db.session.add(act)

        db.session.commit()
        print(f'Seeded {len(CITIES)} cities and activities successfully.')


if __name__ == '__main__':
    seed()
