export enum UserRole {
  ADMIN = 'admin',
  CLIENT = 'client',
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  token?: string;
}

export interface Invitation {
  id: string;
  email: string;
  role: UserRole;
  token: string;
  created_at: string;
  expires_at?: string;
  is_used: boolean;
} 