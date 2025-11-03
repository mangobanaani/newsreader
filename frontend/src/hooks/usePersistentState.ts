import { useEffect, useRef, useState } from 'react';

const isBrowser = typeof window !== 'undefined';

export function usePersistentState<T>(key: string, defaultValue: T) {
  const [state, setState] = useState<T>(() => {
    if (!isBrowser) {
      return defaultValue;
    }
    try {
      const stored = window.localStorage.getItem(key);
      if (stored !== null) {
        return JSON.parse(stored) as T;
      }
    } catch (error) {
      console.warn(`Failed to read persistent state for key "${key}"`, error);
    }
    return defaultValue;
  });

  const keyRef = useRef(key);
  keyRef.current = key;

  useEffect(() => {
    if (!isBrowser) {
      return;
    }
    try {
      window.localStorage.setItem(keyRef.current, JSON.stringify(state));
    } catch (error) {
      console.warn(`Failed to persist state for key "${keyRef.current}"`, error);
    }
  }, [state]);

  return [state, setState] as const;
}
