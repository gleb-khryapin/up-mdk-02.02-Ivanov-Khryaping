import { useState } from "react";
import type { Priority, TaskStatus, User } from "../api/types";

interface Props {
  status: TaskStatus;
  users: User[];
  isLead: boolean;
  currentUserId: number;
  onClose: () => void;
  onSubmit: (payload: Record<string, unknown>) => Promise<void>;
}

export default function TaskDialog({
  status,
  users,
  isLead,
  currentUserId,
  onClose,
  onSubmit,
}: Props) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<Priority>("medium");
  const [assigneeId, setAssigneeId] = useState<number | "">(isLead ? "" : currentUserId);
  const [branch, setBranch] = useState("");
  const [estimate, setEstimate] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (title.trim().length < 3) {
      setError("Название должно содержать не менее трёх символов");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim(),
        status,
        priority,
        assignee_id: assigneeId === "" ? null : Number(assigneeId),
        branch: branch.trim() || null,
        estimate_hours: estimate ? Number(estimate) : null,
      });
      onClose();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Не удалось создать задачу");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 px-4">
      <form onSubmit={handleSubmit} className="bg-white rounded-xl w-full max-w-md p-6 shadow-lg">
        <h3 className="text-lg font-semibold mb-4">Новая задача</h3>

        <label className="block text-sm text-slate-600 mb-1">Название</label>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          autoFocus
          className="w-full border border-slate-200 rounded-lg px-3 py-2 mb-3"
        />

        <label className="block text-sm text-slate-600 mb-1">Описание</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          className="w-full border border-slate-200 rounded-lg px-3 py-2 mb-3"
        />

        <div className="grid grid-cols-2 gap-3 mb-3">
          <div>
            <label className="block text-sm text-slate-600 mb-1">Приоритет</label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as Priority)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2"
            >
              <option value="low">низкий</option>
              <option value="medium">средний</option>
              <option value="high">высокий</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-600 mb-1">Оценка, часов</label>
            <input
              type="number"
              min={0}
              step={0.5}
              value={estimate}
              onChange={(e) => setEstimate(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2"
            />
          </div>
        </div>

        <label className="block text-sm text-slate-600 mb-1">Исполнитель</label>
        <select
          value={assigneeId}
          onChange={(e) => setAssigneeId(e.target.value === "" ? "" : Number(e.target.value))}
          disabled={!isLead}
          className="w-full border border-slate-200 rounded-lg px-3 py-2 mb-3 disabled:bg-slate-50"
        >
          <option value="">не назначен</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>
              {user.full_name}
            </option>
          ))}
        </select>
        {!isLead && (
          <p className="text-xs text-slate-400 -mt-2 mb-3">
            Назначать задачи другим участникам может только тимлид
          </p>
        )}

        <label className="block text-sm text-slate-600 mb-1">Ветка в Git</label>
        <input
          value={branch}
          onChange={(e) => setBranch(e.target.value)}
          placeholder="feature/task-name"
          className="w-full border border-slate-200 rounded-lg px-3 py-2 mb-4 font-mono text-sm"
        />

        {error && <p className="text-sm text-red-600 mb-3">{error}</p>}

        <div className="flex gap-2">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 py-2 rounded-lg bg-slate-100 text-slate-600 font-medium"
          >
            Отмена
          </button>
          <button
            type="submit"
            disabled={busy}
            className="flex-1 py-2 rounded-lg bg-accent text-white font-medium disabled:opacity-60"
          >
            {busy ? "Сохранение..." : "Создать"}
          </button>
        </div>
      </form>
    </div>
  );
}
