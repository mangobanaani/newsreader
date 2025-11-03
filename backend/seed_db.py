#!/usr/bin/env python3
"""Seed the database with initial admin user and feed library."""

import os
import sys

# Add the parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Use dev database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# Create engine and session
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Feed library data - comprehensive list of RSS feeds
FEED_LIBRARY = [
    # Finland - News (Finnish)
    {'name': 'Yle Uutiset - Tuoreimmat', 'url': 'https://yle.fi/rss/uutiset/tuoreimmat', 'category': 'News', 'country': 'FI', 'description': 'Latest Finnish news from Yle'},
    {'name': 'Yle Uutiset - Pääuutiset', 'url': 'https://yle.fi/rss/uutiset/paauutiset', 'category': 'News', 'country': 'FI', 'description': 'Top headlines from Yle'},
    {'name': 'Yle News - English', 'url': 'https://yle.fi/rss/news', 'category': 'News', 'country': 'FI', 'description': 'Yle News in English'},
    {'name': 'Helsingin Sanomat - Suomi', 'url': 'https://www.hs.fi/rss/suomi.xml', 'category': 'News', 'country': 'FI', 'description': 'Domestic Finnish news'},
    {'name': 'Helsingin Sanomat - Maailma', 'url': 'https://www.hs.fi/rss/maailma.xml', 'category': 'News', 'country': 'FI', 'description': 'International news'},
    {'name': 'Helsingin Sanomat - Kaupunki', 'url': 'https://www.hs.fi/rss/kaupunki.xml', 'category': 'News', 'country': 'FI', 'description': 'Helsinki city news'},
    {'name': 'Iltalehti Uutiset', 'url': 'https://www.iltalehti.fi/rss/uutiset.xml', 'category': 'News', 'country': 'FI', 'description': 'Iltalehti news feed'},
    {'name': 'Ilta-Sanomat Kotimaa', 'url': 'https://www.is.fi/rss/kotimaa.xml', 'category': 'News', 'country': 'FI', 'description': 'Domestic news'},
    {'name': 'Ilta-Sanomat Ulkomaat', 'url': 'https://www.is.fi/rss/ulkomaat.xml', 'category': 'News', 'country': 'FI', 'description': 'International news'},

    # Finland - Business & Economy
    {'name': 'Helsingin Sanomat - Talous', 'url': 'https://www.hs.fi/rss/talous.xml', 'category': 'Business', 'country': 'FI', 'description': 'Finnish business news'},
    {'name': 'Kauppalehti', 'url': 'https://www.kauppalehti.fi/rss/uusimmat', 'category': 'Business', 'country': 'FI', 'description': 'Finnish business daily'},
    {'name': 'Taloussanomat', 'url': 'https://www.is.fi/rss/taloussanomat.xml', 'category': 'Business', 'country': 'FI', 'description': 'Finnish economy news'},

    # Finland - Technology
    {'name': 'Helsingin Sanomat - Tiede', 'url': 'https://www.hs.fi/rss/tiede.xml', 'category': 'Tech', 'country': 'FI', 'description': 'Science and tech news'},
    {'name': 'MikroBitti', 'url': 'https://www.mikrobitti.fi/rss/all', 'category': 'Tech', 'country': 'FI', 'description': 'Finnish tech magazine'},
    {'name': 'Tivi - IT-uutiset', 'url': 'https://www.tivi.fi/rss/uusimmat', 'category': 'Tech', 'country': 'FI', 'description': 'IT news in Finnish'},

    # Finland - Sports
    {'name': 'Yle Urheilu', 'url': 'https://yle.fi/rss/urheilu', 'category': 'Sports', 'country': 'FI', 'description': 'Finnish sports news'},
    {'name': 'Helsingin Sanomat - Urheilu', 'url': 'https://www.hs.fi/rss/urheilu.xml', 'category': 'Sports', 'country': 'FI', 'description': 'HS Sports'},
    {'name': 'Iltalehti Urheilu', 'url': 'https://www.iltalehti.fi/rss/urheilu.xml', 'category': 'Sports', 'country': 'FI', 'description': 'Sports from Iltalehti'},

    # Finland - Entertainment & Culture
    {'name': 'Helsingin Sanomat - Kulttuuri', 'url': 'https://www.hs.fi/rss/kulttuuri.xml', 'category': 'Culture', 'country': 'FI', 'description': 'Finnish culture news'},
    {'name': 'Helsingin Sanomat - Viihde', 'url': 'https://www.hs.fi/rss/viihde.xml', 'category': 'Entertainment', 'country': 'FI', 'description': 'Entertainment news'},
    {'name': 'Iltalehti Viihde', 'url': 'https://www.iltalehti.fi/rss/viihde.xml', 'category': 'Entertainment', 'country': 'FI', 'description': 'Entertainment from IL'},

    # International - Tech News
    {'name': 'Hacker News', 'url': 'https://hnrss.org/frontpage', 'category': 'Tech', 'country': 'US', 'description': 'Tech community news'},
    {'name': 'TechCrunch', 'url': 'https://techcrunch.com/feed/', 'category': 'Tech', 'country': 'US', 'description': 'Startup & tech news'},
    {'name': 'Ars Technica', 'url': 'https://feeds.arstechnica.com/arstechnica/index', 'category': 'Tech', 'country': 'US', 'description': 'Technology & culture'},
    {'name': 'The Verge', 'url': 'https://www.theverge.com/rss/index.xml', 'category': 'Tech', 'country': 'US', 'description': 'Tech, science, art'},
    {'name': 'Wired', 'url': 'https://www.wired.com/feed/rss', 'category': 'Tech', 'country': 'US', 'description': 'Technology & innovation'},
    {'name': 'Engadget', 'url': 'https://www.engadget.com/rss.xml', 'category': 'Tech', 'country': 'US', 'description': 'Consumer electronics'},

    # International - World News
    {'name': 'BBC News - World', 'url': 'https://feeds.bbci.co.uk/news/world/rss.xml', 'category': 'News', 'country': 'GB', 'description': 'World news from BBC'},
    {'name': 'BBC News - Technology', 'url': 'https://feeds.bbci.co.uk/news/technology/rss.xml', 'category': 'Tech', 'country': 'GB', 'description': 'Tech news from BBC'},
    {'name': 'The Guardian - World', 'url': 'https://www.theguardian.com/world/rss', 'category': 'News', 'country': 'GB', 'description': 'International news'},
    {'name': 'Reuters - World News', 'url': 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best', 'category': 'News', 'country': 'US', 'description': 'Global news coverage'},
    {'name': 'Al Jazeera English', 'url': 'https://www.aljazeera.com/xml/rss/all.xml', 'category': 'News', 'country': 'QA', 'description': 'International news'},

    # International - Business
    {'name': 'Bloomberg Technology', 'url': 'https://feeds.bloomberg.com/technology/news.rss', 'category': 'Business', 'country': 'US', 'description': 'Business & tech news'},
    {'name': 'Financial Times', 'url': 'https://www.ft.com/?format=rss', 'category': 'Business', 'country': 'GB', 'description': 'Global finance news'},

    # International - Science
    {'name': 'Science Daily', 'url': 'https://www.sciencedaily.com/rss/all.xml', 'category': 'Science', 'country': 'US', 'description': 'Latest science news'},
    {'name': 'Nature - Latest Research', 'url': 'https://www.nature.com/nature.rss', 'category': 'Science', 'country': 'GB', 'description': 'Scientific research'},
    {'name': 'Scientific American', 'url': 'http://rss.sciam.com/ScientificAmerican-Global', 'category': 'Science', 'country': 'US', 'description': 'Science & technology'},

    # Social Media & Communities
    {'name': 'Reddit - World News', 'url': 'https://www.reddit.com/r/worldnews/.rss', 'category': 'News', 'country': 'US', 'description': 'Community curated news'},
    {'name': 'Reddit - Technology', 'url': 'https://www.reddit.com/r/technology/.rss', 'category': 'Tech', 'country': 'US', 'description': 'Tech discussions'},
    {'name': 'Reddit - Science', 'url': 'https://www.reddit.com/r/science/.rss', 'category': 'Science', 'country': 'US', 'description': 'Science community'},

    # Gaming
    {'name': 'IGN All', 'url': 'https://feeds.ign.com/ign/all', 'category': 'Gaming', 'country': 'US', 'description': 'Gaming news and reviews'},
    {'name': 'GameSpot', 'url': 'https://www.gamespot.com/feeds/mashup/', 'category': 'Gaming', 'country': 'US', 'description': 'Video game news and reviews'},
    {'name': 'Kotaku', 'url': 'https://kotaku.com/rss', 'category': 'Gaming', 'country': 'US', 'description': 'Gaming culture and news'},
    {'name': 'PC Gamer', 'url': 'https://www.pcgamer.com/rss/', 'category': 'Gaming', 'country': 'US', 'description': 'PC gaming news'},
    {'name': 'Polygon', 'url': 'https://www.polygon.com/rss/index.xml', 'category': 'Gaming', 'country': 'US', 'description': 'Gaming and entertainment news'},
    {'name': 'Rock Paper Shotgun', 'url': 'https://www.rockpapershotgun.com/feed', 'category': 'Gaming', 'country': 'GB', 'description': 'PC gaming blog'},

    # Cryptocurrency & Blockchain
    {'name': 'CoinDesk', 'url': 'https://www.coindesk.com/arc/outboundfeeds/rss/', 'category': 'Crypto', 'country': 'US', 'description': 'Cryptocurrency news and analysis'},
    {'name': 'Cointelegraph', 'url': 'https://cointelegraph.com/rss', 'category': 'Crypto', 'country': 'US', 'description': 'Blockchain and crypto news'},
    {'name': 'Bitcoin Magazine', 'url': 'https://bitcoinmagazine.com/.rss/full/', 'category': 'Crypto', 'country': 'US', 'description': 'Bitcoin news and analysis'},
    {'name': 'Decrypt', 'url': 'https://decrypt.co/feed', 'category': 'Crypto', 'country': 'US', 'description': 'Crypto and Web3 news'},
    {'name': 'The Block', 'url': 'https://www.theblock.co/rss.xml', 'category': 'Crypto', 'country': 'US', 'description': 'Crypto and blockchain research'},

    # Design & Creativity
    {'name': 'Smashing Magazine', 'url': 'https://www.smashingmagazine.com/feed/', 'category': 'Design', 'country': 'DE', 'description': 'Web design and development'},
    {'name': 'A List Apart', 'url': 'https://alistapart.com/main/feed/', 'category': 'Design', 'country': 'US', 'description': 'Web design and standards'},
    {'name': 'CSS-Tricks', 'url': 'https://css-tricks.com/feed/', 'category': 'Design', 'country': 'US', 'description': 'Web design tips and tutorials'},
    {'name': 'Colossal', 'url': 'https://www.thisiscolossal.com/feed/', 'category': 'Art', 'country': 'US', 'description': 'Art, design, and visual culture'},
    {'name': 'Creative Bloq', 'url': 'https://www.creativebloq.com/feed', 'category': 'Design', 'country': 'GB', 'description': 'Art and design inspiration'},
    {'name': 'Behance Featured', 'url': 'https://www.behance.net/feeds/projects', 'category': 'Design', 'country': 'US', 'description': 'Creative work showcase'},

    # Photography
    {'name': 'PetaPixel', 'url': 'https://petapixel.com/feed/', 'category': 'Photography', 'country': 'US', 'description': 'Photography news and tutorials'},
    {'name': 'Digital Photography School', 'url': 'https://digital-photography-school.com/feed/', 'category': 'Photography', 'country': 'AU', 'description': 'Photography tips and techniques'},
    {'name': 'Fstoppers', 'url': 'https://fstoppers.com/rss.xml', 'category': 'Photography', 'country': 'US', 'description': 'Photography community and education'},

    # Health & Fitness
    {'name': 'Healthline', 'url': 'https://www.healthline.com/feeds/rss', 'category': 'Health', 'country': 'US', 'description': 'Health and wellness information'},
    {'name': 'WebMD', 'url': 'https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC', 'category': 'Health', 'country': 'US', 'description': 'Medical news and health info'},
    {'name': 'Medical News Today', 'url': 'https://www.medicalnewstoday.com/rss', 'category': 'Health', 'country': 'GB', 'description': 'Latest medical research'},
    {'name': 'Fitness Magazine', 'url': 'https://www.fitnessmagazine.com/rss.xml', 'category': 'Fitness', 'country': 'US', 'description': 'Fitness tips and workouts'},
    {'name': 'Yoga Journal', 'url': 'https://www.yogajournal.com/rss/', 'category': 'Fitness', 'country': 'US', 'description': 'Yoga practice and lifestyle'},

    # Cooking & Food
    {'name': 'Serious Eats', 'url': 'https://www.seriouseats.com/rss/recipes.xml', 'category': 'Food', 'country': 'US', 'description': 'Recipes and cooking techniques'},
    {'name': 'Bon Appétit', 'url': 'https://www.bonappetit.com/feed/rss', 'category': 'Food', 'country': 'US', 'description': 'Recipes and food culture'},
    {'name': 'Food52', 'url': 'https://food52.com/blog.rss', 'category': 'Food', 'country': 'US', 'description': 'Community recipes and cooking'},
    {'name': 'Epicurious', 'url': 'https://www.epicurious.com/services/rss/recipes', 'category': 'Food', 'country': 'US', 'description': 'Recipe database and cooking tips'},
    {'name': 'Minimalist Baker', 'url': 'https://minimalistbaker.com/feed/', 'category': 'Food', 'country': 'US', 'description': 'Simple plant-based recipes'},

    # Travel & Lifestyle
    {'name': 'Lonely Planet', 'url': 'https://www.lonelyplanet.com/feeds/news', 'category': 'Travel', 'country': 'GB', 'description': 'Travel guides and tips'},
    {'name': 'Nomadic Matt', 'url': 'https://www.nomadicmatt.com/feed/', 'category': 'Travel', 'country': 'US', 'description': 'Budget travel advice'},
    {'name': 'Travel + Leisure', 'url': 'https://www.travelandleisure.com/rss', 'category': 'Travel', 'country': 'US', 'description': 'Travel inspiration and tips'},
    {'name': 'Condé Nast Traveler', 'url': 'https://www.cntraveler.com/feed/rss', 'category': 'Travel', 'country': 'US', 'description': 'Luxury travel and culture'},
    {'name': 'The Points Guy', 'url': 'https://thepointsguy.com/feed/', 'category': 'Travel', 'country': 'US', 'description': 'Travel rewards and miles'},

    # Fashion & Style
    {'name': 'Vogue', 'url': 'https://www.vogue.com/feed/rss', 'category': 'Fashion', 'country': 'US', 'description': 'Fashion and style trends'},
    {'name': 'GQ', 'url': 'https://www.gq.com/feed/rss', 'category': 'Fashion', 'country': 'US', 'description': "Men's fashion and lifestyle"},
    {'name': 'Elle', 'url': 'https://www.elle.com/rss/all.xml/', 'category': 'Fashion', 'country': 'US', 'description': 'Fashion trends and beauty'},
    {'name': 'Fashionista', 'url': 'https://fashionista.com/.rss/full/', 'category': 'Fashion', 'country': 'US', 'description': 'Fashion industry news'},

    # Entertainment & Pop Culture
    {'name': 'Variety', 'url': 'https://variety.com/feed/', 'category': 'Entertainment', 'country': 'US', 'description': 'Entertainment industry news'},
    {'name': 'The Hollywood Reporter', 'url': 'https://www.hollywoodreporter.com/feed/', 'category': 'Entertainment', 'country': 'US', 'description': 'Film and TV industry news'},
    {'name': 'Deadline', 'url': 'https://deadline.com/feed/', 'category': 'Entertainment', 'country': 'US', 'description': 'Hollywood breaking news'},
    {'name': 'Rolling Stone', 'url': 'https://www.rollingstone.com/feed/', 'category': 'Music', 'country': 'US', 'description': 'Music and pop culture'},
    {'name': 'Pitchfork', 'url': 'https://pitchfork.com/rss/news/', 'category': 'Music', 'country': 'US', 'description': 'Music reviews and news'},
    {'name': 'Billboard', 'url': 'https://www.billboard.com/feed/', 'category': 'Music', 'country': 'US', 'description': 'Music charts and news'},

    # Movies & TV
    {'name': 'IndieWire', 'url': 'https://www.indiewire.com/feed/', 'category': 'Movies', 'country': 'US', 'description': 'Independent film news'},
    {'name': 'Screen Rant', 'url': 'https://screenrant.com/feed/', 'category': 'Movies', 'country': 'US', 'description': 'Movie and TV news'},
    {'name': 'Collider', 'url': 'https://collider.com/feed/', 'category': 'Movies', 'country': 'US', 'description': 'Entertainment news and reviews'},
    {'name': 'Den of Geek', 'url': 'https://www.denofgeek.com/feed/', 'category': 'Entertainment', 'country': 'GB', 'description': 'Pop culture and geek news'},

    # Sports - International
    {'name': 'ESPN', 'url': 'https://www.espn.com/espn/rss/news', 'category': 'Sports', 'country': 'US', 'description': 'Sports news and scores'},
    {'name': 'Sky Sports', 'url': 'https://www.skysports.com/rss/12040', 'category': 'Sports', 'country': 'GB', 'description': 'UK sports news'},
    {'name': 'The Athletic', 'url': 'https://theathletic.com/feeds/rss/', 'category': 'Sports', 'country': 'US', 'description': 'In-depth sports coverage'},
    {'name': 'Bleacher Report', 'url': 'https://bleacherreport.com/articles/feed', 'category': 'Sports', 'country': 'US', 'description': 'Sports news and highlights'},

    # Environment & Climate
    {'name': 'Grist', 'url': 'https://grist.org/feed/', 'category': 'Environment', 'country': 'US', 'description': 'Climate and sustainability news'},
    {'name': 'Inside Climate News', 'url': 'https://insideclimatenews.org/feed/', 'category': 'Environment', 'country': 'US', 'description': 'Climate journalism'},
    {'name': 'TreeHugger', 'url': 'https://www.treehugger.com/rss', 'category': 'Environment', 'country': 'US', 'description': 'Sustainability and green living'},

    # Space & Astronomy
    {'name': 'Space.com', 'url': 'https://www.space.com/feeds/all', 'category': 'Space', 'country': 'US', 'description': 'Space and astronomy news'},
    {'name': 'NASA', 'url': 'https://www.nasa.gov/rss/dyn/breaking_news.rss', 'category': 'Space', 'country': 'US', 'description': 'NASA news and updates'},
    {'name': 'Universe Today', 'url': 'https://www.universetoday.com/feed/', 'category': 'Space', 'country': 'CA', 'description': 'Space exploration news'},

    # History & Culture
    {'name': 'Smithsonian Magazine', 'url': 'https://www.smithsonianmag.com/rss/latest_articles/', 'category': 'Culture', 'country': 'US', 'description': 'History, science, and culture'},
    {'name': 'History', 'url': 'https://www.history.com/feeds/rss', 'category': 'History', 'country': 'US', 'description': 'Historical articles and stories'},

    # Psychology & Personal Development
    {'name': 'Psychology Today', 'url': 'https://www.psychologytoday.com/us/front/feed', 'category': 'Psychology', 'country': 'US', 'description': 'Psychology and mental health'},
    {'name': 'Brain Pickings', 'url': 'https://www.themarginalian.org/feed/', 'category': 'Culture', 'country': 'US', 'description': 'Literature, philosophy, and art'},
    {'name': 'Farnam Street', 'url': 'https://fs.blog/feed/', 'category': 'Learning', 'country': 'US', 'description': 'Wisdom and decision-making'},

    # Parenting & Family
    {'name': 'Scary Mommy', 'url': 'https://www.scarymommy.com/feed/', 'category': 'Parenting', 'country': 'US', 'description': 'Parenting humor and advice'},
    {'name': 'Parents Magazine', 'url': 'https://www.parents.com/feed/', 'category': 'Parenting', 'country': 'US', 'description': 'Parenting tips and advice'},

    # DIY & Crafts
    {'name': 'Make Magazine', 'url': 'https://makezine.com/feed/', 'category': 'DIY', 'country': 'US', 'description': 'DIY projects and making'},
    {'name': 'Instructables', 'url': 'https://www.instructables.com/rss/', 'category': 'DIY', 'country': 'US', 'description': 'DIY tutorials and projects'},

    # Cars & Automotive
    {'name': 'Car and Driver', 'url': 'https://www.caranddriver.com/rss/all.xml/', 'category': 'Automotive', 'country': 'US', 'description': 'Car reviews and auto news'},
    {'name': 'Motor Trend', 'url': 'https://www.motortrend.com/rss/', 'category': 'Automotive', 'country': 'US', 'description': 'Automotive news and reviews'},
    {'name': 'Top Gear', 'url': 'https://www.topgear.com/rss', 'category': 'Automotive', 'country': 'GB', 'description': 'Car reviews and motoring'},

    # Pets & Animals
    {'name': 'The Dodo', 'url': 'https://www.thedodo.com/rss', 'category': 'Pets', 'country': 'US', 'description': 'Animal news and stories'},
    {'name': 'National Geographic Animals', 'url': 'https://www.nationalgeographic.com/animals/rss', 'category': 'Animals', 'country': 'US', 'description': 'Wildlife and animal stories'},

    # Real Estate & Architecture
    {'name': 'ArchDaily', 'url': 'https://www.archdaily.com/feed/', 'category': 'Architecture', 'country': 'CL', 'description': 'Architecture news and projects'},
    {'name': 'Dezeen', 'url': 'https://www.dezeen.com/feed/', 'category': 'Design', 'country': 'GB', 'description': 'Architecture and design magazine'},
    {'name': 'Apartment Therapy', 'url': 'https://www.apartmenttherapy.com/main.rss', 'category': 'Home', 'country': 'US', 'description': 'Home decor and design'},
]


def seed_database():
    """Seed the database with initial data."""
    db = SessionLocal()

    try:
        # Create tables if they don't exist
        with engine.begin() as conn:
            try:
                # Create users table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email VARCHAR NOT NULL UNIQUE,
                        hashed_password VARCHAR NOT NULL,
                        is_active BOOLEAN DEFAULT 1
                    )
                """))
                print("✅ Users table created/verified")

                # Create feeds table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS feeds (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        url VARCHAR NOT NULL,
                        title VARCHAR,
                        description TEXT,
                        is_active BOOLEAN DEFAULT 0,
                        last_fetched TIMESTAMP,
                        country_code VARCHAR(2),
                        category VARCHAR,
                        is_library BOOLEAN DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """))
                print("✅ Feeds table created/verified")

            except Exception as e:
                print(f"Table creation note: {e}")

        # Create admin user
        result = db.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": "admin@newsreader.local"}
        )
        existing_user = result.fetchone()

        if existing_user:
            print("\n✅ Admin user already exists!")
            admin_id = existing_user[0]  # Get user ID
        else:
            # Pre-computed bcrypt hash for password "admin123"
            admin_password_hash = "$2b$12$oHmQS28PINu7YF9LB8xdxepYKd9hP6Pkk4fVaJHODboJn1ieaJpiS"

            db.execute(
                text("""
                    INSERT INTO users (email, hashed_password, is_active)
                    VALUES (:email, :password, :active)
                """),
                {
                    "email": "admin@newsreader.local",
                    "password": admin_password_hash,
                    "active": True
                }
            )
            db.commit()
            print("\n✅ Admin user created successfully!")

            # Get admin ID
            result = db.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": "admin@newsreader.local"}
            )
            admin_id = result.fetchone()[0]

        # Seed feed library for admin user
        print("\n📚 Seeding feed library...")
        feeds_added = 0
        feeds_skipped = 0

        for feed_data in FEED_LIBRARY:
            # Check if feed already exists
            result = db.execute(
                text("SELECT id FROM feeds WHERE url = :url AND user_id = :user_id"),
                {"url": feed_data['url'], "user_id": admin_id}
            )
            existing_feed = result.fetchone()

            if not existing_feed:
                db.execute(
                    text("""
                        INSERT INTO feeds (user_id, url, title, description, is_active, country_code, category, is_library)
                        VALUES (:user_id, :url, :title, :description, :is_active, :country_code, :category, :is_library)
                    """),
                    {
                        "user_id": admin_id,
                        "url": feed_data['url'],
                        "title": feed_data['name'],
                        "description": feed_data.get('description', ''),
                        "is_active": False,  # Inactive by default
                        "country_code": feed_data.get('country', ''),
                        "category": feed_data.get('category', ''),
                        "is_library": True  # Mark as library feed
                    }
                )
                feeds_added += 1
            else:
                feeds_skipped += 1

        db.commit()
        print(f"✅ Feed library seeded: {feeds_added} added, {feeds_skipped} already existed")

        print("\n" + "="*60)
        print("ADMIN LOGIN CREDENTIALS:")
        print("="*60)
        print("  Email:    admin@newsreader.local")
        print("  Password: admin123")
        print("="*60)
        print(f"\n📊 Database Summary:")
        print(f"  - Users: 1")
        print(f"  - Feeds in Library: {len(FEED_LIBRARY)}")
        print("="*60)
        print("\n⚠️  IMPORTANT: Change the admin password after first login!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🌱 Starting database seeding...")
    seed_database()
    print("\n💡 Tip: Run 'make dev' to start both backend and frontend servers")
