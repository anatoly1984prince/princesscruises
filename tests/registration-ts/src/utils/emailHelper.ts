/**
 * Generates a unique email using current date + hour + minute.
 * Format: test<YYYYMMDDHHmm>@test.com
 */
export function generateDynamicEmail(): string {
  const now = new Date();
  const pad = (n: number): string => String(n).padStart(2, '0');

  const yyyy = now.getFullYear();
  const mm   = pad(now.getMonth() + 1);
  const dd   = pad(now.getDate());
  const hh   = pad(now.getHours());
  const min  = pad(now.getMinutes());

  return `test${yyyy}${mm}${dd}${hh}${min}@test.com`;
}

export function printRegistrationSummary(name: string, email: string, password: string): void {
  console.log('\n================================');
  console.log('NEW USER CREATED');
  console.log(`Name: ${name}`);
  console.log(`Email: ${email}`);
  console.log(`Password: ${password}`);
  console.log('================================\n');
}
