export type Role = "lead" | "developer";
export type TaskStatus = "backlog" | "todo" | "in_progress" | "review" | "done";
export type Priority = "low" | "medium" | "high";

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: Role;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Task {
  id: number;
  board_id: number;
  title: string;
  description: string;
  status: TaskStatus;
  priority: Priority;
  position: number;
  author_id: number;
  assignee_id: number | null;
  branch: string | null;
  estimate_hours: number | null;
  created_at: string;
  updated_at: string;
  assignee: User | null;
}

export interface BoardColumn {
  status: TaskStatus;
  title: string;
  position: number;
  wip_limit: number | null;
}

export interface Board {
  id: number;
  title: string;
  description: string;
  owner_id: number;
}

export interface BoardDetail extends Board {
  columns: BoardColumn[];
  tasks: Task[];
}
