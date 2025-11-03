import React, { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import type { Feed } from '../types';

interface EditFeedModalProps {
  feed: Feed;
  isOpen: boolean;
  onClose: () => void;
  onSave: (feedId: number, updates: {
    title?: string;
    description?: string;
    country_code?: string;
    is_active?: boolean;
  }) => void;
  isSaving?: boolean;
}

export const EditFeedModal: React.FC<EditFeedModalProps> = ({
  feed,
  isOpen,
  onClose,
  onSave,
  isSaving = false
}) => {
  const [title, setTitle] = useState(feed.title || '');
  const [description, setDescription] = useState(feed.description || '');
  const [countryCode, setCountryCode] = useState(feed.country_code || '');
  const [isActive, setIsActive] = useState(feed.is_active);

  // Reset form when feed changes
  useEffect(() => {
    setTitle(feed.title || '');
    setDescription(feed.description || '');
    setCountryCode(feed.country_code || '');
    setIsActive(feed.is_active);
  }, [feed]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(feed.id, {
      title: title.trim() || undefined,
      description: description.trim() || undefined,
      country_code: countryCode.trim() || undefined,
      is_active: isActive,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-2xl mx-4 bg-dark-primary border border-dark-border rounded-xl shadow-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-dark-primary border-b border-dark-border px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-dark-700">Edit Feed</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-dark-secondary rounded-lg transition-colors"
            aria-label="Close"
          >
            <XMarkIcon className="w-5 h-5 text-dark-600" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Feed URL (read-only) */}
          <div>
            <label className="block text-sm font-medium text-dark-600 mb-2">
              Feed URL
            </label>
            <input
              type="text"
              value={feed.url}
              disabled
              className="w-full bg-dark-tertiary border border-dark-border rounded-lg px-3 py-2 text-dark-500 cursor-not-allowed"
            />
            <p className="text-xs text-dark-500 mt-1">Feed URL cannot be changed</p>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-dark-600 mb-2">
              Custom Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Leave empty to use feed's default title"
              className="w-full bg-dark-secondary border border-dark-tertiary rounded-lg px-3 py-2 text-dark-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-dark-600 mb-2">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description for this feed"
              rows={3}
              className="w-full bg-dark-secondary border border-dark-tertiary rounded-lg px-3 py-2 text-dark-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          {/* Country Code */}
          <div>
            <label className="block text-sm font-medium text-dark-600 mb-2">
              Country Code (ISO 3166-1 alpha-2)
            </label>
            <input
              type="text"
              value={countryCode}
              onChange={(e) => setCountryCode(e.target.value.toUpperCase())}
              placeholder="e.g., FI, US, GB"
              maxLength={2}
              className="w-full bg-dark-secondary border border-dark-tertiary rounded-lg px-3 py-2 text-dark-700 font-mono focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <p className="text-xs text-dark-500 mt-1">
              2-letter country code (FI=Finland, US=United States, GB=United Kingdom, etc.)
            </p>
          </div>

          {/* Active Status */}
          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              id="is_active"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
              className="w-4 h-4 rounded border-dark-tertiary bg-dark-secondary text-primary-600 focus:ring-2 focus:ring-primary-500"
            />
            <label htmlFor="is_active" className="text-sm font-medium text-dark-600 cursor-pointer">
              Feed is active (will be included in automatic refresh)
            </label>
          </div>

          {/* Metadata */}
          <div className="pt-4 border-t border-dark-border">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-dark-500">Last Fetched:</span>
                <span className="ml-2 text-dark-700">
                  {feed.last_fetched
                    ? new Date(feed.last_fetched).toLocaleString()
                    : 'Never'}
                </span>
              </div>
              <div>
                <span className="text-dark-500">Feed ID:</span>
                <span className="ml-2 text-dark-700 font-mono">#{feed.id}</span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={isSaving}
              className="px-4 py-2 bg-dark-secondary hover:bg-dark-tertiary disabled:opacity-50 text-dark-700 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white rounded-lg transition-colors"
            >
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
