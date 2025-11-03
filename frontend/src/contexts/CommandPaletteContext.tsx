import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';

export interface CommandPaletteItem {
  id: string;
  title: string;
  subtitle?: string;
  group?: string;
  keywords?: string[];
  action: () => void;
  icon?: React.ReactNode;
}

interface CommandPaletteContextValue {
  registerCommands: (commands: CommandPaletteItem[]) => () => void;
  openPalette: (options?: { query?: string }) => void;
  closePalette: () => void;
  isOpen: boolean;
}

const CommandPaletteContext = createContext<CommandPaletteContextValue | undefined>(undefined);

interface CommandPaletteProviderProps {
  children: React.ReactNode;
}

export const CommandPaletteProvider: React.FC<CommandPaletteProviderProps> = ({ children }) => {
  const commandsRef = useRef<Map<string, CommandPaletteItem>>(new Map());
  const [version, setVersion] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const registerCommands = useCallback((commands: CommandPaletteItem[]) => {
    commands.forEach((command) => {
      commandsRef.current.set(command.id, command);
    });
    setVersion((v) => v + 1);

    return () => {
      commands.forEach((command) => {
        commandsRef.current.delete(command.id);
      });
      setVersion((v) => v + 1);
    };
  }, []);

  const openPalette = useCallback((options?: { query?: string }) => {
    if (options?.query) {
      setSearchQuery(options.query);
    }
    setIsOpen(true);
  }, []);

  const closePalette = useCallback(() => {
    setIsOpen(false);
    setSearchQuery('');
  }, []);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        setIsOpen(true);
      }

      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    if (isOpen) {
      const previousOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = previousOverflow;
      };
    }
    return;
  }, [isOpen]);

  const commandList = useMemo(() => {
    return Array.from(commandsRef.current.values());
  }, [version]);

  return (
    <CommandPaletteContext.Provider
      value={{
        registerCommands,
        openPalette,
        closePalette,
        isOpen,
      }}
    >
      {children}
      <CommandPaletteOverlay
        isOpen={isOpen}
        onClose={closePalette}
        commands={commandList}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />
    </CommandPaletteContext.Provider>
  );
};

export const useCommandPalette = () => {
  const context = useContext(CommandPaletteContext);
  if (!context) {
    throw new Error('useCommandPalette must be used within a CommandPaletteProvider');
  }
  return context;
};

interface CommandPaletteOverlayProps {
  isOpen: boolean;
  onClose: () => void;
  commands: CommandPaletteItem[];
  searchQuery: string;
  onSearchChange: (value: string) => void;
}

const CommandPaletteOverlay: React.FC<CommandPaletteOverlayProps> = ({
  isOpen,
  onClose,
  commands,
  searchQuery,
  onSearchChange,
}) => {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [activeIndex, setActiveIndex] = useState(0);

  const filteredCommands = useMemo(() => {
    const trimmedQuery = searchQuery.trim().toLowerCase();
    const allCommands = [...commands].sort((a, b) => a.title.localeCompare(b.title));

    if (!trimmedQuery) {
      return allCommands;
    }

    return allCommands.filter((command) => {
      const haystack = [
        command.title,
        command.subtitle,
        ...(command.keywords || []),
      ]
        .join(' ')
        .toLowerCase();

      return haystack.includes(trimmedQuery);
    });
  }, [commands, searchQuery]);

  const groupedCommands = useMemo(() => {
    return filteredCommands.reduce<Record<string, CommandPaletteItem[]>>((acc, command) => {
      const groupKey = command.group || 'General';
      if (!acc[groupKey]) {
        acc[groupKey] = [];
      }
      acc[groupKey].push(command);
      return acc;
    }, {});
  }, [filteredCommands]);

  useEffect(() => {
    if (isOpen) {
      setActiveIndex(0);
      requestAnimationFrame(() => inputRef.current?.focus());
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyNavigation = (event: KeyboardEvent) => {
      if (!isOpen) return;
      if (filteredCommands.length === 0) return;

      if (event.key === 'ArrowDown' || (event.key === 'Tab' && !event.shiftKey)) {
        event.preventDefault();
        setActiveIndex((prev) => (prev + 1) % Math.max(filteredCommands.length, 1));
      }

      if (event.key === 'ArrowUp' || (event.key === 'Tab' && event.shiftKey)) {
        event.preventDefault();
        setActiveIndex((prev) =>
          prev === 0 ? Math.max(filteredCommands.length - 1, 0) : prev - 1
        );
      }

      if (event.key === 'Enter') {
        event.preventDefault();
        const command = filteredCommands[activeIndex];
        if (command) {
          command.action();
          onClose();
        }
      }
    };

    window.addEventListener('keydown', handleKeyNavigation);
    return () => window.removeEventListener('keydown', handleKeyNavigation);
  }, [activeIndex, filteredCommands, isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-[999] flex items-start justify-center bg-black/60 backdrop-blur-sm px-4 pt-24"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onClose();
        }
      }}
    >
      <div className="w-full max-w-3xl rounded-xl bg-dark-primary border border-dark-border shadow-2xl">
        <div className="border-b border-dark-border">
          <input
            ref={inputRef}
            value={searchQuery}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder="Search anything..."
            className="w-full bg-transparent px-5 py-4 text-lg text-dark-700 placeholder-dark-500 focus:outline-none"
          />
        </div>

        <div className="max-h-[420px] overflow-y-auto">
          {filteredCommands.length === 0 && (
            <div className="px-5 py-6 text-dark-500 text-sm">
              No matches. Try a different keyword.
            </div>
          )}

          {Object.entries(groupedCommands).map(([group, items]) => (
            <div key={group}>
              <div className="px-5 pt-4 text-xs uppercase tracking-wide text-dark-500">
                {group}
              </div>
              <ul className="mt-2">
                {items.map((command, index) => {
                  const isActive = filteredCommands[activeIndex]?.id === command.id;
                  return (
                    <li
                      key={command.id}
                      className={`mx-2 mb-1 rounded-lg border border-transparent transition-colors ${
                        isActive
                          ? 'bg-primary-600/10 border-primary-500/20'
                          : 'hover:bg-dark-secondary/70'
                      }`}
                    >
                      <button
                        type="button"
                        onClick={() => {
                          command.action();
                          onClose();
                        }}
                        className="w-full flex items-center justify-between px-4 py-3 text-left"
                      >
                        <div className="flex items-center space-x-3">
                          {command.icon && (
                            <span className="text-dark-400">{command.icon}</span>
                          )}
                          <div>
                            <div className="text-sm font-medium text-dark-700">
                              {command.title}
                            </div>
                            {command.subtitle && (
                              <div className="text-xs text-dark-500">
                                {command.subtitle}
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="text-xs text-dark-500">
                          {command.keywords?.slice(0, 3).join(' • ')}
                        </div>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>

        <div className="flex items-center justify-between border-t border-dark-border px-4 py-3 text-xs text-dark-500">
          <div>Type to search feeds, topics, or actions</div>
          <div className="flex items-center space-x-3">
            <kbd className="rounded bg-dark-secondary px-2 py-1 font-mono text-[11px] text-dark-500">
              ⌘/Ctrl + K
            </kbd>
            <span>Close</span>
            <kbd className="rounded bg-dark-secondary px-2 py-1 font-mono text-[11px] text-dark-500">
              Esc
            </kbd>
          </div>
        </div>
      </div>
    </div>
  );
};
