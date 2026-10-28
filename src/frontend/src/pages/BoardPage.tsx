import { DndContext, PointerSensor, closestCorners, useSensor, useSensors } from "@dnd-kit/core";
import type { DragEndEvent } from "@dnd-kit/core";
import { useCallback, useEffect, useState } from "react";
import { authApi, boardApi } from "../api/client";
import BoardColumn from "../components/BoardColumn";
import TaskDialog from "../components/TaskDialog";
import { useAuth } from "../context/AuthContext";
import type { BoardDetail, Task, TaskStatus, User } from "../api/types";

export default function BoardPage() {
  const { user, logout } = useAuth();
  const [board, setBoard] = useState<BoardDetail | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [dialogStatus, setDialogStatus] = useState<TaskStatus | null>(null);
  const [notice, setNotice] = useState("");
  const [onlyMine, setOnlyMine] = useState(false);

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

  const load = useCallback(async () => {
    const boards = await boardApi.list();
    if (boards.length === 0) {
      const created = await boardApi.create("Доска команды", "Учебная практика УП.02");
      setBoard(await boardApi.detail(created.id));
      return;
    }
    setBoard(await boardApi.detail(boards[0].id));
  }, []);

  useEffect(() => {
    load().catch(() => setNotice("Не удалось загрузить доску"));
    authApi.users().then(setUsers).catch(() => undefined);
  }, [load]);

  function showNotice(text: string) {
    setNotice(text);
    window.setTimeout(() => setNotice(""), 4000);
  }

  async function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over || !board) return;

    const taskId = Number(active.id);
    const task = board.tasks.find((t) => t.id === taskId);
    if (!task) return;

    const overTask = board.tasks.find((t) => t.id === Number(over.id));
    const targetStatus = (overTask ? overTask.status : over.id) as TaskStatus;
    if (!targetStatus) return;

    const columnTasks = board.tasks
      .filter((t) => t.status === targetStatus && t.id !== taskId)
      .sort((a, b) => a.position - b.position);
    const position = overTask
      ? columnTasks.findIndex((t) => t.id === overTask.id)
      : columnTasks.length;

    const previous = board;
    setBoard({
      ...board,
      tasks: board.tasks.map((t) => (t.id === taskId ? { ...t, status: targetStatus } : t)),
    });

    try {
      await boardApi.moveTask(board.id, taskId, targetStatus, Math.max(0, position));
      setBoard(await boardApi.detail(board.id));
    } catch (err: any) {
      setBoard(previous);
      const detail = err?.response?.data?.detail;
      showNotice(typeof detail === "string" ? detail : "Не удалось переместить задачу");
    }
  }

  async function handleDelete(task: Task) {
    if (!board || !window.confirm(`Удалить задачу «${task.title}»?`)) return;
    try {
      await boardApi.deleteTask(board.id, task.id);
      setBoard(await boardApi.detail(board.id));
    } catch {
      showNotice("Удалять задачи может только тимлид");
    }
  }

  if (!board) {
    return <div className="min-h-screen grid place-items-center text-slate-400">Загрузка доски...</div>;
  }

  const visibleTasks = onlyMine
    ? board.tasks.filter((t) => t.assignee_id === user?.id)
    : board.tasks;

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between">
        <div>
          <h1 className="font-semibold">{board.title}</h1>
          <p className="text-xs text-slate-400">{board.description}</p>
        </div>

        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-slate-600">
            <input type="checkbox" checked={onlyMine} onChange={(e) => setOnlyMine(e.target.checked)} />
            только мои задачи
          </label>
          <div className="text-right">
            <p className="text-sm font-medium">{user?.full_name}</p>
            <p className="text-xs text-slate-400">
              {user?.role === "lead" ? "тимлид" : "разработчик"}
            </p>
          </div>
          <button onClick={logout} className="text-sm text-slate-500 hover:text-red-600">
            Выйти
          </button>
        </div>
      </header>

      {notice && (
        <div className="bg-amber-50 border-b border-amber-200 text-amber-800 text-sm px-6 py-2">
          {notice}
        </div>
      )}

      <DndContext sensors={sensors} collisionDetection={closestCorners} onDragEnd={handleDragEnd}>
        <main className="flex-1 overflow-x-auto p-6">
          <div className="flex gap-4 min-h-full">
            {board.columns.map((column) => (
              <BoardColumn
                key={column.status}
                column={column}
                tasks={visibleTasks
                  .filter((t) => t.status === column.status)
                  .sort((a, b) => a.position - b.position)}
                canDelete={user?.role === "lead"}
                onDelete={handleDelete}
                onAdd={(status) => setDialogStatus(status as TaskStatus)}
              />
            ))}
          </div>
        </main>
      </DndContext>

      {dialogStatus && user && (
        <TaskDialog
          status={dialogStatus}
          users={users}
          isLead={user.role === "lead"}
          currentUserId={user.id}
          onClose={() => setDialogStatus(null)}
          onSubmit={async (payload) => {
            await boardApi.createTask(board.id, payload as Partial<Task>);
            setBoard(await boardApi.detail(board.id));
          }}
        />
      )}
    </div>
  );
}
