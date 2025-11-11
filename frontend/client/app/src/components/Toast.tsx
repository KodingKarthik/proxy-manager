import { useEffect } from 'react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface ToastProps {
  message: string;
  type?: ToastType;
  onClose: () => void;
  duration?: number;
}

export const Toast: React.FC<ToastProps> = ({
  message,
  type = 'info',
  onClose,
  duration = 5000,
}) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const typeStyles = {
    success: 'bg-green-500 bg-opacity-20 border-green-500 text-green-400',
    error: 'bg-neon-magenta bg-opacity-20 border-neon-magenta text-neon-magenta',
    info: 'bg-neon-cyan bg-opacity-20 border-neon-cyan text-neon-cyan',
    warning: 'bg-yellow-500 bg-opacity-20 border-yellow-500 text-yellow-400',
  };

  return (
    <div
      className={`fixed bottom-4 right-4 p-4 border rounded-lg shadow-lg ${typeStyles[type]} max-w-md z-50`}
      role="alert"
      aria-live="assertive"
    >
      <div className="flex items-center justify-between">
        <p className="text-sm">{message}</p>
        <button
          onClick={onClose}
          className="ml-4 text-current hover:opacity-75"
          aria-label="Close notification"
        >
          ×
        </button>
      </div>
    </div>
  );
};

