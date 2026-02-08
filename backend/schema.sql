-- NewsReader database schema
-- Run this to initialize the PostgreSQL database:
--   docker exec -i newsreader-db psql -U newsreader -d newsreader < backend/schema.sql

CREATE TABLE IF NOT EXISTS feed_templates (
	id SERIAL NOT NULL,
	name VARCHAR NOT NULL,
	description TEXT,
	category VARCHAR,
	icon VARCHAR,
	suggested_feeds JSON,
	rules JSON,
	preferences JSON,
	is_public BOOLEAN DEFAULT TRUE,
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS users (
	id SERIAL NOT NULL,
	email VARCHAR NOT NULL,
	hashed_password VARCHAR,
	is_active BOOLEAN DEFAULT TRUE,
	is_superuser BOOLEAN DEFAULT FALSE,
	oauth_provider VARCHAR,
	oauth_id VARCHAR,
	picture VARCHAR,
	PRIMARY KEY (id)
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email);

CREATE TABLE IF NOT EXISTS feeds (
	id SERIAL NOT NULL,
	url VARCHAR NOT NULL,
	title VARCHAR,
	description TEXT,
	country_code VARCHAR(2),
	category VARCHAR,
	is_library BOOLEAN DEFAULT FALSE,
	last_fetched TIMESTAMP WITHOUT TIME ZONE,
	is_active BOOLEAN DEFAULT TRUE,
	user_id INTEGER NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_feed_url_user UNIQUE (url, user_id),
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX IF NOT EXISTS ix_feeds_url ON feeds (url);
CREATE INDEX IF NOT EXISTS ix_feeds_user_id ON feeds (user_id);

CREATE TABLE IF NOT EXISTS prompt_templates (
	id SERIAL NOT NULL,
	user_id INTEGER,
	name VARCHAR NOT NULL,
	description TEXT,
	category VARCHAR,
	prompt_text TEXT NOT NULL,
	is_public BOOLEAN DEFAULT FALSE,
	is_active BOOLEAN DEFAULT TRUE,
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	variables JSON DEFAULT '[]'::JSON,
	output_format VARCHAR DEFAULT 'text',
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE INDEX IF NOT EXISTS ix_prompt_templates_name ON prompt_templates (name);

CREATE TABLE IF NOT EXISTS rules (
	id SERIAL NOT NULL,
	user_id INTEGER NOT NULL,
	name VARCHAR NOT NULL,
	description TEXT,
	rule_type VARCHAR NOT NULL,
	is_active BOOLEAN DEFAULT TRUE,
	priority INTEGER DEFAULT 0,
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	conditions JSON DEFAULT '[]'::JSON,
	actions JSON DEFAULT '[]'::JSON,
	settings JSON DEFAULT '{}'::JSON,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS scraper_destinations (
	id SERIAL NOT NULL,
	user_id INTEGER NOT NULL,
	name VARCHAR NOT NULL,
	description TEXT,
	source_type VARCHAR NOT NULL,
	source_url VARCHAR NOT NULL,
	is_active BOOLEAN DEFAULT TRUE,
	scrape_interval_minutes INTEGER DEFAULT 60,
	last_scraped_at TIMESTAMP WITHOUT TIME ZONE,
	ocr_enabled BOOLEAN DEFAULT FALSE,
	ocr_languages JSON DEFAULT '["eng"]'::JSON,
	ocr_preprocessing JSON DEFAULT '{}'::JSON,
	css_selectors JSON DEFAULT '{}'::JSON,
	xpath_rules JSON DEFAULT '{}'::JSON,
	clean_html BOOLEAN DEFAULT TRUE,
	extract_images BOOLEAN DEFAULT FALSE,
	extract_links BOOLEAN DEFAULT FALSE,
	auth_type VARCHAR,
	auth_credentials JSON DEFAULT '{}'::JSON,
	custom_headers JSON DEFAULT '{}'::JSON,
	run_nlp BOOLEAN DEFAULT TRUE,
	apply_rules BOOLEAN DEFAULT TRUE,
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS user_preferences (
	id SERIAL NOT NULL,
	user_id INTEGER NOT NULL,
	preferred_topics TEXT,
	excluded_topics TEXT,
	preferred_sources TEXT,
	excluded_sources TEXT,
	excluded_words TEXT,
	enable_recommendations BOOLEAN DEFAULT TRUE,
	min_relevance_score FLOAT DEFAULT 0.5,
	PRIMARY KEY (id),
	UNIQUE (user_id),
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS articles (
	id SERIAL NOT NULL,
	feed_id INTEGER NOT NULL,
	title VARCHAR NOT NULL,
	link VARCHAR NOT NULL,
	description TEXT,
	content TEXT,
	author VARCHAR,
	published_date TIMESTAMP WITHOUT TIME ZONE,
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	embedding TEXT,
	cluster_id INTEGER,
	sentiment_score FLOAT,
	topics TEXT,
	readability_score FLOAT,
	readability_label VARCHAR,
	writing_style VARCHAR,
	is_read BOOLEAN DEFAULT FALSE,
	is_bookmarked BOOLEAN DEFAULT FALSE,
	user_rating FLOAT,
	PRIMARY KEY (id),
	CONSTRAINT uq_article_link_feed UNIQUE (link, feed_id),
	FOREIGN KEY(feed_id) REFERENCES feeds (id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_articles_link ON articles (link);
CREATE INDEX IF NOT EXISTS ix_articles_feed_id ON articles (feed_id);

CREATE TABLE IF NOT EXISTS scraped_content (
	id SERIAL NOT NULL,
	destination_id INTEGER NOT NULL,
	title VARCHAR,
	content_text TEXT,
	content_html TEXT,
	extracted_images JSON DEFAULT '[]'::JSON,
	extracted_links JSON DEFAULT '[]'::JSON,
	ocr_text TEXT,
	ocr_confidence INTEGER,
	ocr_metadata JSON DEFAULT '{}'::JSON,
	source_url VARCHAR NOT NULL,
	scraped_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
	content_hash VARCHAR,
	processing_status VARCHAR DEFAULT 'pending',
	processing_errors JSON DEFAULT '[]'::JSON,
	PRIMARY KEY (id),
	FOREIGN KEY(destination_id) REFERENCES scraper_destinations (id)
);

CREATE TABLE IF NOT EXISTS article_metadata (
	id SERIAL NOT NULL,
	article_id INTEGER NOT NULL,
	entities JSON DEFAULT '{}'::JSON,
	keywords JSON DEFAULT '[]'::JSON,
	summary TEXT,
	main_content TEXT,
	custom_fields JSON DEFAULT '{}'::JSON,
	processed_at TIMESTAMP WITHOUT TIME ZONE,
	processing_status VARCHAR DEFAULT 'pending',
	processing_errors JSON DEFAULT '[]'::JSON,
	PRIMARY KEY (id),
	UNIQUE (article_id),
	FOREIGN KEY(article_id) REFERENCES articles (id)
);
