import React, { useState, useMemo } from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

interface FeedSuggestion {
  name: string;
  url: string;
  category: string;
  country: string;
  description?: string;
}

interface Feed {
  id: number;
  url: string;
  title: string | null;
  description: string | null;
  is_active: boolean;
  last_fetched: string | null;
  country_code: string | null;
}

interface FeedLibraryProps {
  feeds?: Feed[]; // User's actual feeds from database
  onSelectFeed: (feed: FeedSuggestion) => void;
  activeFeedUrls?: string[]; // URLs of currently active feeds
  inactiveFeedUrls?: string[]; // URLs of inactive feeds
  onRemoveFeed?: (url: string) => void; // Callback to deactivate a feed
  onReactivate?: (url: string) => void; // Callback to reactivate an inactive feed
  onEdit?: (feed: Feed) => void; // Callback to edit a feed
  onRefresh?: (feedId: number) => void; // Callback to refresh a feed
  isAdding?: boolean; // Whether a feed is currently being added
  isRefreshing?: boolean; // Whether a feed is being refreshed
}

// Comprehensive feed library with Finland and international sources
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const FEED_LIBRARY: FeedSuggestion[] = [
  // Finland - News (Finnish)
  { name: 'Yle Uutiset - Tuoreimmat', url: 'https://yle.fi/rss/uutiset/tuoreimmat', category: 'News', country: 'FI', description: 'Latest Finnish news from Yle' },
  { name: 'Yle Uutiset - Pääuutiset', url: 'https://yle.fi/rss/uutiset/paauutiset', category: 'News', country: 'FI', description: 'Top headlines from Yle' },
  { name: 'Yle News - English', url: 'https://yle.fi/rss/news', category: 'News', country: 'FI', description: 'Yle News in English' },
  { name: 'Helsingin Sanomat - Suomi', url: 'https://www.hs.fi/rss/suomi.xml', category: 'News', country: 'FI', description: 'Domestic Finnish news' },
  { name: 'Helsingin Sanomat - Maailma', url: 'https://www.hs.fi/rss/maailma.xml', category: 'News', country: 'FI', description: 'International news' },
  { name: 'Helsingin Sanomat - Kaupunki', url: 'https://www.hs.fi/rss/kaupunki.xml', category: 'News', country: 'FI', description: 'Helsinki city news' },
  { name: 'Iltalehti Uutiset', url: 'https://www.iltalehti.fi/rss/uutiset.xml', category: 'News', country: 'FI', description: 'Iltalehti news feed' },
  { name: 'Ilta-Sanomat Kotimaa', url: 'https://www.is.fi/rss/kotimaa.xml', category: 'News', country: 'FI', description: 'Domestic news' },
  { name: 'Ilta-Sanomat Ulkomaat', url: 'https://www.is.fi/rss/ulkomaat.xml', category: 'News', country: 'FI', description: 'International news' },

  // Finland - Business & Economy
  { name: 'Helsingin Sanomat - Talous', url: 'https://www.hs.fi/rss/talous.xml', category: 'Business', country: 'FI', description: 'Finnish business news' },
  { name: 'Kauppalehti', url: 'https://www.kauppalehti.fi/rss/uusimmat', category: 'Business', country: 'FI', description: 'Finnish business daily' },
  { name: 'Taloussanomat', url: 'https://www.is.fi/rss/taloussanomat.xml', category: 'Business', country: 'FI', description: 'Finnish economy news' },

  // Finland - Technology
  { name: 'Helsingin Sanomat - Tiede', url: 'https://www.hs.fi/rss/tiede.xml', category: 'Tech', country: 'FI', description: 'Science and tech news' },
  { name: 'MikroBitti', url: 'https://www.mikrobitti.fi/rss/all', category: 'Tech', country: 'FI', description: 'Finnish tech magazine' },
  { name: 'Tivi - IT-uutiset', url: 'https://www.tivi.fi/rss/uusimmat', category: 'Tech', country: 'FI', description: 'IT news in Finnish' },

  // Finland - Sports
  { name: 'Yle Urheilu', url: 'https://yle.fi/rss/urheilu', category: 'Sports', country: 'FI', description: 'Finnish sports news' },
  { name: 'Helsingin Sanomat - Urheilu', url: 'https://www.hs.fi/rss/urheilu.xml', category: 'Sports', country: 'FI', description: 'HS Sports' },
  { name: 'Iltalehti Urheilu', url: 'https://www.iltalehti.fi/rss/urheilu.xml', category: 'Sports', country: 'FI', description: 'Sports from Iltalehti' },

  // Finland - Entertainment & Culture
  { name: 'Helsingin Sanomat - Kulttuuri', url: 'https://www.hs.fi/rss/kulttuuri.xml', category: 'Culture', country: 'FI', description: 'Finnish culture news' },
  { name: 'Helsingin Sanomat - Viihde', url: 'https://www.hs.fi/rss/viihde.xml', category: 'Entertainment', country: 'FI', description: 'Entertainment news' },
  { name: 'Iltalehti Viihde', url: 'https://www.iltalehti.fi/rss/viihde.xml', category: 'Entertainment', country: 'FI', description: 'Entertainment from IL' },

  // International - Tech News
  { name: 'Hacker News', url: 'https://hnrss.org/frontpage', category: 'Tech', country: 'US', description: 'Tech community news' },
  { name: 'TechCrunch', url: 'https://techcrunch.com/feed/', category: 'Tech', country: 'US', description: 'Startup & tech news' },
  { name: 'Ars Technica', url: 'https://feeds.arstechnica.com/arstechnica/index', category: 'Tech', country: 'US', description: 'Technology & culture' },
  { name: 'The Verge', url: 'https://www.theverge.com/rss/index.xml', category: 'Tech', country: 'US', description: 'Tech, science, art' },
  { name: 'Wired', url: 'https://www.wired.com/feed/rss', category: 'Tech', country: 'US', description: 'Technology & innovation' },
  { name: 'Engadget', url: 'https://www.engadget.com/rss.xml', category: 'Tech', country: 'US', description: 'Consumer electronics' },

  // International - World News
  { name: 'BBC News - World', url: 'https://feeds.bbci.co.uk/news/world/rss.xml', category: 'News', country: 'GB', description: 'World news from BBC' },
  { name: 'BBC News - Technology', url: 'https://feeds.bbci.co.uk/news/technology/rss.xml', category: 'Tech', country: 'GB', description: 'Tech news from BBC' },
  { name: 'The Guardian - World', url: 'https://www.theguardian.com/world/rss', category: 'News', country: 'GB', description: 'International news' },
  { name: 'Reuters - World News', url: 'https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best', category: 'News', country: 'US', description: 'Global news coverage' },
  { name: 'Al Jazeera English', url: 'https://www.aljazeera.com/xml/rss/all.xml', category: 'News', country: 'QA', description: 'International news' },

  // International - Business
  { name: 'Bloomberg Technology', url: 'https://feeds.bloomberg.com/technology/news.rss', category: 'Business', country: 'US', description: 'Business & tech news' },
  { name: 'Financial Times', url: 'https://www.ft.com/?format=rss', category: 'Business', country: 'GB', description: 'Global finance news' },

  // International - Science
  { name: 'Science Daily', url: 'https://www.sciencedaily.com/rss/all.xml', category: 'Science', country: 'US', description: 'Latest science news' },
  { name: 'Nature - Latest Research', url: 'https://www.nature.com/nature.rss', category: 'Science', country: 'GB', description: 'Scientific research' },
  { name: 'Scientific American', url: 'http://rss.sciam.com/ScientificAmerican-Global', category: 'Science', country: 'US', description: 'Science & technology' },

  // Social Media & Communities
  { name: 'Reddit - World News', url: 'https://www.reddit.com/r/worldnews/.rss', category: 'News', country: 'US', description: 'Community curated news' },
  { name: 'Reddit - Technology', url: 'https://www.reddit.com/r/technology/.rss', category: 'Tech', country: 'US', description: 'Tech discussions' },
  { name: 'Reddit - Science', url: 'https://www.reddit.com/r/science/.rss', category: 'Science', country: 'US', description: 'Science community' },
];

export const FeedLibrary: React.FC<FeedLibraryProps> = ({
  feeds = [],
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  onSelectFeed: _onSelectFeed,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  activeFeedUrls: _activeFeedUrls = [],
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  inactiveFeedUrls: _inactiveFeedUrls = [],
  onRemoveFeed,
  onReactivate,
  onEdit,
  onRefresh,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  isAdding: _isAdding = false,
  isRefreshing = false
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCountry, setSelectedCountry] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [availableCurrentPage, setAvailableCurrentPage] = useState(1);
  const availableItemsPerPage = 10;

  // Filter active and inactive feeds
  const activeFeeds = feeds?.filter(f => f.is_active) || [];
  const inactiveFeeds = useMemo(() => feeds?.filter(f => !f.is_active) || [], [feeds]);

  // Get unique countries and categories from inactive feeds
  const countries = useMemo(() => {
    const unique = [...new Set(inactiveFeeds.map(f => f.country_code).filter(Boolean))];
    return unique.sort();
  }, [inactiveFeeds]);

  const categories = useMemo(() => {
    const unique = [...new Set(inactiveFeeds.map(f => f.category).filter(Boolean))];
    return unique.sort();
  }, [inactiveFeeds]);

  // Filter inactive feeds based on search and filters
  const filteredInactiveFeeds = useMemo(() => {
    return inactiveFeeds.filter(feed => {
      const matchesSearch = searchTerm === '' ||
        feed.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        feed.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        feed.url.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesCountry = selectedCountry === 'all' || feed.country_code === selectedCountry;
      const matchesCategory = selectedCategory === 'all' || feed.category === selectedCategory;

      return matchesSearch && matchesCountry && matchesCategory;
    });
  }, [inactiveFeeds, searchTerm, selectedCountry, selectedCategory]);

  // Pagination for inactive feeds
  const totalPages = Math.ceil(filteredInactiveFeeds.length / availableItemsPerPage);
  const startIndex = (availableCurrentPage - 1) * availableItemsPerPage;
  const paginatedInactiveFeeds = filteredInactiveFeeds.slice(startIndex, startIndex + availableItemsPerPage);

  // Reset page when filters change
  React.useEffect(() => {
    setAvailableCurrentPage(1);
  }, [searchTerm, selectedCountry, selectedCategory]);

  // Format date helper
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Never';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      {/* My Feeds Section - Only Active Feeds */}
      {activeFeeds.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-semibold text-dark-700 mb-4">
            My Feeds ({activeFeeds.length})
          </h2>
          <div className="space-y-3">
            {activeFeeds.map((feed) => (
              <div
                key={feed.id}
                className={`p-4 rounded-lg border transition-colors ${
                  feed.is_active
                    ? 'bg-dark-secondary border-green-500/30'
                    : 'bg-dark-tertiary border-gray-500/30'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-dark-700">
                        {feed.title || 'Untitled Feed'}
                      </h3>
                      <span
                        className={`text-xs px-2 py-1 rounded ${
                          feed.is_active
                            ? 'bg-green-500/20 text-green-400 border border-green-500/50'
                            : 'bg-gray-500/20 text-gray-400 border border-gray-500/50'
                        }`}
                      >
                        {feed.is_active ? 'Active' : 'Inactive'}
                      </span>
                      {feed.country_code && (
                        <span className="text-xs px-2 py-1 rounded bg-blue-500/20 text-blue-400 border border-blue-500/50">
                          {feed.country_code}
                        </span>
                      )}
                    </div>
                    {feed.description && (
                      <p className="text-dark-600 text-sm mb-2">{feed.description}</p>
                    )}
                    <div className="flex items-center space-x-4 text-sm text-dark-500">
                      <span>Last updated: {formatDate(feed.last_fetched)}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    {onEdit && (
                      <button
                        onClick={() => onEdit(feed)}
                        className="px-3 py-1.5 text-sm bg-dark-tertiary hover:bg-dark-secondary text-dark-700 rounded-lg transition-colors"
                        title="Edit feed settings"
                      >
                        Edit
                      </button>
                    )}
                    {onRefresh && (
                      <button
                        onClick={() => onRefresh(feed.id)}
                        disabled={isRefreshing}
                        className="px-3 py-1.5 text-sm bg-primary-600/20 hover:bg-primary-600/30 text-primary-400 rounded-lg transition-colors disabled:opacity-50"
                        title="Refresh this feed"
                      >
                        {isRefreshing ? '...' : 'Refresh'}
                      </button>
                    )}
                    {feed.is_active ? (
                      onRemoveFeed && (
                        <button
                          onClick={() => onRemoveFeed(feed.url)}
                          className="px-3 py-1.5 text-sm bg-orange-500/20 hover:bg-orange-500/30 text-orange-400 rounded-lg transition-colors"
                          title="Deactivate this feed"
                        >
                          Deactivate
                        </button>
                      )
                    ) : (
                      onReactivate && (
                        <button
                          onClick={() => onReactivate(feed.url)}
                          className="px-3 py-1.5 text-sm bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg transition-colors"
                          title="Activate this feed"
                        >
                          Activate
                        </button>
                      )
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Available Feeds Section - Shows ALL inactive feeds from database */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-dark-700">
            Available Feeds ({filteredInactiveFeeds.length})
          </h2>
          <div className="text-sm text-dark-500">
            {filteredInactiveFeeds.length} {filteredInactiveFeeds.length === inactiveFeeds.length ? 'ready to activate' : `of ${inactiveFeeds.length} feeds`}
          </div>
        </div>

      {/* Search and Filters */}
      <div className="space-y-4 mb-6">
        {/* Search Bar */}
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-500" />
          <input
            type="text"
            placeholder="Search feeds by name, description, or URL..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-dark-secondary border border-dark-tertiary rounded-lg text-dark-700 placeholder-dark-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-3">
          {/* Country Filter */}
          <select
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
            className="px-4 py-2 bg-dark-secondary border border-dark-tertiary rounded-lg text-dark-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Countries ({inactiveFeeds.length})</option>
            {countries.map(country => (
              <option key={country} value={country}>{country}</option>
            ))}
          </select>

          {/* Category Filter */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 bg-dark-secondary border border-dark-tertiary rounded-lg text-dark-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Categories</option>
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>

          {/* Quick filters */}
          {countries.includes('FI') && (
            <button
              onClick={() => { setSelectedCountry('FI'); setSelectedCategory('all'); }}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedCountry === 'FI'
                  ? 'bg-primary-600 text-white'
                  : 'bg-dark-secondary text-dark-700 hover:bg-dark-tertiary'
              }`}
            >
              Finland
            </button>
          )}
          {categories.includes('Tech') && (
            <button
              onClick={() => { setSelectedCountry('all'); setSelectedCategory('Tech'); }}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedCategory === 'Tech'
                  ? 'bg-primary-600 text-white'
                  : 'bg-dark-secondary text-dark-700 hover:bg-dark-tertiary'
              }`}
            >
              Technology
            </button>
          )}
          {(searchTerm || selectedCountry !== 'all' || selectedCategory !== 'all') && (
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedCountry('all');
                setSelectedCategory('all');
              }}
              className="px-4 py-2 rounded-lg bg-dark-secondary text-dark-700 hover:bg-dark-tertiary transition-colors"
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Feed List - Display paginated inactive feeds from database */}
      <div className="space-y-3">
        {paginatedInactiveFeeds.map((feed) => (
          <div
            key={feed.id}
            className="p-4 rounded-lg border bg-dark-tertiary border-gray-500/30 transition-colors hover:border-gray-500/50"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h3 className="text-lg font-semibold text-dark-700">
                    {feed.title || 'Untitled Feed'}
                  </h3>
                  {feed.country_code && (
                    <span className="text-xs px-2 py-1 rounded bg-blue-500/20 text-blue-400 border border-blue-500/50">
                      {feed.country_code}
                    </span>
                  )}
                  {feed.category && (
                    <span className="text-xs px-2 py-1 rounded bg-primary-600/20 text-primary-400">
                      {feed.category}
                    </span>
                  )}
                </div>
                {feed.description && (
                  <p className="text-dark-600 text-sm mb-2">{feed.description}</p>
                )}
                <div className="text-xs text-dark-500 truncate">
                  {feed.url}
                </div>
              </div>
              <div className="flex items-center space-x-2 ml-4">
                {onReactivate && (
                  <button
                    onClick={() => onReactivate(feed.url)}
                    className="px-3 py-1.5 text-sm bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg transition-colors"
                    title="Activate this feed"
                  >
                    Activate
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-dark-tertiary">
          <div className="text-sm text-dark-500">
            Showing {startIndex + 1}-{Math.min(startIndex + availableItemsPerPage, filteredInactiveFeeds.length)} of {filteredInactiveFeeds.length}
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setAvailableCurrentPage(Math.max(1, availableCurrentPage - 1))}
              disabled={availableCurrentPage === 1}
              className="px-3 py-1.5 text-sm bg-dark-secondary hover:bg-dark-tertiary text-dark-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <div className="flex items-center space-x-1">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                // Show first page, last page, current page, and pages around current
                const showPage = page === 1 ||
                                page === totalPages ||
                                Math.abs(page - availableCurrentPage) <= 1;
                const showEllipsis = (page === 2 && availableCurrentPage > 3) ||
                                    (page === totalPages - 1 && availableCurrentPage < totalPages - 2);

                if (!showPage && !showEllipsis) return null;
                if (showEllipsis) {
                  return <span key={page} className="text-dark-500 px-2">...</span>;
                }

                return (
                  <button
                    key={page}
                    onClick={() => setAvailableCurrentPage(page)}
                    className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                      page === availableCurrentPage
                        ? 'bg-primary-600 text-white'
                        : 'bg-dark-secondary hover:bg-dark-tertiary text-dark-700'
                    }`}
                  >
                    {page}
                  </button>
                );
              })}
            </div>
            <button
              onClick={() => setAvailableCurrentPage(Math.min(totalPages, availableCurrentPage + 1))}
              disabled={availableCurrentPage === totalPages}
              className="px-3 py-1.5 text-sm bg-dark-secondary hover:bg-dark-tertiary text-dark-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Empty State */}
      {inactiveFeeds.length === 0 && (
        <div className="text-center py-8 text-dark-500">
          All feeds are active! Check the "My Feeds" section above.
        </div>
      )}
      {inactiveFeeds.length > 0 && filteredInactiveFeeds.length === 0 && (
        <div className="text-center py-8 text-dark-500">
          No feeds match your search criteria. Try adjusting your filters.
        </div>
      )}
      </div>
    </div>
  );
};
