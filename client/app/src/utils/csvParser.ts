export interface CsvRow {
  [key: string]: unknown;
  ip: string;
  port: number;
  protocol?: string;
  username?: string;
  password?: string;
}

export interface CsvValidationError {
  [key: string]: unknown;
  row: number;
  field: string;
  message: string;
}

export interface ParsedCsvData {
  rows: CsvRow[];
  errors: CsvValidationError[];
}

export const parseCsv = (csvText: string): ParsedCsvData => {
  const lines = csvText.split('\n').filter((line) => line.trim());
  const rows: CsvRow[] = [];
  const errors: CsvValidationError[] = [];

  // Skip header row if present
  const startIndex = lines[0]?.toLowerCase().includes('ip') ? 1 : 0;

  for (let i = startIndex; i < lines.length; i++) {
    const line = lines[i];
    const columns = line.split(',').map((col) => col.trim().replace(/^"|"$/g, ''));

    if (columns.length < 2) {
      errors.push({
        row: i + 1,
        field: 'row',
        message: 'Row must have at least IP and Port columns',
      });
      continue;
    }

    const ip = columns[0];
    const port = parseInt(columns[1], 10);
    const protocol = columns[2] || 'http';
    const username = columns[3] || undefined;
    const password = columns[4] || undefined;

    // Validate IP
    if (!ip || !/^(\d{1,3}\.){3}\d{1,3}$/.test(ip)) {
      errors.push({
        row: i + 1,
        field: 'ip',
        message: 'Invalid IP address',
      });
    }

    // Validate port
    if (isNaN(port) || port < 1 || port > 65535) {
      errors.push({
        row: i + 1,
        field: 'port',
        message: 'Port must be a number between 1 and 65535',
      });
    }

    // Validate protocol
    if (protocol && !['http', 'https', 'socks5'].includes(protocol.toLowerCase())) {
      errors.push({
        row: i + 1,
        field: 'protocol',
        message: 'Protocol must be http, https, or socks5',
      });
    }

    if (errors.filter((e) => e.row === i + 1).length === 0) {
      rows.push({
        ip,
        port,
        protocol: protocol.toLowerCase(),
        username,
        password,
      });
    }
  }

  return { rows, errors };
};

export const csvTemplate = `ip,port,protocol,username,password
192.168.1.1,8080,http,user1,pass1
192.168.1.2,8080,https,user2,pass2`;

