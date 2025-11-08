import React from 'react';

export interface TableColumn<T> {
  key: string;
  header: string;
  accessor?: (row: T) => React.ReactNode;
  sortable?: boolean;
}

export interface TableProps<T> {
  columns: TableColumn<T>[];
  data: T[];
  isLoading?: boolean;
  onRowClick?: (row: T) => void;
  emptyMessage?: string;
  className?: string;
}

export function Table<T extends Record<string, unknown>>({
  columns,
  data,
  isLoading = false,
  onRowClick,
  emptyMessage = 'No data available',
  className = '',
}: TableProps<T>) {
  if (isLoading) {
    return (
      <div className="animate-pulse">
        <div className="h-12 bg-panel rounded mb-2"></div>
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-10 bg-panel rounded mb-2"></div>
        ))}
      </div>
    );
  }

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table
        className="min-w-full divide-y divide-neon-cyan"
        role="table"
        aria-label="Data table"
      >
        <thead className="bg-panel">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-neon-cyan uppercase tracking-wider"
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-bg divide-y divide-neon-cyan">
          {data.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                className="px-6 py-4 whitespace-nowrap text-sm text-muted text-center"
              >
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                onClick={() => onRowClick?.(row)}
                className={onRowClick ? 'cursor-pointer hover:bg-panel transition-colors' : ''}
                role="row"
              >
                {columns.map((column) => (
                  <td
                    key={column.key}
                    className="px-6 py-4 whitespace-nowrap text-sm text-neon-cyan"
                  >
                    {column.accessor ? column.accessor(row) : (row[column.key] as React.ReactNode)}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

